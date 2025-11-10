## 2025-11-09

- Docs. Changed from Latex to Typst backend
- Docs. Converted from Python make script to Makefile
- Repo. Added GPL3 LICENSE
- Compose. Substitute variables using envsubst if available.
- Compose/Run. Changed create script to check for SUDO_UID/SUDO_GID first.
- Container. Updated transfer report export script to only save if there is a transfer.
- Container. Changed how APPNAME user gets created.
- Container. Added FTP login messages to log at start.
- Container. Deferred setting passwords until verifying FTP exists.
- Container. Added PYTHONUNBUFFERED env variable to Dockerfile.
- Container. Updated Dockerfile HUID and HGID to 0 instead of 1001.
- Container. Added GPL3 LICENSE LABEL to Dockerfile
