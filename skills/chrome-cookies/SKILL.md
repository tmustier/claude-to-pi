---
name: chrome-cookies
description: Extract session cookies from Chrome on macOS by decrypting Chrome's cookie database. Use when you need to authenticate API calls using the user's existing browser session — e.g., refreshing expired session cookies, accessing a service the user is logged into, or bootstrapping API access for a tool that uses cookie auth.
---

# Chrome Cookie Extraction (macOS)

Extract and decrypt cookies from the user's Chrome browser on macOS. No browser automation, no debug ports, no passwords needed — reads the encrypted cookie SQLite DB directly using the Chrome Safe Storage key from macOS Keychain.

## When to use

- API returns 401 and the user says "I'm logged in" — refresh the session cookies
- Setting up programmatic access to a service where the user has a browser session
- Any cookie-based API that doesn't have proper OAuth/API keys

## How it works

Chrome stores cookies in a SQLite database (`~/Library/Application Support/Google/Chrome/<Profile>/Cookies`), encrypted with AES-128-CBC. The encryption key is derived from a password stored in macOS Keychain under "Chrome Safe Storage". This script reads both, decrypts, and outputs the plaintext cookie values.

## Requirements

- macOS (uses Keychain + Chrome's macOS cookie encryption)
- Python 3 with `cryptography` package (`pip install cryptography`)
- Chrome must have the cookies (user is logged in)
- Chrome does NOT need to be quit — reads the DB in read-only mode

## Usage

The helper script is at the skill directory: `extract.py` (resolve relative to this SKILL.md).

```bash
# Extract all cookies for a domain
python3 $SKILL_DIR/extract.py --domain app.example.com

# Extract specific cookies
python3 $SKILL_DIR/extract.py --domain app.example.com --names session_id auth_token

# Output as curl cookie header
python3 $SKILL_DIR/extract.py --domain github.com --curl

# Output as env vars
python3 $SKILL_DIR/extract.py --domain app.example.com --env

# Get a single cookie value (for scripting)
python3 $SKILL_DIR/extract.py --domain app.example.com --names session_id --value

# Specify Chrome profile (default: auto-detects which profile has the cookies)
python3 $SKILL_DIR/extract.py --domain app.example.com --profile "Profile 1"

# Include subdomains (.example.com matches app.example.com, api.example.com, etc.)
python3 $SKILL_DIR/extract.py --domain example.com --include-subdomains
```

## Programmatic use from Python

```python
from extract import extract_cookies

cookies = extract_cookies(domain="app.example.com", names=["session_id", "auth_token"])
# Returns: {"session_id": "abc...", "auth_token": "xyz..."}
```

## Known limitations

- **macOS only** — the Keychain integration and Chrome cookie encryption format are macOS-specific.
- **Chrome profiles** — the script auto-detects which profile has the cookies, but you can override with `--profile`.
- **v10 format** — handles Chrome's v10 (AES-128-CBC) encryption. If Chrome changes to a new format, the script will need updating.

## Why not agent-browser --auto-connect?

Chrome 145+ blocks `--remote-debugging-port` on the default profile for security. There is no way to connect agent-browser or any CDP tool to the user's live Chrome session with their cookies. This skill bypasses the browser entirely by reading the cookie database directly.
