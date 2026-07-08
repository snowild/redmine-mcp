# Issue File Upload Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add file upload capability to redmine-mcp: a new `attach_files_to_issue` MCP tool and a `file_paths` parameter on `create_new_issue`.

**Architecture:** Redmine uploads are two-step: `POST /uploads.json` with raw bytes returns a token; the token is then referenced in `uploads: [{token, filename, content_type}]` inside an issue create/update payload. The client layer gains `upload_file`/`upload_files` plus `uploads` support in `update_issue`/`create_issue`; the tool layer composes them.

**Tech Stack:** Python 3.12, FastMCP, requests, pytest. Run everything with `uv run`.

**Spec:** `docs/superpowers/specs/2026-07-08-issue-file-upload-design.md`

## Global Constraints

- No client-side file size limit — the Redmine server enforces its own limit (HTTP 422 is translated to a friendly message by existing `_make_request` error handling).
- Fail-fast: if any file fails to upload, nothing is attached / no issue is created.
- `add_issue_note` is NOT modified.
- All user-facing strings in English (matches current codebase convention).
- **Git rule (user preference, overrides per-task commit steps):** do NOT commit code automatically. Each task ends by running tests; commits happen only after the user has verified the result at the end. Commit messages must NOT contain AI attribution (no Co-Authored-By).

---

### Task 1: Client upload methods (`upload_file` / `upload_files`)

**Files:**
- Modify: `src/redmine_mcp/redmine_client.py` (add `import mimetypes` near the top imports; add methods after `download_attachment`, around line 880)
- Test: `tests/unit/test_redmine_client.py` (append to `TestRedmineClient` class)

**Interfaces:**
- Consumes: existing `self._make_request(method, endpoint, **kwargs)`, `RedmineAPIError`.
- Produces:
  - `upload_file(self, file_path: str) -> Dict[str, Any]` — returns `{'token': str, 'filename': str, 'content_type': str}`; raises `RedmineAPIError` on missing/unreadable file or missing token in response.
  - `upload_files(self, file_paths: List[str]) -> List[Dict[str, Any]]` — sequential uploads, propagates the first `RedmineAPIError` (fail-fast).

- [ ] **Step 1: Write the failing tests**

Append to `TestRedmineClient` in `tests/unit/test_redmine_client.py`:

```python
    @patch('requests.Session.request')
    def test_upload_file_success(self, mock_request, tmp_path):
        """Test successful file upload returns token dict"""
        test_file = tmp_path / "report.txt"
        test_file.write_bytes(b"hello redmine")

        mock_response = Mock()
        mock_response.json.return_value = {'upload': {'token': '123.abc456'}}
        mock_response.content = b'{"upload": {"token": "123.abc456"}}'
        mock_request.return_value = mock_response

        result = self.client.upload_file(str(test_file))

        assert result == {
            'token': '123.abc456',
            'filename': 'report.txt',
            'content_type': 'text/plain',
        }
        args, kwargs = mock_request.call_args
        assert args[0] == 'POST'
        assert args[1].endswith('/uploads.json')
        assert kwargs['params'] == {'filename': 'report.txt'}
        assert kwargs['data'] == b"hello redmine"
        assert kwargs['headers'] == {'Content-Type': 'application/octet-stream'}

    def test_upload_file_not_found(self):
        """Test upload of nonexistent path raises friendly error"""
        with pytest.raises(RedmineAPIError, match="does not exist"):
            self.client.upload_file('/no/such/file.txt')

    def test_upload_file_directory(self, tmp_path):
        """Test upload of a directory path raises friendly error"""
        with pytest.raises(RedmineAPIError, match="does not exist"):
            self.client.upload_file(str(tmp_path))

    @patch('requests.Session.request')
    def test_upload_file_unknown_mime_falls_back(self, mock_request, tmp_path):
        """Test unknown extension falls back to application/octet-stream"""
        test_file = tmp_path / "data.xyz123"
        test_file.write_bytes(b"\x00\x01")

        mock_response = Mock()
        mock_response.json.return_value = {'upload': {'token': '9.def'}}
        mock_response.content = b'{"upload": {"token": "9.def"}}'
        mock_request.return_value = mock_response

        result = self.client.upload_file(str(test_file))

        assert result['content_type'] == 'application/octet-stream'

    @patch('requests.Session.request')
    def test_upload_file_no_token_in_response(self, mock_request, tmp_path):
        """Test missing token in response raises error"""
        test_file = tmp_path / "a.txt"
        test_file.write_bytes(b"x")

        mock_response = Mock()
        mock_response.json.return_value = {}
        mock_response.content = b'{}'
        mock_request.return_value = mock_response

        with pytest.raises(RedmineAPIError, match="no upload token"):
            self.client.upload_file(str(test_file))

    @patch('requests.Session.request')
    def test_upload_files_multiple(self, mock_request, tmp_path):
        """Test multi-file upload returns uploads array in order"""
        file_a = tmp_path / "a.txt"
        file_a.write_bytes(b"a")
        file_b = tmp_path / "b.png"
        file_b.write_bytes(b"b")

        responses = []
        for token in ('1.aaa', '2.bbb'):
            mock_response = Mock()
            mock_response.json.return_value = {'upload': {'token': token}}
            mock_response.content = b'{"upload": {}}'
            responses.append(mock_response)
        mock_request.side_effect = responses

        result = self.client.upload_files([str(file_a), str(file_b)])

        assert [u['token'] for u in result] == ['1.aaa', '2.bbb']
        assert [u['filename'] for u in result] == ['a.txt', 'b.png']

    def test_upload_files_fail_fast(self, tmp_path):
        """Test upload_files aborts on first missing file"""
        with pytest.raises(RedmineAPIError, match="does not exist"):
            self.client.upload_files([str(tmp_path / "missing.txt")])
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run python -m pytest tests/unit/test_redmine_client.py -k upload -v`
Expected: 7 tests FAIL with `AttributeError: 'RedmineClient' object has no attribute 'upload_file'` (and `upload_files`)

