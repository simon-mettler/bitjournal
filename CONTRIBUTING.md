# Contributing to bitjournal

Thanks for your interest in bitjournal. It is under active development and maintained by one person, so please read this page before you open an issue or a pull request.

## Feature requests are discussions

**Feature requests must be opened as [discussions](https://github.com/simon-mettler/bitjournal/discussions), not issues.** Issues are for bugs only, and feature requests opened as issues will be closed and moved.

## What is accepted

bitjournal is still building its base feature set, so the scope of contributions is limited for now:

| Contribution                      | Status                                                        |
| --------------------------------- | ------------------------------------------------------------- |
| Bug fixes                         | Welcome. Open an issue first unless the fix is trivial.       |
| Enhancements to existing features | Welcome. Open a discussion first if the change is not small.  |
| Documentation fixes               | Welcome. Docs live in the separate bitjournal-web repository. |
| New features                      | Not accepted for now. Pull requests will be closed.           |

If you are unsure which category your idea falls into, ask in a discussion before you write code.

## Use of AI

I use AI tools for development myself and have no problem with you doing the same. What matters is that I am talking to a human.

- You may use AI to help you write, understand or review code.
- You must understand every line you submit, test it yourself, and be able to explain and defend it in review.
- You must write the pull request description and your replies yourself, in your own words.
- Fully AI-generated or agent-driven contributions are not allowed. That includes pull requests, issues, discussions and comments opened or answered by an autonomous agent or bot with no human reading and owning them.

Contributions that look unreviewed or automated will be closed without further discussion.

## Reporting bugs

Search existing issues first, then open a bug report and fill in the template. Include your bitjournal version, how you run it (Docker or development setup), and steps to reproduce. Remove personal data from logs and screenshots before posting.

Report security problems privately as described in [SECURITY.md](SECURITY.md), never in a public issue.

## Development setup

The repository has two independent projects, `backend/` (Django and Django REST Framework) and `frontend/` (Vue 3 and Vite).

### Backend

Requires Python 3.14 and PostgreSQL. Copy `.env.example` to `.env` in the repository root and fill in the required values. Then, from `backend/`:

```bash
docker compose -f docker-compose.dev.yml up -d   # local PostgreSQL
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
python manage.py migrate
python manage.py runserver                       # http://localhost:8000
```

### Frontend

Requires Node.js 24. From `frontend/`:

```bash
npm ci
npm run dev                                      # http://localhost:5173
```

The dev server proxies `/api` to the backend on port 8000.

## Before you open a pull request

CI runs the same checks, and a pull request cannot be merged until they pass.

```bash
# backend/
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test

# frontend/
npm run check        # type-check, lint, format check, unit tests
npm run build-only
```

- Run `npm run fix` in `frontend/` to apply lint and formatting fixes.
- Include tests for the behavior you change where it is practical.
- Commit migrations if you change models. Never edit existing migrations.
- If your change affects the UI, add before and after screenshots to the pull request.
- If your change affects a setting, environment variable, or deploy step, say so in the pull request so the docs can be updated.

## Pull requests

- Branch from `main` and use a prefix such as `fix/`, `feat/` or `chore/`.
- Keep each pull request small and focused on one thing. Unrelated changes will be asked to be split out.
- Use a clear title in the style of the existing history, for example `fix: update docker repository in compose.yml`.
- Link the issue or discussion your change relates to.
- Expect review feedback. Reviews are best effort, so please be patient.

## License

bitjournal is licensed under the [GNU General Public License v3.0](LICENSE). By submitting a contribution you agree that it is licensed under the same terms.

## Code of conduct

Be respectful. This project follows the [Code of Conduct](CODE_OF_CONDUCT.md).
