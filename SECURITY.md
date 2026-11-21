# Security

Report a vulnerability through GitHub's private vulnerability reporting on this repository (Security tab, "Report a vulnerability"). Please do not open a public issue.

modwright has no network code. `mw.py` reads a game install and its loader logs, copies files you name into a backup folder, and writes a Workshop VDF or Thunderstore manifest. It never uploads anything and never injects into a running game.