- [ ] **Step 3: Write the implementation**

In `src/redmine_mcp/redmine_client.py`, add to the imports block at the top (after `import json`):

```python
import mimetypes
```

Then add these methods to `RedmineClient`, directly after `download_attachment` (which ends around line 880):

```python
    def upload_file(self, file_path: str) -> Dict[str, Any]:
        """
        Upload a local file to Redmine (POST /uploads.json)

        Args:
            file_path: Local file path

        Returns:
            Upload descriptor: {'token', 'filename', 'content_type'}
        """
        path = Path(file_path)
        if not path.is_file():
            raise RedmineAPIError(f"File does not exist or is not a file: {file_path}")

        try:
            file_content = path.read_bytes()
        except OSError as e:
            raise RedmineAPIError(f"Failed to read file {file_path}: {e}")

        content_type = mimetypes.guess_type(path.name)[0] or 'application/octet-stream'

        response = self._make_request(
            'POST', '/uploads.json',
            params={'filename': path.name},
            data=file_content,
            headers={'Content-Type': 'application/octet-stream'}
        )

        token = response.get('upload', {}).get('token')
        if not token:
            raise RedmineAPIError(f"Upload failed: no upload token returned for {path.name}")

        return {
            'token': token,
            'filename': path.name,
            'content_type': content_type,
        }

    def upload_files(self, file_paths: List[str]) -> List[Dict[str, Any]]:
        """
        Upload multiple local files sequentially (fail-fast)

        Args:
            file_paths: List of local file paths

        Returns:
            List of upload descriptors suitable for an issue 'uploads' payload
        """
        return [self.upload_file(file_path) for file_path in file_paths]
```

