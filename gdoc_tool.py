#!/usr/bin/env python3
"""
Google Docs CLI Tool - Full Read/Write Access

A simple CLI for creating, reading, and writing to Google Docs.
Uses OAuth credentials from ~/.gdoc/credentials.json (or $XDG_CONFIG_HOME/.gdoc/)

Dependencies:
    pip install google-auth google-api-python-client
"""

import json
import os
import sys
from pathlib import Path
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

XDG_CONFIG_HOME = os.environ.get("XDG_CONFIG_HOME", str(Path.home() / ".config"))
CREDS_FILE = Path(XDG_CONFIG_HOME) / ".gdoc" / "credentials.json"


def get_service():
    """Build and return the Google Docs service."""
    with open(CREDS_FILE) as f:
        creds_data = json.load(f)

    creds = Credentials(
        creds_data["refresh_token"],
        refresh_token=creds_data["refresh_token"],
        client_id=creds_data["client_id"],
        client_secret=creds_data["client_secret"],
        token_uri="https://oauth2.googleapis.com/token",
    )

    if not creds.valid:
        creds.refresh(Request())

    return build("docs", "v1", credentials=creds)


def create(title, content=""):
    """Create a new Google Doc with optional content."""
    service = get_service()
    doc = service.documents().create(body={"title": title}).execute()
    doc_id = doc.get("documentId")

    if content:
        end_idx = doc["body"]["content"][-1]["endIndex"]
        service.documents().batchUpdate(
            documentId=doc_id,
            body={
                "requests": [
                    {
                        "insertText": {
                            "location": {"index": end_idx - 1},
                            "text": content + "\n",
                        }
                    }
                ]
            },
        ).execute()

    return doc_id


def read(doc_id):
    """Read document content as plain text."""
    service = get_service()
    doc = service.documents().get(documentId=doc_id).execute()

    content = []
    for elem in doc.get("body", {}).get("content", []):
        if "paragraph" in elem:
            for para in elem["paragraph"].get("elements", []):
                if "textRun" in para:
                    content.append(para["textRun"].get("content", ""))

    return "".join(content).strip()


def write(doc_id, content, append=True):
    """Write/append content to a document."""
    service = get_service()
    doc = service.documents().get(documentId=doc_id).execute()
    end_idx = doc["body"]["content"][-1]["endIndex"]

    service.documents().batchUpdate(
        documentId=doc_id,
        body={
            "requests": [
                {
                    "insertText": {
                        "location": {"index": end_idx - 1},
                        "text": content + "\n",
                    }
                }
            ]
        },
    ).execute()

    return True


def main():
    if len(sys.argv) < 3:
        print("Usage: gdoc_tool.py <command> <args>")
        print("  create <title> [content]  (content can also be passed via stdin)")
        print("  read <doc_id>")
        print("  write <doc_id>            (content passed via stdin)")
        sys.exit(1)

    cmd = sys.argv[1]

    try:
        if cmd == "create":
            title = sys.argv[2]
            content = " ".join(sys.argv[3:]) if len(sys.argv) > 3 else ""
            if not content:
                content = sys.stdin.read().strip()
            doc_id = create(title, content)
            print(f"https://docs.google.com/document/d/{doc_id}/edit")

        elif cmd == "read":
            doc_id = sys.argv[2]
            print(read(doc_id))

        elif cmd == "write":
            doc_id = sys.argv[2]
            content = sys.stdin.read()
            write(doc_id, content)
            print("OK")

        else:
            print(f"Unknown command: {cmd}")
            sys.exit(1)

    except FileNotFoundError:
        print("Error: Credentials not found.")
        print(f"Expected: {CREDS_FILE}")
        print("Run setup_oauth.py to configure credentials.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
