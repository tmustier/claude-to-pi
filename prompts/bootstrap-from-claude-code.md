---
description: Bootstrap Pi credentials from an existing Claude Code installation — no need to log in again
---

The user already has Claude Code installed and logged in. You're going to copy their Anthropic OAuth tokens from Claude Code into Pi so they don't need to log in again.

## How it works

Claude Code stores its Anthropic OAuth tokens in the macOS Keychain under the service name `Claude Code-credentials`. Pi stores its tokens in `~/.pi/agent/auth.json`. Both use the same Anthropic OAuth token format (`sk-ant-ort01-` for refresh, `sk-ant-oat01-` for access), so we can copy them across.

## Steps

### 1. Check Claude Code is installed and authenticated

Run this to check if Claude Code has stored credentials:

```bash
security find-generic-password -s "Claude Code-credentials" -w 2>/dev/null | python3 -c "
import sys, json
d = json.loads(sys.stdin.read())
oauth = d.get('claudeAiOauth', {})
if oauth.get('accessToken'):
    print('✓ Claude Code is authenticated')
    print(f'  Token prefix: {oauth[\"accessToken\"][:15]}...')
    sub = oauth.get('subscriptionType', 'unknown')
    print(f'  Subscription: {sub}')
else:
    print('✗ No Claude Code credentials found')
"
```

If no credentials found, tell the user to open Claude Code and log in first, then come back.

### 2. Extract tokens and write Pi auth.json

```bash
mkdir -p ~/.pi/agent

security find-generic-password -s "Claude Code-credentials" -w 2>/dev/null | python3 -c "
import sys, json, pathlib

# Read Claude Code tokens from keychain
cc = json.loads(sys.stdin.read())
oauth = cc['claudeAiOauth']

# Build Pi auth.json
auth = {
    'anthropic': {
        'type': 'oauth',
        'refresh': oauth['refreshToken'],
        'access': oauth['accessToken'],
        'expires': oauth['expiresAt']
    }
}

# Write (or merge with existing)
auth_path = pathlib.Path.home() / '.pi' / 'agent' / 'auth.json'
if auth_path.exists():
    existing = json.loads(auth_path.read_text())
    existing['anthropic'] = auth['anthropic']
    auth = existing

auth_path.write_text(json.dumps(auth, indent=2))
print('✓ Wrote Anthropic credentials to ~/.pi/agent/auth.json')
"
```

### 3. Verify it works

Tell the user: "Let's make sure Pi can talk to Claude. I'm going to do a quick test."

The fact that they're running this prompt inside Pi and getting a response means it worked. Confirm that to them.

### 4. OpenAI (optional)

Claude Code does NOT store OpenAI credentials — only Anthropic. If the user wants to use GPT-5.4 in Pi (one of the three models we set up), they'll need to log in to OpenAI separately:

Tell them: "You're now authenticated with Claude (Anthropic). If you also want access to GPT-5.4, run `/login` and connect your OpenAI/ChatGPT account. This is optional — you can use Pi with just Claude models."

### Notes
- The tokens are OAuth refresh tokens, so they'll auto-renew. The user doesn't need to re-do this.
- If Claude Code credentials expire or the user logs out of Claude Code, Pi keeps its own copy — they're independent after this point.
- This only works on macOS (Keychain-based credential storage).
