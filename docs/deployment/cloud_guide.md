# OpsPilot — Free Cloud Deployment Guide

This guide details how to deploy the entire **OpsPilot** system to the cloud **100% free of charge**:
- **Frontend (Next.js):** Deployed on **Vercel** (Global Edge CDN, Free Hobby Tier)
- **Entire Backend (FastAPI + AI Engine + DB):** Deployed on **Hugging Face Spaces** (Dedicated Linux Container with **16 GB RAM & 2 vCPUs**, 100% Free Forever)

---

## 1. System Architecture & Topology

```
                  ┌──────────────────────────────────────────────┐
                  │                 USER BROWSER                 │
                  └──────────────────────┬───────────────────────┘
                                         │
                        1. Visits Web App│
                                         ▼
                  ┌──────────────────────────────────────────────┐
                  │           FRONTEND (Hosted on VERCEL)        │
                  │   Next.js 16 • Tailwind • SRE Dashboard      │
                  │   URL: https://opspilot.vercel.app           │
                  └──────────────────────┬───────────────────────┘
                                         │
                        2. API Calls (HTTPS)
                                         ▼
                  ┌──────────────────────────────────────────────┐
                  │      ENTIRE BACKEND (HUGGING FACE SPACES)    │
                  │   • Full FastAPI Application (Python 3.12)   │
                  │   • Pydantic v2 Schema Validation            │
                  │   • Secret Redactor & Injection Defense      │
                  │   • SRE Root Cause & Evidence Engine         │
                  │   • SQLAlchemy Persistence (SQLite/Postgres) │
                  │   • 16 GB RAM & 2 vCPUs Container (FREE)     │
                  │   URL: https://<username>-opspilot-api.hf.space│
                  └──────────────────────────────────────────────┘
```

In this architecture:
1. **GitHub** holds the complete monorepo (`apps/web` and `apps/api`).
2. **Hugging Face Spaces** hosts the **entire backend** inside a high-memory Docker container.
3. **Vercel** hosts the **frontend** and communicates with Hugging Face via the environment variable `NEXT_PUBLIC_API_URL`.

---

## 2. Step 1: Deploy Entire Backend to Hugging Face Spaces

### Why Hugging Face Spaces for the Backend?
- **16 GB RAM & 2 vCPUs** free forever (32x more memory than Render or Heroku).
- **Never sleeps:** No cold starts or 40-second delays.
- Dedicated HTTPS endpoint: `https://<your-username>-opspilot-api.hf.space`.

---

### Step 1.1: Create Your Free Space on Hugging Face
1. Log in to **[huggingface.co](https://huggingface.co)** (create a free account if needed).
2. Click your profile avatar (top-right) → **"New Space"**.
3. Configure the Space:
   - **Space Name:** `opspilot-api`
   - **License:** `mit` or `apache-2.0`
   - **Space SDK:** Choose **Docker** *(Select "Blank")*
   - **Space Hardware:** Select **Free (2 vCPU · 16 GB RAM)**
   - **Visibility:** Public
4. Click **"Create Space"**.

---

### Step 1.2: Deploy the Backend Code

You can deploy using either of two methods:

#### Method A: Automated GitHub Actions CI/CD (Recommended DevOps Practice)

OpsPilot includes a prebuilt workflow in [.github/workflows/sync-to-huggingface.yml](file:///Users/shaik/Desktop/DevOpsProjects/OpsPilot/.github/workflows/sync-to-huggingface.yml) that pushes the backend to Hugging Face whenever you push to GitHub.

1. **Get your Hugging Face Token:**
   - Go to **[huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)**.
   - Click **"Create new token"** → Name: `github-deploy` → Role: **Write** → Click **Create Token**.
   - Copy the token string (starts with `hf_...`).
2. **Add Secrets to GitHub:**
   - Go to your GitHub repository → **Settings** → **Secrets and variables** → **Actions**.
   - Add Secret: `HF_TOKEN` = *(your `hf_...` token)*
   - Add Secret: `HF_SPACE_REPO` = `<your-username>/opspilot-api`
3. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "feat: setup cloud deployment"
   git push origin main
   ```
   GitHub Actions will automatically build and deploy your backend to Hugging Face Spaces!

---

#### Method B: Direct Git Push from Your Terminal

If you prefer deploying directly from your computer without GitHub Secrets:

```bash
# 1. Copy the Hugging Face Dockerfile to apps/api
cp apps/api/Dockerfile.hf apps/api/Dockerfile

# 2. Split and push apps/api directly to Hugging Face:
git subtree split --prefix=apps/api -b hf-deploy
git push https://huggingface.co/spaces/<YOUR-USERNAME>/opspilot-api hf-deploy:main --force
```
*(When prompted for password, paste your Hugging Face `Write` token).*

---

### Step 1.3: Verify Your Live Backend

Once Hugging Face shows the Space status as **"Running"**:
- **Health Check:** `https://<YOUR-USERNAME>-opspilot-api.hf.space/health`
- **Interactive Swagger Docs:** `https://<YOUR-USERNAME>-opspilot-api.hf.space/docs`

---

## 3. Step 2: Deploy Frontend on Vercel

**Vercel** provides fast Edge hosting for Next.js applications for free.

### Step 2.1: Import Repository
1. Go to **[vercel.com](https://vercel.com)** and sign in with GitHub.
2. Click **"Add New..."** → **"Project"**.
3. Find your `OpsPilot` repository and click **"Import"**.

### Step 2.2: Configure Monorepo Root Directory
1. Under **Configure Project**, click **"Edit"** next to **Root Directory**.
2. Select or type: **`apps/web`** *(Crucial: tells Vercel where the Next.js project lives)*.
3. The **Framework Preset** will automatically show **Next.js**.

### Step 2.3: Set Environment Variable
Expand the **Environment Variables** section and add:
- **Key:** `NEXT_PUBLIC_API_URL`
- **Value:** `https://<YOUR-USERNAME>-opspilot-api.hf.space` *(paste your live Hugging Face backend URL)*

### Step 2.4: Deploy
Click **"Deploy"**. In ~45 seconds, your production frontend will be live at:
`https://opspilot.vercel.app`

---

## 4. CORS & Network Security Configuration

The FastAPI backend in [main.py](file:///Users/shaik/Desktop/DevOpsProjects/OpsPilot/apps/api/app/main.py) is pre-configured with:
```python
allow_origin_regex=r"^https:\/\/.*\.vercel\.app$"
```
This guarantees that:
- Any Vercel deployment URL (including preview branch URLs) can make API calls to your Hugging Face backend.
- Browsers will not trigger CORS preflight blocks.
- Your credentials and AI keys remain server-side on Hugging Face Spaces and are never exposed to the public browser.

---

## 5. Summary Table

| Service | Platform | Free Specs | Cost | Live URL Format |
| :--- | :--- | :--- | :--- | :--- |
| **Frontend** | Vercel | Global CDN, Unlimited Bandwidth | $0 / month | `https://opspilot.vercel.app` |
| **Backend** | Hugging Face Spaces | 16 GB RAM, 2 vCPUs, Persistent Linux Container | $0 / month | `https://<user>-opspilot-api.hf.space` |
| **Database** | HF Local Storage / SQLite | Built into the container filesystem | $0 / month | Embedded in backend |
