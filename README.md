# BigRedButton

Select a RUTUBE episode on a Linux computer and open it on an Android TV over
Ethernet using Android TV Remote Protocol v2. The main application does not
need root, USB, or ADB.

See [RUN.md](RUN.md) for installation, automatic updates, pairing, desktop
shortcut setup, and release instructions.

## Release model

Version tags build a wheel in GitHub Actions. Each GitHub Release contains the
wheel, a checksum, machine-readable release metadata, and the resilient
`run.sh` launcher. The launcher downloads updates atomically and falls back to
the last verified wheel when offline.

Pairing credentials are generated locally under
`~/BigRedButton/h96_credentials` and are ignored by Git.
