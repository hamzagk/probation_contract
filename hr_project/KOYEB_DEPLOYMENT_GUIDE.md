# Deploying the GIK HR Portal to Koyeb

This guide walks you through deploying the Django HR portal to Koyeb so that
everyone at GIK Institute can access it. The portal will be served over HTTPS
at `https://hr-portal-web-<your-account>.koyeb.app`.

## Architecture

Two Koyeb services share the same Docker image:

| Service              | Type   | Runs                                    | Purpose                          |
|----------------------|--------|-----------------------------------------|----------------------------------|
| `hr-portal-web`      | web    | gunicorn on port 8000                   | Serves the portal                |
| `hr-portal-worker`   | worker | `celery -A hr_project worker -l info`   | Runs scheduled email tasks       |

External dependencies:

- **Postgres** (Neon free tier recommended) — primary database
- **Redis** (Upstash free tier) — Celery broker
- **cron-job.org** (free) — triggers scheduled emails by hitting an HTTPS endpoint

You do **not** need a paid Koyeb tier for any of this.

---

## 1. Provision external services

### 1a. Neon Postgres

1. Sign up at <https://neon.tech> (free).
2. Create a project named `gik-hr-portal`. Region: pick the one closest to
   where most users are (Pakistan → `Asia Pacific (Singapore)` or `EU`).
3. Copy the **pooled connection string** from the Neon dashboard. It looks
   like `postgresql://neondb_owner:xxxxx@ep-xxx-pooler.<region>.aws.neon.tech/neondb?sslmode=require`.
4. Keep this handy — you'll paste it into Koyeb as `DATABASE_URL`.

### 1b. Upstash Redis

1. Sign up at <https://upstash.com> (free).
2. Create a Redis database named `gik-hr-broker`. Region: same as Neon.
3. Copy the **Redis URL** (with TLS). It looks like `rediss://default:xxxxx@<host>.upstash.io:6379`.
4. Keep this handy — you'll paste it into Koyeb as `REDIS_URL`.

### 1c. Generate a Django SECRET_KEY

Run this on your local machine:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Save the output — it becomes `SECRET_KEY` on Koyeb.

### 1d. SMTP credentials

The portal sends email via SMTP. If you have a Gmail/Outlook account with an
**app password** ready, set:

- `EMAIL_HOST=smtp.gmail.com` (or `smtp.office365.com` for Outlook)
- `EMAIL_PORT=587`
- `EMAIL_USE_TLS=True`
- `EMAIL_HOST_USER=your.email@giki.edu.pk`
- `EMAIL_HOST_PASSWORD=<your app password>`

If you do **not** have credentials yet, the portal will still deploy, but any
"send email" button (e.g. contract renewal, probation notifications) will
return SMTP errors until you set them.

### 1e. CRON_TOKEN

Run this once and save the output:

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

This token is the shared secret between cron-job.org and the portal. Keep it
private.

---

## 2. Push the repo to GitHub

Koyeb builds from a GitHub repo. Push the current code:

```bash
cd C:\Users\Hamza\.qwen\projects\hr_contract
git add hr_project/celery.py  # if not already added
git add hr_project/hr_project/__init__.py
git add hr_project/hr_project/celery.py
git add hr_project/Dockerfile
git add hr_project/docker-entrypoint.sh
git add hr_project/koyeb.yaml
git add hr_project/hr_project/settings.py
git add hr_project/hr_portal/views.py
git add hr_project/hr_portal/urls.py
git add hr_project/KOYEB_DEPLOYMENT_GUIDE.md
git commit -m "Add Koyeb deployment support"
git push origin main
```

If the repo is not yet on GitHub, create it at <https://github.com/new> and
follow GitHub's instructions to push.

---

## 3. Create the Koyeb web service

