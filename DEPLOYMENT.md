# Deployment Documentation — MTG Collection Manager

## Live URL

www.tccartemtgcollection.com

*(Also accessible at: https://web-production-de99a.up.railway.app)*

---
## Domain & Registrar
- **Domain:** `www.tccartemtgcollection.com`
- **Registrar:** Namecheap
- DNS is pointed at Railway using a CNAME record. Railway handles TLS automatically via Let's Encrypt, so HTTPS is enabled with no extra configuration.

---

## Hosting Provider

The entire app — frontend and backend — is deployed on **[Railway](https://railway.app)**. Railway watches the GitHub repository and automatically redeploys whenever a new commit is pushed to `main`. No manual build steps needed.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Vanilla HTML, CSS, JavaScript (no framework) |
| Backend | Python 3 / Flask |
| WSGI server | Gunicorn |
| Database | PostgreSQL |
| Hosting | Railway |

The frontend is served as static files directly by Flask, so there is only one service to deploy and one URL to worry about.

---

## Database

- **Type:** PostgreSQL
- **Hosted on:** Railway (provisioned as a Railway Postgres plugin inside the same project)
- The schema is created automatically on startup via `CREATE TABLE IF NOT EXISTS` inside `app.py`, so there is no separate migration step.
- On first deploy (empty database), run the seed script to load 30 starter cards — see *Seeding* below.

---

## How to Deploy and Update the App

### First-time setup

1. Fork or clone this repository to your own GitHub account.
2. Go to [railway.app](https://railway.app) and create a new project.
3. Choose **Deploy from GitHub repo** and select this repository.
4. Inside the project, click **+ Create** → **Database** → **PostgreSQL** to provision a database.
5. In the web service's **Variables** tab, add a variable:
   - Key: `DATABASE_URL`
   - Value: click the reference picker and select the Postgres `DATABASE_URL`
6. Railway will build and deploy automatically. The `Procfile` tells it to run Gunicorn.

### Updating the app

Just push commits to the `main` branch:
Railway picks up the push and redeploys within a minute or two. Zero downtime for most changes.

### Seeding the database

After the first deploy (or after clearing the database), load the 30 starter cards by running:

```bash
python http_seed.py https://www.tccartemtgcollection.com
```

This script uses only Python's built-in `urllib` — no extra packages required locally. It checks whether data already exists before inserting, so it is safe to run multiple times.

---

## Configuration and Secrets

All sensitive configuration is managed through **environment variables** — nothing is hardcoded in the source code.

| Variable | Description | Where to set it |
|----------|-------------|-----------------|
| `DATABASE_URL` | PostgreSQL connection string | Railway web service → Variables |
| `PORT` | Port for Gunicorn to bind (optional) | Provided automatically by Railway |

**Local development:** Copy `.env.example` to `.env` and fill in your local PostgreSQL URL. Use a tool like `python-dotenv` or simply `export DATABASE_URL=...` in your shell before running `python app.py`. Never commit `.env` to Git — it is listed in `.gitignore`.

**Production:** Variables are set in the Railway dashboard and injected into the container at runtime. They are never stored in the repository.

