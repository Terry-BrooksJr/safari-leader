<div align="center">

# 🦁 Safari Leader

**A comprehensive childcare management platform for daycare centers and after-school programs.**

Enrollment · Attendance · Secure Student Handoff · Staff Scheduling · Parent Communication — all in one unified system.

[![CI Pipeline](https://github.com/Terry-BrooksJr/safari-leader/actions/workflows/commit_check.yaml/badge.svg)](https://github.com/Terry-BrooksJr/safari-leader/actions/workflows/commit_check.yaml)
[![codecov](https://codecov.io/gh/Terry-BrooksJr/safari-leader/branch/master/graph/badge.svg)](https://codecov.io/gh/Terry-BrooksJr/safari-leader)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Django 6.0](https://img.shields.io/badge/django-6.0-092E20.svg?logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](#-license)

</div>

---

## 📑 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Architecture](#-architecture)
- [Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Environment Variables](#environment-variables)
  - [Database Setup](#database-setup)
  - [Running the App](#running-the-app)
- [Task Reference](#-task-reference)
- [Testing](#-testing)
- [Code Quality](#-code-quality)
- [Deployment](#-deployment)
- [Security](#-security)
- [Project Structure](#-project-structure)
- [Contributing](#-contributing)
- [License](#-license)
- [Author](#-author)

---

## 🌍 Overview

**Safari Leader** is a Django-based operations platform purpose-built for the realities of running a
licensed childcare center. It replaces the patchwork of paper sign-in sheets, spreadsheets, and group
chats that most programs rely on with a single, auditable system of record.

The platform is designed to **reduce administrative overhead** and **surface real-time operational
visibility** — from who is in the building right now and which rooms are within ratio, to whether a
child has an active custody restriction at pickup time.

Key design principles:

- **Compliance-first** — field-level encryption for sensitive records, role-based access control, and an audit-friendly data model.
- **Operationally aware** — staff-to-child ratio tracking, room/program structure, and shift management baked into the domain model.
- **Family-facing** — guardians, authorized pickups, announcements, and direct messaging are first-class concepts.

---

## ✨ Features

Safari Leader is organized into focused Django apps, each owning a slice of the domain:

| Module | Responsibility |
| --- | --- |
| 👤 **Accounts** | Custom user model with role-based access control (Admin, Director, Instructor, Aide, Guardian, Authorized Pickup, Clerical) and scoped role assignments per child/room. |
| 🧒 **Children** | Child profiles, guardian relationships, emergency contacts, authorized-pickup profiles, allergies (with severity), medical notes, and **custody restrictions**. |
| 📋 **Enrollment** | Enrollment lifecycle/status tracking and per-child weekly schedules. |
| ✅ **Attendance** | Daily attendance records plus granular check-in / check-out events. |
| 🤝 **Handoff** | Secure student handoff workflow with multiple verification methods and a full event trail. |
| 💬 **Communication** | Center-wide announcements, direct messaging, and a notification system (delivered to templates via a context processor). |
| 🚨 **Incidents** | Incident reports classified by type and severity. |
| 🧑‍🏫 **Staffing** | Staff profiles, assignments, shifts, and **ratio requirements** for compliance monitoring. |
| 🏫 **Facilities** | Sites, rooms, and programs structured by age group and program type. |
| 📄 **Documents** | Document storage and classification, backed by private S3-compatible object storage. |

---

## 🛠 Tech Stack

| Layer | Technology |
| --- | --- |
| **Language** | Python 3.12+ |
| **Framework** | Django 6.0 |
| **Database** | PostgreSQL (with server-side connection pooling) |
| **Cache** | Redis (via `django-redis`) |
| **App Server** | Gunicorn |
| **Static Files** | WhiteNoise + DigitalOcean Spaces (S3-compatible) via `django-storages` |
| **Media Storage** | Private S3-compatible buckets (restricted/compliance media) |
| **Auth & Security** | `django-allauth`, Argon2 password hashing, field-level encryption (`pgcrypto` + Fernet), reCAPTCHA & simple-captcha |
| **UI** | Crispy Forms + Bootstrap 5, Django Widget Tweaks |
| **Observability** | `django-prometheus` instrumentation middleware |
| **Secrets** | [Doppler](https://www.doppler.com/) |
| **Dependency Mgmt** | [Poetry](https://python-poetry.org/) |
| **Task Runner** | [Task (go-task)](https://taskfile.dev/) |
| **CI/CD** | GitHub Actions · Codecov · Codacy · Safety · Bandit |

---

## 🏗 Architecture

```
HTTP ─► Gunicorn ─► Django (core)
                      │
                      ├── Prometheus middleware (request metrics)
                      ├── WhiteNoise (static asset serving)
                      ├── CORS / CSRF / Security middleware
                      ├── LoginRequired middleware (auth gate)
                      └── Cache middleware (Redis-backed)
                      │
        ┌─────────────┴───────────────────────────────┐
        ▼                                              ▼
  applications/*  (domain apps)                  common/  (shared helpers,
  accounts, children, enrollment,                          storage backends)
  attendance, handoff, communication,
  incidents, staffing, facilities, documents
        │
        ▼
  PostgreSQL (pooled)   Redis   S3-compatible Object Storage (DO Spaces)
```

---

## 🚀 Getting Started

### Prerequisites

Make sure the following are installed and available on your `PATH`:

- **Python 3.12+**
- **PostgreSQL** (a running instance you can connect to)
- **[Task](https://taskfile.dev/installation/)** (`go-task`) — the project's command runner
- **[Doppler CLI](https://docs.doppler.com/docs/install-cli)** — secrets are injected at runtime
- **Redis** (for caching)

> 💡 Most workflows are wrapped in `Taskfile.yml`. Run `task -l` to list every available command.

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/Terry-BrooksJr/safari-leader.git
cd safari-leader

# 2. Create the virtual environment and install all dependencies
#    (creates .venv, installs Poetry, locks, and installs the project)
task install
```

### Environment Variables

Secrets are managed with **Doppler** and injected at runtime — they are never committed to the repo.
The application reads the following variables (configure them in your Doppler project or a local
`.envrc`, which is git-ignored):

| Variable | Purpose |
| --- | --- |
| `SECRET_KEY` | Django secret key |
| `FERNET_KEYS` | Comma-separated keys for field-level encryption |
| `POSTGRES_DB` | Database name |
| `PG_DATABASE_USER` | Database user |
| `PG_DATABASE_PASSWORD` | Database password |
| `PG_DATABASE_HOST` | Database host |
| `PG_DATABASE_PORT` | Database port |
| `RECAPTCHA_PUBLIC_KEY` | Google reCAPTCHA site key |
| `RECAPTCHA_PRIVATE_KEY` | Google reCAPTCHA secret key |
| `AWS_ACCESS_KEY_ID` | Object-storage access key (DO Spaces / S3) |
| `AWS_SECRET_ACCESS_KEY` | Object-storage secret key |
| `AWS_DEFAULT_REGION` / `AWS_S3_REGION_NAME` | Storage region |
| `AWS_STORAGE_BUCKET_NAME` | Bucket name |
| `AWS_S3_CUSTOM_DOMAIN` | CDN/custom domain for assets |
| `AWS_S3_ENDPOINT_URL` | Storage endpoint (defaults to DigitalOcean Spaces NYC3) |
| `DOPPLER_TOKEN` | Doppler service token (used by Task targets) |

> ⚠️ **Never commit real secrets.** `.envrc`, `.env`, and `local_settings.py` are already git-ignored.

### Database Setup

Run migrations to provision the schema:

```bash
task db_sync     # runs makemigrations + migrate
```

> `db_sync` requires `DOPPLER_TOKEN` to be set.

### Running the App

```bash
# Django development server (defaults to 127.0.0.1:8000)
task run:dev

# ...or pass a custom port
task run:dev -- 9000

# Single-worker Gunicorn for production-parity local testing
task run:gunicorn-dev
```

Then open **http://127.0.0.1:8000** — the root path redirects to `/dashboard/`.

| Route | Description |
| --- | --- |
| `/dashboard/` | Main authenticated dashboard |
| `/children/` | Child profiles & records |
| `/registration/` | Enrollment |
| `/attendance/` | Attendance & check-in/out |
| `/communication/` | Announcements & messaging |
| `/admin/` | Django admin |

---

## ⚙️ Task Reference

Common `Taskfile.yml` targets (run `task -l` for the complete list):

| Command | Description |
| --- | --- |
| `task install` | Create venv and install all dependencies via Poetry |
| `task run:dev` | Start the Django development server |
| `task run:gunicorn-dev` | Start a single-worker Gunicorn server |
| `task db_sync` | Make and apply database migrations |
| `task collect` | Collect static files for production |
| `task run:test` | Run the full test suite with coverage (primary CI task) |
| `task test:coverage` | Run tests with term, XML, and HTML coverage reports |
| `task lint:lint` | Run all linters/formatters in check mode |
| `task lint:fix` | Auto-fix lint/format issues, then report what remains |
| `task django -- <cmd>` | Run any Django management command (e.g. `task django -- shell`) |
| `task freeze` | Pin dependencies and export requirements files |
| `task build-image` | Build & push the multi-arch Docker image |
| `task compose:up` / `compose:down` | Manage the Docker Compose stack |

---

## 🧪 Testing

The project uses **pytest** with `pytest-django` and **coverage**, configured in `pyproject.toml`.

```bash
# Run the full suite with coverage (generates cobertura.xml)
task run:test

# Generate term + XML + HTML coverage reports (htmlcov/index.html)
task test:coverage
```

Coverage is measured across the `applications`, `common`, and `core` packages (migrations excluded)
and uploaded to **Codecov** and **Codacy** in CI.

---

## 🎨 Code Quality

A comprehensive quality gate runs on every push and pull request. The same checks run locally:

```bash
task lint:lint   # check-only (CI behavior)
task lint:fix    # auto-fix, then report remaining issues
```

| Tool | Role |
| --- | --- |
| **Black** | Code formatting |
| **isort** | Import sorting |
| **Ruff** | Fast linting |
| **Pylint** | Comprehensive linting (with `pylint-django`) |
| **autoflake** | Removes unused imports/variables |
| **mypy** | Static type checking (with `django-stubs`) |
| **Bandit** | Security static analysis |
| **djlint** | Django template linting |
| **pre-commit** | Git hooks to run checks before commit |

---

## 📦 Deployment

Production runs under **Gunicorn** with configuration in [`.deploy/gunicorn.conf.py`](.deploy/gunicorn.conf.py),
serving static assets via WhiteNoise and media via S3-compatible object storage.

```bash
# Full production bring-up: install deps, migrate, then start Gunicorn
task run:prod

# ...or specify a port
task run:prod -- 8080
```

**Container deployment** targets are defined in `Taskfile.yml` (`build-image`, `compose:up`,
`compose:down`) for a multi-architecture (`linux/amd64`, `linux/arm64`) image build.

> ℹ️ The Docker build/compose targets reference a `Dockerfile` and `docker-compose.yml`. Ensure these
> deployment manifests are present before invoking the container tasks.

---

## 🔒 Security

Safari Leader handles sensitive information about minors, so security is treated as a first-class concern:

- **Field-level encryption** for sensitive records via `pgcrypto` and Fernet-encrypted fields.
- **Argon2** password hashing (with secure fallbacks).
- **Role-based access control** scoped to children and rooms.
- **Login-required** middleware gating the entire application surface.
- **reCAPTCHA** and CAPTCHA protection on public-facing forms.
- **Private object storage** for compliance documents and restricted media.
- **Automated scanning** with Bandit (SAST) and Safety (dependency CVEs) in CI.

Found a vulnerability? Please report it privately to the maintainer (see [Author](#-author)) rather than
opening a public issue.

---

## 📁 Project Structure

```
safari-leader/
├── applications/          # Domain apps
│   ├── accounts/          # Users, roles, RBAC
│   ├── attendance/        # Attendance records & check-in/out events
│   ├── children/          # Child profiles, guardians, allergies, custody
│   ├── communication/     # Announcements, messages, notifications
│   ├── documents/         # Document storage & classification
│   ├── enrollment/        # Enrollment lifecycle & schedules
│   ├── facilities/        # Sites, rooms, programs
│   ├── handoff/           # Secure student handoff workflow
│   ├── incidents/         # Incident reports
│   └── staffing/          # Staff profiles, shifts, ratio requirements
├── common/                # Shared helpers & storage backends
├── core/                  # Project config (settings, urls, wsgi, asgi)
├── run/                   # manage.py entrypoint
├── templates/             # Django templates (per-app + components)
├── static/                # CSS/SCSS, JS, fonts, images, vendors
├── scripts/               # Utility scripts (e.g. seed data generation)
├── .deploy/               # Deployment config (Gunicorn)
├── .github/               # CI workflows & composite actions
├── Taskfile.yml           # Task runner definitions
├── pyproject.toml         # Project metadata & dependencies (Poetry)
└── poetry.lock            # Locked dependency versions
```

---

## 🤝 Contributing

Contributions are welcome! To get started:

1. **Fork** the repository and create a feature branch (`git checkout -b feat/my-feature`).
2. Make your changes and ensure the quality gate passes: `task lint:lint && task run:test`.
3. **Commit** your changes (pre-commit hooks will run automatically).
4. **Open a pull request** against `master`.

Please keep PRs focused, include tests for new behavior, and ensure CI is green before requesting review.

---

## 📄 License

This project is licensed under the **MIT License**. See the `pyproject.toml` metadata for details.

---

## 👤 Author

**Terry A. Brooks, Jr.**
📧 [Terry.Arthur@BrooksJr.com](mailto:Terry.Arthur@BrooksJr.com)
🔗 [github.com/Terry-BrooksJr](https://github.com/Terry-BrooksJr)

<div align="center">

---

Made with ❤️ for the people who care for our kids.

</div>
