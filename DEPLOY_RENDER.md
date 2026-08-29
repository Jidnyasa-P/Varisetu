# Deploying VariSetu Backend (+ Frontend) — free, from scratch

This deploys ONE Render service that serves both the FastAPI backend and the
existing Frontend (app.js/index.html) together — `Backend/app/main.py`
already mounts and serves the Frontend directly, so you do not need a
separate Vercel deployment. Simpler, and one less thing to keep in sync.

Everything below is free. The only place you'll be asked for a card is
Supabase's signup flow for identity verification — you will not be charged
as long as you stay on the free tier (which this setup does).

---

## What was fixed before this zip was made (context, not action items)

- `Backend/app/core/config.py` — `HF_SPACE_ID` was pointing at a Space that
  doesn't exist (`Jidnyasa-P/VariSetu-Vision`); fixed to the real deployed
  Space (`Saj2005/VariSetu`). `VISION_PROVIDER` was defaulting to `"mock"`;
  changed to `"hf_space"` so the real models are actually called.
- `Frontend/app.js` — `API_BASE`/`WS_BASE` were hardcoded to
  `localhost:8000`, which would have completely failed once deployed
  anywhere else. Now defaults to same-origin (`window.location.origin`),
  which works correctly both locally and once deployed, with no config
  needed.
- Confirmed `Backend/requirements.txt` installs cleanly with no dependency
  conflicts (tested in a clean virtual environment before packaging this).
- Confirmed the FastAPI app itself imports successfully and registers all
  33 routes without error.
- Removed the unused `Backend/cctv video/` folder (55MB, not referenced
  anywhere in the frontend) to keep the deploy package lean. The Frontend's
  OWN `assets/videos/` folder IS used (the live CCTV demo feeds) and is
  kept.

---

## Step 1 — Set up Supabase (free database)

1. Go to supabase.com, sign up, create a new project (pick any region close
   to you; free tier).
2. Wait for provisioning (~2 minutes).
3. Go to **Project Settings → Database → Connection string**. Select the
   **Transaction pooler** tab (port 6543) — this is the right one for a
   scale-to-zero-friendly host like Render, not the direct connection.
4. Copy the connection string. It looks like:
   ```
   postgresql://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres
   ```
5. You'll need this in Step 3 — just note it down for now. **Change the
   `postgresql://` prefix to `postgresql+asyncpg://`** when you use it (the
   backend uses the async driver):
   ```
   postgresql+asyncpg://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres
   ```

You don't need to create any tables manually — `Backend/app/core/database.py`
creates them automatically on first startup (`init_db()` in the app's
lifespan handler).

---

## Step 2 — Push this code to GitHub

If it's not already the current state of your repo, replace your
`Backend/` and `Frontend/` folders with the ones in this zip (they contain
the fixes above), and add `render.yaml` at the repo root. Commit and push.

```bash
git add Backend Frontend render.yaml
git commit -m "Fix HF Space wiring and same-origin API base for deployment"
git push
```

---

## Step 3 — Deploy on Render

### Option A — Blueprint (uses the included render.yaml)

1. Go to render.com, sign up (free, no card required to start).
2. **New → Blueprint**.
3. Connect your GitHub account and select this repo.
4. Render reads `render.yaml` and shows you the `varisetu-backend` service
   it's about to create. Click **Apply**.
5. Once created, go to the service → **Environment** tab and add the two
   secrets that were deliberately left out of `render.yaml` (secrets should
   never live in a committed file):
   - `DATABASE_URL` = your Supabase connection string from Step 1
   - `JWT_SECRET_KEY` = generate one with:
     ```
     python -c "import secrets; print(secrets.token_urlsafe(48))"
     ```
6. Save — this triggers a redeploy with the new environment variables.

### Option B — Manual Web Service (if you'd rather not use the Blueprint)

1. **New → Web Service** → connect this repo.
2. Fill in:
   - **Root Directory:** `Backend`
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type:** Free
3. Under **Environment Variables**, add everything listed in
   `Backend/.env.render.example` — at minimum:
   ```
   DATABASE_URL=<your Supabase connection string, +asyncpg prefix>
   JWT_SECRET_KEY=<generate your own, see command above>
   VISION_PROVIDER=hf_space
   HF_SPACE_ID=Saj2005/VariSetu
   APP_ENV=production
   DEBUG=false
   AUTH_REQUIRED=true
   ```
4. Click **Create Web Service**.

---

## Step 4 — Watch the first deploy

Render will show build logs, then deploy logs. First build takes a few
minutes (installing dependencies). Watch for:

```
Initializing VariSetu Command Center Backend...
Database tables initialized.
```

If you see `Failed to initialize HF Space Client (...); fallback to mock`
in the logs, the Space call failed — check that `HF_SPACE_ID` is exactly
`Saj2005/VariSetu` (no `/spaces/` prefix, no trailing slash) and that
`https://huggingface.co/spaces/Saj2005/VariSetu` is actually up when you
check it in a browser.

---

## Step 5 — Open it

Render gives you a URL like `https://varisetu-backend-xxxx.onrender.com`.
Open it in a browser — you should see the actual VariSetu dashboard (the
Frontend), not a bare JSON response, since `main.py` serves `index.html` at
the root path.

Log in, and try a flow that touches the real models (e.g. the Lost & Found
search) to confirm the HF Space connection works end-to-end, not just that
the page loads.

---

## Known limitations of this free setup (be upfront about these, don't discover them live)

- **Cold starts.** Render's free tier spins the service down after ~15
  minutes of no traffic. The next request takes 30-50 seconds to wake back
  up. Ping the URL a minute or two before a demo.
- **Uploaded files don't persist.** `STORAGE_PROVIDER=local` writes to
  `Backend/uploads/` on Render's local disk, which is wiped on every
  redeploy and doesn't survive a cold start/restart on the free tier. Fine
  for a demo session, not for real persistence — if that matters later,
  switch to Supabase Storage.
- **Redis, Speech (Sarvam/Groq), Weather, Notifications, Maps** all default
  to `mock`/graceful-fallback and will keep working with simulated data
  until you add real API keys for them — nothing crashes without them.
- **The HF Space itself** has its own separate free-tier constraints
  (ZeroGPU account requirements, 2-Space cap) — already covered in the
  earlier deployment conversation for that piece.