Note: `Path` is already imported in this file (`from pathlib import Path`).

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run python -m pytest tests/unit/test_redmine_client.py -k upload -v`
Expected: 7 PASS

- [ ] **Step 5: Checkpoint (no commit — see Global Constraints)**

Run: `uv run python -m pytest tests/unit/ -q`
Expected: all pass, no regressions

---

### Task 2: Client `uploads` payload support in `update_issue` / `create_issue` (+ `private_notes` fix)

**Files:**
- Modify: `src/redmine_mcp/redmine_client.py:249-331` (`create_issue`, `update_issue`)
- Test: `tests/unit/test_redmine_client.py` (append to `TestRedmineClient` class)

**Interfaces:**
- Consumes: nothing from Task 1 (independent payload plumbing).
- Produces:
  - `update_issue(issue_id, **kwargs)` additionally honors `uploads: List[Dict]` and `private_notes: bool` kwargs (both placed into the `issue` payload).
  - `create_issue(..., uploads: Optional[List[Dict]] = None)` — appends `uploads` to the issue payload after validation.

**Background:** `update_issue` currently ignores unknown kwargs. `add_issue_note` (server.py:829) already passes `private_notes=True`, which is silently dropped today — a pre-existing bug that this task fixes because `attach_files_to_issue` needs the same kwarg.

- [ ] **Step 1: Write the failing tests**

Append to `TestRedmineClient` in `tests/unit/test_redmine_client.py`:

```python
    @patch('requests.Session.request')
    def test_update_issue_with_uploads(self, mock_request):
        """Test update_issue includes uploads and private_notes in payload"""
        mock_response = Mock()
        mock_response.json.return_value = {}
        mock_response.content = b''
        mock_request.return_value = mock_response

        uploads = [{'token': '1.aaa', 'filename': 'a.txt', 'content_type': 'text/plain'}]
        result = self.client.update_issue(
            123, notes='see attachment', uploads=uploads, private_notes=True
        )

        assert result is True
        args, kwargs = mock_request.call_args
        assert kwargs['json']['issue']['uploads'] == uploads
        assert kwargs['json']['issue']['private_notes'] is True
        assert kwargs['json']['issue']['notes'] == 'see attachment'

    @patch('requests.Session.request')
    def test_create_issue_with_uploads(self, mock_request):
        """Test create_issue includes uploads in payload"""
        mock_response = Mock()
        mock_response.json.return_value = {'issue': {'id': 456}}
        mock_response.content = b'{"issue": {"id": 456}}'
        mock_request.return_value = mock_response

        uploads = [{'token': '1.aaa', 'filename': 'a.txt', 'content_type': 'text/plain'}]
        issue_id = self.client.create_issue(
            project_id=1, subject='With attachment', uploads=uploads
        )

        assert issue_id == 456
        args, kwargs = mock_request.call_args
        assert kwargs['json']['issue']['uploads'] == uploads
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run python -m pytest tests/unit/test_redmine_client.py -k "with_uploads" -v`
Expected: 2 FAIL — `test_update_issue_with_uploads` with `KeyError: 'uploads'`; `test_create_issue_with_uploads` with `TypeError: ... unexpected keyword argument 'uploads'`

- [ ] **Step 3: Write the implementation**

In `update_issue` (`redmine_client.py`), after the `custom_fields` block (line 324-325) and before the empty-payload check, add:

```python
        if 'private_notes' in kwargs:
            update_data['issue']['private_notes'] = kwargs['private_notes']
        if 'uploads' in kwargs:
            update_data['issue']['uploads'] = kwargs['uploads']
```

In `create_issue`, add the parameter to the signature (after `category_id`):

```python
    def create_issue(self, project_id: int, subject: str, description: str = "",
                    tracker_id: Optional[int] = None, status_id: Optional[int] = None,
                    priority_id: Optional[int] = None, assigned_to_id: Optional[int] = None,
                    parent_issue_id: Optional[int] = None, custom_fields: Optional[List[Dict]] = None,
                    start_date: Optional[str] = None, due_date: Optional[str] = None,
                    estimated_hours: Optional[float] = None,
                    category_id: Optional[int] = None,
                    uploads: Optional[List[Dict]] = None) -> int:
