# Changelog

All notable changes to bitjournal are documented in this file.

## v0.1.5

### Updated

- Emails can now be sent via SMTP

## v0.1.4

### Updated

- PWA updates now happen automatically in the background
- Infos about the PWA install, version and service worker are now displayed under App > Settings

## v0.1.3

### Added

- Per-signal average weighting setting, used by the analytics charts when aggregating values.
- Clicking a signal in the journal opens its stats.
- Community files: `README.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md` and `SECURITY.md`.
- Basic `pytest` setup with a first test for the analytics services.

### Fixed

- Saving an event now shows a loading state ("Saving…") and disables to prevent duplicate events on slow connections.
- Minor styling fixes on the board track view and tabs.
