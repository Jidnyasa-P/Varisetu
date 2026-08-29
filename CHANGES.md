# What changed — apply these on top of your existing repo

Keep the same folder structure below relative to your repo root; each file
replaces (or adds to) the matching path in your existing project.

## Modified

- `Backend/app/core/config.py`
  - `VISION_PROVIDER`: `"mock"` → `"hf_space"`
  - `HF_SPACE_ID`: `"Jidnyasa-P/VariSetu-Vision"` (doesn't exist) → `"Saj2005/VariSetu"` (your real deployed Space)

- `Backend/.env.example`
  - Same two values corrected, for local dev consistency.

- `Frontend/app.js` (only lines 3-11 changed)
  - `API_BASE`/`WS_BASE` hardcoded to `http://localhost:8000` → now derived
    from `window.location.origin`, so it works both locally and once
    deployed, with no manual config needed.

## New

- `Backend/.env.render.example` — reference for exactly which environment
  variables to set in Render's dashboard (DATABASE_URL, JWT_SECRET_KEY,
  VISION_PROVIDER, HF_SPACE_ID, etc.), with a freshly generated JWT secret
  you can use or replace.

- `render.yaml` — goes at your **repo root** (sibling to `Backend/` and
  `Frontend/`), enables one-click Blueprint deployment on Render.

- `DEPLOY_RENDER.md` — full step-by-step deployment guide, from Supabase
  setup through to your first live request.

## Verified before packaging (not a file, just confirming this was tested)

- `Backend/requirements.txt` installs cleanly with no dependency conflicts
  (tested in a clean venv).
- `Backend/app/main.py` imports successfully and registers all 33 routes
  with these config changes applied.