```

Do NOT add `uploads` to `validation_data` (the validator only knows issue fields). Instead, after `issue_data = {'issue': validated_data}` (line 280), add:

```python
        if uploads:
            issue_data['issue']['uploads'] = uploads
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run python -m pytest tests/unit/test_redmine_client.py -k "with_uploads" -v`
Expected: 2 PASS

- [ ] **Step 5: Checkpoint (no commit — see Global Constraints)**

Run: `uv run python -m pytest tests/ -q`
Expected: all pass (existing `add_issue_note` tests must still pass with the `private_notes` fix)

---

### Task 3: MCP tool `attach_files_to_issue`

**Files:**
- Modify: `src/redmine_mcp/server.py` (imports at top; new tool after `get_attachment_info`, around line 2626)
- Test: `tests/integration/test_advanced_mcp_tools.py` (new test class at end of file)

**Interfaces:**
- Consumes: `client.upload_files(file_paths) -> List[Dict]` (Task 1), `client.update_issue(issue_id, uploads=..., notes=..., private_notes=...)` (Task 2), `client.get_issue(issue_id) -> RedmineIssue` (existing).
- Produces: MCP tool `attach_files_to_issue(issue_id: int, file_paths: List[str], notes: str = "", private: bool = False) -> str`.

- [ ] **Step 1: Write the failing tests**

Append to `tests/integration/test_advanced_mcp_tools.py`. Add `attach_files_to_issue` to the existing `from redmine_mcp.server import (...)` import at the top of the file, then add:

```python
class TestAttachFilesToIssue:
    """attach_files_to_issue tool tests"""

    def setup_method(self):
        """Setup before each test"""
        with patch.dict(os.environ, {
            'REDMINE_DOMAIN': 'https://test.redmine.com',
            'REDMINE_API_KEY': 'test_api_key'
        }, clear=True), patch('redmine_mcp.config.load_dotenv'):
            pass

    @patch('redmine_mcp.server.get_client')
    def test_attach_files_success(self, mock_get_client, tmp_path):
        """Test attaching files without a note"""
        test_file = tmp_path / "log.txt"
        test_file.write_bytes(b"some log content")

        mock_client = Mock()
        mock_client.upload_files.return_value = [
            {'token': '1.aaa', 'filename': 'log.txt', 'content_type': 'text/plain'}
        ]
        mock_issue = Mock()
        mock_issue.subject = 'Test Issue'
        mock_client.get_issue.return_value = mock_issue
        mock_get_client.return_value = mock_client

        result = attach_files_to_issue(123, [str(test_file)])

        assert "Files attached successfully" in result
        assert "log.txt" in result
        mock_client.upload_files.assert_called_once_with([str(test_file)])
        mock_client.update_issue.assert_called_once_with(
            123,
            uploads=[{'token': '1.aaa', 'filename': 'log.txt', 'content_type': 'text/plain'}]
        )

    @patch('redmine_mcp.server.get_client')
    def test_attach_files_with_private_note(self, mock_get_client, tmp_path):
        """Test attaching files together with a private note"""
        test_file = tmp_path / "screenshot.png"
        test_file.write_bytes(b"\x89PNG fake")

        uploads = [{'token': '2.bbb', 'filename': 'screenshot.png', 'content_type': 'image/png'}]
        mock_client = Mock()
        mock_client.upload_files.return_value = uploads
        mock_issue = Mock()
        mock_issue.subject = 'Test Issue'
        mock_client.get_issue.return_value = mock_issue
        mock_get_client.return_value = mock_client

        result = attach_files_to_issue(123, [str(test_file)], notes="see screenshot", private=True)

        assert "Files attached successfully" in result
        assert "see screenshot" in result
        assert "private" in result
        mock_client.update_issue.assert_called_once_with(
            123, uploads=uploads, notes="see screenshot", private_notes=True
        )

    @patch('redmine_mcp.server.get_client')
    def test_attach_files_empty_list(self, mock_get_client):
        """Test empty file_paths is rejected"""
        result = attach_files_to_issue(123, [])

        assert "Error" in result
        mock_get_client.return_value.update_issue.assert_not_called()

    @patch('redmine_mcp.server.get_client')
    def test_attach_files_upload_failure_aborts(self, mock_get_client):
        """Test upload failure aborts without touching the issue"""
        mock_client = Mock()
        mock_client.upload_files.side_effect = RedmineAPIError(
            "File does not exist or is not a file: /no/such.txt"
        )
        mock_get_client.return_value = mock_client

        result = attach_files_to_issue(123, ['/no/such.txt'])

        assert "Failed to attach files" in result
        assert "/no/such.txt" in result
        mock_client.update_issue.assert_not_called()
```

Also add `RedmineAPIError` to the existing `from redmine_mcp.redmine_client import ...` import in that file if not already imported.

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run python -m pytest tests/integration/test_advanced_mcp_tools.py::TestAttachFilesToIssue -v`
Expected: ImportError — `cannot import name 'attach_files_to_issue'`

- [ ] **Step 3: Write the implementation**

In `src/redmine_mcp/server.py`, update the typing import (line 8):

```python
from typing import Any, List
```

and add below it (after `from datetime import datetime`):

```python
from pathlib import Path
```

Add the tool after `get_attachment_info` (before `def main():`, around line 2626):

