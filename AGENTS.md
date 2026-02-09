# AI Agent Instructions

This document provides guidance for AI agents using the Google Docs CLI Tool.

## Overview

The `gdoc_tool.py` script provides full read/write access to Google Docs via the API. It requires OAuth credentials configured via `setup_oauth.py`.

## For OpenClaw Agents

### Tool Integration

Use the `exec` tool to run `gdoc_tool.py`:

```bash
# Create a new document with content
gdoc_tool.py create "Meeting Notes" "Attendees: Alice, Bob"

# Read document content
gdoc_tool.py read <doc_id>

# Write/append to existing document
echo "Additional notes..." | gdoc_tool.py write <doc_id>
```

### Example Workflow

```
1. Research topic using web_fetch
2. Create doc: gdoc_tool.py create "Research: AI Trends" "<summary>"
3. Write findings: gdoc_tool.py write <doc_id> "<detailed notes>"
4. Read back for review: gdoc_tool.py read <doc_id>
```

## OpenClaw Skill Template

To integrate this tool as an OpenClaw skill, create a `SKILL.md` file:

```markdown
---
name: gdocs
description: Read and write to Google Docs. Create documents, read content, and append notes.
metadata:
  openclaw:
    emoji: "📄"
    requires: { "bins": ["python3"] }
    install:
      [
        {
          "id": "pip-deps",
          "kind": "pip",
          "packages": ["google-auth", "google-api-python-client"],
          "label": "Install Python dependencies",
        },
      ]
---

# Google Docs Skill

Use this skill when the user wants to:
- Create Google Docs
- Read document content
- Write/append notes to existing documents

## Setup Required

1. Run `python setup_oauth.py` to configure credentials
2. Requires `client_secret.json` from Google Cloud Console

## Commands

| Command | Usage | Description |
|---------|-------|-------------|
| create | `gdoc_tool.py create "Title" "Content"` | Create new doc |
| read | `gdoc_tool.py read <doc_id>` | Read doc content |
| write | `gdoc_tool.py write <doc_id> "Content"` | Append to doc |

## Example Usage

User: "Take meeting notes in a new doc"

Response: `gdoc_tool.py create "Meeting Notes" "Attendees:..."`
```

## Configuration

### Credential Path

- Default: `~/.config/.gdoc/credentials.json`
- Override: Set `XDG_CONFIG_HOME` environment variable

### Dependencies

```txt
google-auth>=2.0.0
google-api-python-client>=2.0.0
```

## Notes

- The `write` command appends content to the end of the document
- No true in-place editing - only append operations are supported
- Documents are created with edit URL output for easy access
