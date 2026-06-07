# Safety

Jarvis v0.1A is read-only-first and local-first. Agents request actions, the runtime validates them, and blocked decisions are logged to `security.jsonl`.

## Hard Blocks

Jarvis blocks dangerous commands such as `git push`, `git merge`, `git reset --hard`, `rm -rf`, `del /s`, `format`, `diskpart`, `reg delete`, `Disable-WindowsDefender`, unrestricted execution policy changes, downloaded script execution, file deletion automation, secret reads, browser session access, email sending, public posting, and payments.

## Protected Files

Protected paths such as `.env`, `.pem`, `.key`, SSH keys, service account files, browser sessions, cookies, token caches, and password manager exports may be detected by name only. Their contents must not be read or printed.

## Exclusions

Jarvis v0.1A does not execute Codex, automate browsers, use paid AI APIs, access external accounts, or silently escalate permissions.