```python
@mcp.tool()
def attach_files_to_issue(issue_id: int, file_paths: List[str],
                          notes: str = "", private: bool = False) -> str:
    """
    Upload local files and attach them to an existing Redmine issue

    Uploads every file first; if any file fails to upload, nothing is
    attached to the issue.

    Args:
        issue_id: Issue ID
        file_paths: List of local file paths to upload
        notes: Optional note added together with the attachments
        private: Whether the note is private (only applies when notes is provided)

    Returns:
        Attach result message
    """
    try:
        if not file_paths:
            return "Error: file_paths cannot be empty"

        client = get_client()

        uploads = client.upload_files(file_paths)

        update_kwargs = {'uploads': uploads}
        if notes.strip():
            update_kwargs['notes'] = notes.strip()
            if private:
                update_kwargs['private_notes'] = True

        client.update_issue(issue_id, **update_kwargs)

        issue = client.get_issue(issue_id)

        file_lines = []
        for file_path in file_paths:
            path = Path(file_path)
            size_kb = path.stat().st_size / 1024
            file_lines.append(f"- {path.name} ({size_kb:.1f} KB)")

        result = f"""Files attached successfully!

Issue: #{issue_id} - {issue.subject}
Attached files ({len(file_paths)}):
""" + "\n".join(file_lines)

        if notes.strip():
            privacy_text = "private" if private else "public"
            result += f"\n\nNote ({privacy_text}):\n{notes.strip()}"

        return result

    except RedmineAPIError as e:
        return f"Failed to attach files: {str(e)}"
    except Exception as e:
        return f"System error: {str(e)}"
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run python -m pytest tests/integration/test_advanced_mcp_tools.py::TestAttachFilesToIssue -v`
Expected: 4 PASS

- [ ] **Step 5: Checkpoint (no commit — see Global Constraints)**

Run: `uv run python -m pytest tests/ -q`
Expected: all pass

---

### Task 4: `create_new_issue` gains `file_paths` parameter

**Files:**
- Modify: `src/redmine_mcp/server.py:937-1086` (`create_new_issue`)
- Test: `tests/integration/test_advanced_mcp_tools.py` (append to existing create tests class)

**Interfaces:**
- Consumes: `client.upload_files(file_paths)` (Task 1), `client.create_issue(..., uploads=...)` (Task 2).
- Produces: MCP tool parameter `create_new_issue(..., file_paths: List[str] = None) -> str`.

- [ ] **Step 1: Write the failing tests**

Append to the class containing `test_create_new_issue_success` in `tests/integration/test_advanced_mcp_tools.py`:

```python
    @patch('redmine_mcp.server.get_client')
    def test_create_new_issue_with_files(self, mock_get_client, tmp_path):
        """Test creating an issue with attachments"""
        test_file = tmp_path / "spec.pdf"
        test_file.write_bytes(b"%PDF fake")

        uploads = [{'token': '3.ccc', 'filename': 'spec.pdf',
                    'content_type': 'application/pdf'}]
        mock_client = Mock()
        mock_client.upload_files.return_value = uploads
        mock_client.create_issue.return_value = 456

        mock_issue = Mock()
        mock_issue.subject = 'Issue with attachment'
        mock_issue.project = {'name': 'Test Project'}
        mock_issue.tracker = {'name': 'Bug'}
        mock_issue.status = {'name': 'New'}
        mock_issue.priority = {'name': 'Normal'}
        mock_issue.assigned_to = None
        mock_client.get_issue.return_value = mock_issue
        mock_get_client.return_value = mock_client

        result = create_new_issue(1, "Issue with attachment",
                                  file_paths=[str(test_file)])

        assert "New issue created successfully" in result
        assert "spec.pdf" in result
        mock_client.upload_files.assert_called_once_with([str(test_file)])
        assert mock_client.create_issue.call_args.kwargs['uploads'] == uploads

    @patch('redmine_mcp.server.get_client')
    def test_create_new_issue_upload_failure_aborts(self, mock_get_client):
        """Test issue is not created when an upload fails"""
        mock_client = Mock()
        mock_client.upload_files.side_effect = RedmineAPIError(
            "File does not exist or is not a file: /no/such.txt"
        )
        mock_get_client.return_value = mock_client

        result = create_new_issue(1, "Doomed issue", file_paths=['/no/such.txt'])

        assert "Failed to create issue" in result
        mock_client.create_issue.assert_not_called()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run python -m pytest tests/integration/test_advanced_mcp_tools.py -k "with_files or upload_failure_aborts" -v`
