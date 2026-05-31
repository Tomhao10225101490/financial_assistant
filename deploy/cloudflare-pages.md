# Cloud Deployment Guide

MarketRadar supports a zero-cost cloud demo for competition judges.

## Option A: Render (recommended for Python API)

1. Push this repository to GitHub.
2. Create a **New Web Service** on [Render](https://render.com/).
3. Connect the repo and use the included [`render.yaml`](../render.yaml), or set:
   - **Build Command**: `pip install --upgrade pip`
   - **Start Command**: `python server.py`
   - **Environment**:
     - `HOST=0.0.0.0`
     - `PORT=10000` (Render sets `PORT` automatically; our server reads it)
4. After deploy, open `https://<your-service>.onrender.com`.

Render free tier sleeps after inactivity; first load may take ~30s.

## Option B: Cloudflare Pages (static + API proxy)

If the API runs on Render at `https://marketradar-api.onrender.com`:

1. Create a Cloudflare Pages project from this repo.
2. **Build command**: none (static site)
3. **Output directory**: `/` (project root)
4. Add `_redirects` or Pages Functions to proxy `/api/*` to Render.

Example `_redirects`:

```text
/api/*  https://marketradar-api.onrender.com/api/:splat  200
```

5. Demo URL becomes `https://<project>.pages.dev`.

## Option C: Local + Cloudflare Quick Tunnel

For offline demos with temporary public URL:

1. Run `run.bat` locally.
2. Run `公开访问金融小助手.bat` with `cloudflared.exe` in project root.

## Health check

```bash
curl https://<host>/api/health
curl https://<host>/api/briefing
curl https://<host>/api/sources
```

## Notes

- Free data sources may rate-limit cloud IPs; TTL caching in `server.py` and `sources/` mitigates this.
- Set `HOST=0.0.0.0` for any PaaS deployment.
- Static assets (`index.html`, `app.js`, `styles.css`) can be served by the same Python process for simplest demo.
