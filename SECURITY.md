# Security Policy

OpenPrototypes publishes AI-generated work live, so we take two risks especially seriously: **leaked secrets** and **prompt injection**.

## What to report

- A leaked secret (API key, token, password or personal data) in any commit, issue, log or note, in this repository or in any `op-*` project repository.
- Content designed to manipulate our agents (prompt injection) in issues, pull requests, notes or linked material.
- A vulnerability in a prototype, script or workflow.

## How to report

Do **not** open a public issue. Use one of these channels:

- Email **info@materiacore.com** with the subject `[SECURITY] OpenPrototypes`.
- Use GitHub's [private vulnerability reporting](https://github.com/MaterIA-Lab/OpenPrototypes/security/advisories/new) for the affected repository.

Please include the repository, the commit or file, and a short description. We aim to acknowledge reports within 72 hours.

## What we do

- Revoke and rotate any leaked credential immediately, then clean it from history where possible.
- Scan every push with [gitleaks](https://github.com/gitleaks/gitleaks).
- Run agents in a sandbox with a capped budget, and only let them push to `agent/*` branches.

## Scope note

Prototypes in `prototypes/agents/` are experimental research code. They are not hardened for production use.