1. Sign in to <https://app.koyeb.com>.
2. Click **Create Web Service** → **GitHub**.
3. Select your repository and branch (`main`).
4. **Builder**: Docker.
5. **Dockerfile path**: `hr_project/Dockerfile` (Koyeb asks for the path
   relative to the repo root).
6. **Run command**: leave the default — it uses the Dockerfile `CMD`.
7. **Port**: `8000`.
8. **Instance type**: `eco-nano` (free).
9. **Region**: `fra` (Frankfurt) or your preferred region.
10. **Environment variables** — add the following (mark sensitive ones as
    secrets):

    | Key                    | Value                                                            | Secret? |
    |------------------------|------------------------------------------------------------------|---------|
    | `PORT`                 | `8000`                                                           |         |
    | `DEBUG`                | `False`                                                          |         |
    | `SECURE_SSL_REDIRECT`  | `True`                                                           |         |
    | `SESSION_COOKIE_SECURE`| `True`                                                           |         |
    | `CSRF_COOKIE_SECURE`   | `True`                                                           |         |
    | `SECRET_KEY`           | (the value from step 1c)                                         | yes     |
    | `DATABASE_URL`         | (the Neon connection string from step 1a)                        | yes     |
    | `REDIS_URL`            | (the Upstash URL from step 1b)                                   | yes     |
    | `ALLOWED_HOSTS`        | `*.koyeb.app,<your-custom-domain-if-any>`                        |         |
    | `CSRF_TRUSTED_ORIGINS` | `https://<your-app>.koyeb.app`                                   |         |
    | `EMAIL_HOST`           | `smtp.gmail.com` (or your provider)                              |         |
    | `EMAIL_PORT`           | `587`                                                            |         |
    | `EMAIL_USE_TLS`        | `True`                                                           |         |
    | `EMAIL_HOST_USER`      | your SMTP user                                                   |         |
    | `EMAIL_HOST_PASSWORD`  | your SMTP app password                                           | yes     |
    | `DEFAULT_FROM_EMAIL`   | your SMTP user                                                   |         |
    | `HR_EMAIL`             | HR recipient for notifications                                   |         |
    | `CRON_TOKEN`           | (the value from step 1e)                                         | yes     |
    | `OPENAI_API_KEY`       | your OpenAI key, or leave blank to disable the AI assistant      | yes     |

11. Click **Deploy**. The first build takes a few minutes.

---

## 4. Create the Koyeb worker service

1. Click **Create Service** → **Worker**.
2. Same GitHub repo and branch.
3. **Dockerfile path**: `hr_project/Dockerfile`.
4. **Run command override**: enable and set to
   `celery -A hr_project worker -l info`.
