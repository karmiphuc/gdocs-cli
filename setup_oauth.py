#!/usr/bin/env python3
"""
Google Docs OAuth Setup Helper

This script walks you through creating OAuth credentials and obtaining a refresh token.
Run this once to configure the gdoc_tool.py CLI.

Steps:
1. Download client_secret.json from Google Cloud Console
2. Run this script
3. Enter the verification code when prompted
"""

import json
import os
import sys
import webbrowser
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from pathlib import Path

XDG_CONFIG_HOME = os.environ.get("XDG_CONFIG_HOME", str(Path.home() / ".config"))
CREDS_DIR = Path(XDG_CONFIG_HOME) / ".gdoc"
CREDS_FILE = CREDS_DIR / "credentials.json"
DOWNLOADS = Path.home() / "Downloads"

SCOPES = ["https://www.googleapis.com/auth/documents"]
REDIRECT_URI = "http://localhost:8091/callback"


def find_client_secret():
    """Look for client_secret.json in common locations."""
    locations = [
        DOWNLOADS / "client_secret.json",
        Path.cwd() / "client_secret.json",
        Path.home() / "client_secret.json",
    ]

    for loc in locations:
        if loc.exists():
            return loc

    return None


def get_client_info():
    """Get client_id/client_secret from existing credentials or download."""
    client_file = find_client_secret()

    if client_file:
        print(f"Found: {client_file}")
        with open(client_file) as f:
            creds = json.load(f)
        return creds.get("installed", creds).get("client_id"), creds.get(
            "installed", creds
        ).get("client_secret")

    print("\n" + "=" * 60)
    print("Google Docs API Setup")
    print("=" * 60)
    print("\n1. Go to: https://console.cloud.google.com/apis/credentials")
    print("2. Click 'CREATE CREDENTIALS' > 'OAuth client ID'")
    print("3. Application type: 'Desktop app'")
    print("4. Name: 'Google Docs CLI'")
    print("5. Download the JSON file")
    print(f"\n6. Save it to: {DOWNLOADS}/client_secret.json")
    print("\nThen run this script again.")
    sys.exit(1)


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)

        if "code" in params:
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(
                b"<html><body><h1>Authentication successful!</h1><p>You can close this tab.</p></body></html>"
            )

            code = params["code"][0]
            exchange_code_for_token(code)


def exchange_code_for_token(code):
    """Exchange authorization code for refresh token."""
    client_id, client_secret = get_client_info()

    resp = requests.post(
        "https://oauth2.googleapis.com/token",
        data={
            "code": code,
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": REDIRECT_URI,
            "grant_type": "authorization_code",
        },
    )

    if resp.status_code == 200:
        tokens = resp.json()

        CREDS_DIR.mkdir(parents=True, exist_ok=True)

        final_creds = {
            "client_id": client_id,
            "client_secret": client_secret,
            "refresh_token": tokens["refresh_token"],
            "type": "authorized_user",
        }

        with open(CREDS_FILE, "w") as f:
            json.dump(final_creds, f, indent=2)

        print("\n" + "=" * 60)
        print("SUCCESS! Credentials saved.")
        print(f"Location: {CREDS_FILE}")
        print("=" * 60)
        print("\nYou can now use gdoc_tool.py:")
        print('  python gdoc_tool.py create "My Doc" "Hello World"')
        print("  python gdoc_tool.py read <doc_id>")
        print('  python gdoc_tool.py write <doc_id> "More content"')
    else:
        print(f"Error exchanging code: {resp.text}")
        sys.exit(1)


def main():
    client_id, _ = get_client_info()

    auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?client_id={client_id}&redirect_uri={REDIRECT_URI}&response_type=code&scope={'+'.join(SCOPES)}&access_type=offline"

    print("\nOpening browser for authentication...")
    print(f"(Or copy this URL manually: {auth_url})\n")

    webbrowser.open(auth_url)

    print(f"Waiting for authentication at {REDIRECT_URI}...")
    print("If the browser doesn't open, use the URL above.\n")

    server = HTTPServer(("localhost", 8091), Handler)
    server.handle_request()


if __name__ == "__main__":
    main()
