# Google Docs CLI Tool

A simple command-line interface for reading and writing to Google Docs.

## Features

- **Create** new Google Docs with optional content
- **Read** document content as plain text
- **Write**/append content to existing documents

## Requirements

- Python 3.8+
- Google account

## Installation

```bash
pip install -r requirements.txt
```

## Setup

### 1. Create OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Click **CREATE CREDENTIALS** > **OAuth client ID**
3. Application type: **Desktop app**
4. Name: `Google Docs CLI`
5. Click **Create**
6. Click **Download JSON** and save as `client_secret.json` to your `Downloads` folder

### 2. Run Setup Script

```bash
python setup_oauth.py
```

This will:
- Open your browser for authentication
- Save credentials to `~/.config/.gdoc/credentials.json` (or `$XDG_CONFIG_HOME/.gdoc/`)

## Usage

```bash
# Create a new document with content
python gdoc_tool.py create "Meeting Notes" "Attendees: Alice, Bob"

# Create with content from stdin
echo "Content here" | python gdoc_tool.py create "Notes" -

# Read document content
python gdoc_tool.py read 1abc2def3xyz...

# Write to document (appends)
echo "Additional notes" | python gdoc_tool.py write 1abc2def3xyz...
```

## Credential Location

Credentials are stored at:
- Linux/macOS: `~/.config/.gdoc/credentials.json`
- Override with: `XDG_CONFIG_HOME` environment variable

## API Reference

| Command | Args | Description |
|---------|------|-------------|
| `create` | `<title> [content]` | Create a new doc, optionally with initial content |
| `read` | `<doc_id>` | Read document content as plain text |
| `write` | `<doc_id>` | Append content to existing doc (stdin) |

## License

MIT