5. **Instance type**: `eco-nano`.
6. **Region**: same as the web service.
7. **Environment variables**: same as the web service **except** omit
   `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS` (the worker doesn't serve HTTP).
8. Click **Deploy**.

---

## 5. First-run setup (one-off)

Once the web service is up:

1. Open a Koyeb exec session on the web service:
   `koyeb service exec hr-portal-web -- bash` (or use the **Exec** tab in
   the dashboard).
2. Run migrations and create a superuser:

   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

3. Exit the exec session.

---

## 6. Configure the external cron

Koyeb's free tier does not have scheduled-job support, so we use a free
external service to drive Celery.

1. Sign up at <https://cron-job.org> (free).
2. Create three cron jobs, all hitting the same URL pattern with a custom
   header:

   **Header on each job**: `X-Cron-Token: <the CRON_TOKEN you set>`

   | Job    | URL                                                              | Schedule (UTC)              |
   |--------|------------------------------------------------------------------|-----------------------------|
   | daily  | `https://<your-app>.koyeb.app/cron/trigger-emails/?type=daily`   | Every day at 09:00          |
   | weekly | `https://<your-app>.koyeb.app/cron/trigger-emails/?type=weekly`  | Tuesdays at 09:00           |
   | monthly| `https://<your-app>.koyeb.app/cron/trigger-emails/?type=monthly` | 1st of month at 09:00       |

3. The endpoint returns 200 with a Celery task ID on success, 401 if the
   token is wrong. cron-job.org shows you the response, so you can verify.

---

## 7. Verify

1. `curl -I https://<your-app>.koyeb.app/` — should return a 302 to
   `/admin/login/`. If you see 400, your `ALLOWED_HOSTS` is missing the
   Koyeb hostname.
2. Log in at `https://<your-app>.koyeb.app/admin/login/` with the
   superuser from step 5.
3. Open the dashboard at `/`. Employee counts should match the data you
   imported into Neon (you'll need to re-import employees since the SQLite
   data is not on the server).
4. Hit the cron endpoint manually to confirm the worker is running:

   ```bash
   curl -X POST -H "X-Cron-Token: <your-token>" \
     "https://<your-app>.koyeb.app/cron/trigger-emails/?type=daily"
   ```

   You should see `{"ok": true, "type": "daily", "task_id": "..."}`. Check
   the worker logs in the Koyeb dashboard to see the task execute.

5. Stop the local dev server (it's no longer needed):

   ```bash
   # Find the bg task in your terminal: banwb5la5
   # Or just close the terminal that started it
   ```

---

## Data migration from local SQLite

The local `db.sqlite3` (320 KB) contains real employee data, but it is
**not** included in the Docker image. To seed Neon with the local data:

1. On your local machine, dump the SQLite database to a SQL file:

   ```bash
   cd C:\Users\Hamza\.qwen\projects\hr_contract\hr_project
   source venv/Scripts/activate   # or venv\Scripts\activate on cmd
   python manage.py dumpdata --exclude auth.permission --exclude contenttypes \
     --exclude admin.logentry --exclude sessions.session \
     --natural-foreign --natural-primary -o seed.json
   ```

2. On the Koyeb web exec session, load it:

   ```bash
   # In the koyeb exec bash session, after uploading seed.json via scp or paste:
   python manage.py loaddata seed.json
   ```

   `koyeb service exec` does not support file upload natively, so an
   easier path is: temporarily expose a `python manage.py loaddata` view,
   or use the Django admin's bulk-import features (the portal already has
   `/employees/import/` for Excel). Re-import the original
   `Employees Details from Oct-25 onwrds.xlsx` via that UI.

3. **Do not** try to copy `db.sqlite3` directly into the Postgres database
   — schema differences will break things.

---

## Limitations of this deployment

- **Media uploads are ephemeral.** Anything uploaded to `/media/` is wiped
  on every redeploy. If you start relying heavily on document uploads, add
  Cloudflare R2 (S3-compatible) via `django-storages[boto3]`. This is a
  v1 simplification.
- **Koyeb free tier caps**: `eco-nano` instances may sleep after a period
  of inactivity. The first request after sleep takes a few seconds.
- **No Koyeb-managed backups**: rely on Neon's point-in-time recovery
  (free tier includes 7 days).
- **`SECRET_KEY` rotation** is manual. If it leaks, rotate by setting a
  new value in Koyeb and redeploying — this will invalidate all existing
  sessions.

---

## Troubleshooting

- **400 Bad Request on the homepage**: `ALLOWED_HOSTS` doesn't include
  your Koyeb hostname. Check the Koyeb dashboard for the actual hostname
  (it includes your account slug).
- **500 errors mentioning `django.db.utils.OperationalError`**: the
  `DATABASE_URL` is wrong or the Neon project is sleeping. Wake it from
  the Neon dashboard.
- **SMTP errors in worker logs**: `EMAIL_HOST_PASSWORD` is wrong, or the
  account doesn't have app-password / "less secure app" access enabled.
- **Cron returns 401**: the `CRON_TOKEN` in cron-job.org doesn't match
  the one set in Koyeb. Check both.
- **Worker not picking up tasks**: the worker service is not running, or
  `REDIS_URL` is wrong. Check the worker logs.
