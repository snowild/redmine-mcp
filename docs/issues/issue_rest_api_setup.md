# Issue: Redmine REST API Setup Steps Supplement

## Problem Description

When setting up Redmine MCP, users could not find the API key option in "My Account". This is because Redmine does not enable the REST API functionality by default.

## Discovery Process

1. Log in to http://127.0.0.1:3000/ using admin/admin
2. Cannot find the API key option on the "My Account" page
3. Go to http://127.0.0.1:3000/settings?tab=api
4. Check "Enable REST web service (Web Service)"
5. After saving, the API key option can be found in "My Account"

## Solution

### 1. Update README.md
- Added "4.1 Enable REST API" step in Section 4
- Clearly stated that administrator permissions are required to enable this feature
- Strengthened relevant explanations in the troubleshooting section

### 2. Setup Steps
```
4.1 Enable REST API (requires administrator permissions)
1. Log in to the Redmine system as administrator
2. Go to Administration → Settings → API
3. Check "Enable REST web service (Web Service)"
4. Click the Save button

4.2 Get API Key
1. Log in to your Redmine system (can be administrator or regular user)
2. Go to My Account → API Access Key
3. Click Show or Reset to get the API key
4. Copy the key to REDMINE_API_KEY in the .env file
```

## Impact

- This is a prerequisite for all Redmine MCP users
- If REST API is not enabled, all MCP tools will fail
- Administrator permissions are required to enable this feature

## Status

✅ **Resolved** - README.md has been updated, includes complete setup steps and troubleshooting guide

## Related Files

- `/README.md` - Main documentation, includes setup steps
- `/docs/issues/issue_rest_api_setup.md` - This issue record

## Recommendations

Consider adding a check for whether REST API is enabled to the quick setup script (`quick_start.sh`) in the future, and provide corresponding setup guidance.
