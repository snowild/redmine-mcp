# Design: File Upload to Redmine Issues

Date: 2026-07-08
Status: Approved

## Goal

Add file upload capability to the redmine-mcp server, covering three scenarios:

1. Attach files to an existing issue
2. Attach files while adding a note (same API call as scenario 1)
3. Attach files when creating a new issue

## Background: Redmine Upload API

Uploading is a two-step process:

1. `POST /uploads.json?filename=<name>` with the raw file bytes as body
   (`Content-Type: application/octet-stream`) → returns an upload `token`
2. Include `uploads: [{token, filename, content_type}]` in the issue create
   (`POST /issues.json`) or update (`PUT /issues/:id.json`) payload

Since `PUT /issues/:id` accepts both `uploads` and `notes` in one request,
scenarios 1 and 2 are covered by a single tool.

## Decisions

- **Multi-file support**: tools accept a list of file paths.
- **File size limit**: no client-side limit; rely on the Redmine server's
  attachment max size (HTTP 422), translated into a friendly error message.
- **Tool surface** (Approach A): one new tool `attach_files_to_issue` plus a
  `file_paths` parameter on `create_new_issue`. `add_issue_note` is left
  unchanged (already has 6 parameters; attaching with a note is handled by
  the new tool's optional `notes` parameter).

## Design

### 1. Client layer (`src/redmine_mcp/redmine_client.py`)

New methods:

```python
def upload_file(self, file_path: str) -> Dict[str, Any]:
    """Upload one file via POST /uploads.json.
    Returns {token, filename, content_type}."""

def upload_files(self, file_paths: List[str]) -> List[Dict[str, Any]]:
    """Upload multiple files sequentially, return the uploads array."""
```

- `upload_file` validates the path first (exists, is a file, readable) and
  raises `RedmineAPIError` with a friendly message otherwise.
- `content_type` is guessed with `mimetypes.guess_type()`, falling back to
  `application/octet-stream`.
- The upload request must override the session's default JSON `Content-Type`
  header with `application/octet-stream`.

Extended methods:

- `update_issue(**kwargs)`: support an `uploads` kwarg placed into the
  `issue` payload.
- `create_issue(...)`: new optional `uploads` parameter placed into the
  `issue` payload.

### 2. MCP tool layer (`src/redmine_mcp/server.py`)

New tool:

```python
@mcp.tool()
def attach_files_to_issue(issue_id: int, file_paths: List[str],
                          notes: str = "", private: bool = False) -> str
```

- Uploads every file first (fail-fast: if any file fails to upload, abort
  and attach nothing; the error message names the failing file).
- Then issues one `PUT /issues/:id` with `uploads` plus optional
  `notes` / `private_notes`.
- Output follows existing tool formatting: success message plus the list of
  attached files (name, size).

Extended tool:

```python
create_new_issue(..., file_paths: List[str] = None)
```

- When `file_paths` is given, upload first; if any upload fails, the issue
  is not created.

### 3. Error handling

- Nonexistent path / directory path → rejected before any request is sent.
- File exceeding the server limit (HTTP 422) → translated to a friendly
  "file exceeds server limit" style message.
- Network / auth errors → existing `RedmineAPIError` handling applies.

### 4. Testing

- Unit tests (`tests/unit/test_redmine_client.py`): `upload_file` with
  mocked requests (verify URL, Content-Type header, token parsing),
  nonexistent-file error, `upload_files` aggregation.
- Integration tests (`tests/integration/`): `attach_files_to_issue` and
  `create_new_issue` with attachments, mocking the client per the existing
  test patterns (env isolation with `clear=True` and `load_dotenv` mocking).

### 5. Documentation

- Update tool counts and tool lists in `CLAUDE.md` and `README.md`
  (new tool: `attach_files_to_issue`; new parameter on `create_new_issue`).