Expected: `test_create_new_issue_with_files` FAILS with `TypeError: ... unexpected keyword argument 'file_paths'`; `test_create_new_issue_upload_failure_aborts` FAILS (create_issue was called / no failure message)

- [ ] **Step 3: Write the implementation**

In `create_new_issue` (`server.py`):

1. Add the parameter to the signature (after `category_name`):

```python
def create_new_issue(project_id: int, subject: str, description: str = "",
                    tracker_id: int = None, tracker_name: str = None,
                    priority_id: int = None, priority_name: str = None,
                    assigned_to_id: int = None, assigned_to_name: str = None, assigned_to_login: str = None,
                    parent_issue_id: int = None, start_date: str = None, due_date: str = None,
                    estimated_hours: float = None, status_id: int = None, status_name: str = None,
                    category_id: int = None, category_name: str = None,
                    file_paths: List[str] = None) -> str:
```

2. Add to the docstring Args section:

```
        file_paths: local file paths to upload as attachments (optional)
```

3. After the `estimated_hours` validation (line 1037-1038) and before `# Create an issue`, add:

```python
        # Upload attachments first (fail-fast: no issue is created on failure)
        uploads = None
        if file_paths:
            uploads = client.upload_files(file_paths)
```

4. Pass it to `client.create_issue(...)` (add after `category_id=final_category_id,`):

```python
            uploads=uploads,
```

5. After the `if description:` block at the end of the result formatting (line 1078-1079), add:

```python
        if file_paths:
            result += f"\n\nAttached files ({len(file_paths)}):\n" + "\n".join(
                f"- {Path(p).name}" for p in file_paths
            )
```

Note: upload failures raise `RedmineAPIError`, which the existing `except RedmineAPIError` handler formats as `Failed to create issue: ...` — satisfying the abort test.

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run python -m pytest tests/integration/test_advanced_mcp_tools.py -v`
Expected: all PASS (new tests plus existing create tests)

- [ ] **Step 5: Checkpoint (no commit — see Global Constraints)**

Run: `uv run python -m pytest tests/ -q`
Expected: all pass

---

### Task 5: Documentation updates

**Files:**
- Modify: `CLAUDE.md` (tool count and tool lists)
- Modify: `README.md` (tool list / feature docs)

**Interfaces:**
- Consumes: final tool signatures from Tasks 3–4.
- Produces: n/a (docs only).

- [ ] **Step 1: Update CLAUDE.md**

In the "Available MCP Tools" section: bump the count by 1 and add `attach_files_to_issue` to a new **Attachment Tools** entry (alongside `get_attachment_info`, `get_attachment_image`, `get_attachment_text`), and note the new `file_paths` parameter on `create_new_issue` in the Creation Tools line. Add a short usage section mirroring the existing feature sections:

````markdown
## File Upload Feature ✨

### Attach Files to an Existing Issue
```python
# Attach files only
attach_files_to_issue(issue_id=123, file_paths=["/path/to/log.txt"])

# Attach files with a note
attach_files_to_issue(issue_id=123, file_paths=["/path/a.png", "/path/b.pdf"],
                      notes="Attached screenshots", private=False)
```

### Create an Issue with Attachments
```python
create_new_issue(project_id=1, subject="Bug report",
                 file_paths=["/path/to/screenshot.png"])
```

### Behavior
- Multiple files per call are supported
- Fail-fast: if any file fails to upload, nothing is attached / no issue is created
- File size limits are enforced by the Redmine server (oversized files return a friendly error)
````

- [ ] **Step 2: Update README.md**

Locate the tool list in `README.md` (search for `get_attachment_info`) and add `attach_files_to_issue` with a one-line description ("Upload local files and attach them to an issue, with optional note"), and mention the `file_paths` parameter in the `create_new_issue` entry. Match the surrounding format exactly.

- [ ] **Step 3: Verify consistency**

Run: `grep -rn "attach_files_to_issue" CLAUDE.md README.md src/redmine_mcp/server.py | wc -l`
Expected: ≥ 3 (tool defined once in server.py, mentioned in both docs)

- [ ] **Step 4: Final verification (gate before any commit)**

Run: `uv run python -m pytest tests/ -q`
Expected: all pass. Then report results to the user and wait for their verification before committing anything (per Global Constraints).
