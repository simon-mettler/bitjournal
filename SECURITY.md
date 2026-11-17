# Security Policy

## Reporting a vulnerability

Please do not report security vulnerabilities in public issues, discussions or pull requests.

Report them privately using one of these:

- **GitHub private vulnerability reporting**: go to the [Security tab](https://github.com/simon-mettler/bitjournal/security/advisories/new) of this repository and choose "Report a vulnerability".
- **Email**: [contact@simonmettler.com](mailto:contact@simonmettler.com)

Please include:

- A description of the issue and its impact.
- Steps to reproduce, or a proof of concept.
- The affected version and how you run bitjournal (Docker, development setup).
- Any suggested fix, if you have one.

Do not include real personal data or production credentials in your report.

## What to expect

bitjournal is maintained by one person, so responses are best effort:

- You will get an acknowledgement within about 2 days.
- I will confirm the issue, work on a fix, and keep you updated on progress.
- Once a fix is released, the issue is disclosed in the release notes and the [changelog](CHANGELOG.md). Credit is given if you want it.

## Supported versions

bitjournal is under active development. Only the latest release receives security fixes. Please update before reporting, to check the issue still exists.

## Scope

This policy covers the code in this repository. For problems with how a particular instance is set up or run, such as server hardening, TLS, or backups, see the [security guide](https://bitjournal.me/docs/selfhost/security) for self-hosters.
