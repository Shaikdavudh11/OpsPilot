# Deploying OpsPilot Backend on Hugging Face Spaces (100% Free)

This guide walks you through deploying the **entire OpsPilot AI backend** to **Hugging Face Spaces**.

---

## 1. What Runs Inside the Hugging Face Space?

Under the hood, Hugging Face Spaces provisions a **dedicated Linux Docker container** with **16 GB of RAM and 2 vCPUs** completely free of charge.

The **entire backend** runs inside this container:
- **FastAPI Core:** All endpoints (`/health`, `POST /api/incidents/analyze`, `GET /api/demo-scenarios`, `GET /api/incidents`, `/docs`).
- **Grounded SRE Engine:** Deterministic `MockAIProvider` (works out of the box with zero external keys) or real `Gemini` / `OpenAI` providers.
- **Security & Secret Redactor:** Pre-AI regex scrubbing of credentials and prompt injection shields.
- **SQLAlchemy Persistence:** Local SQLite database (`opspilot.db`) persisted directly inside the Space container.

```
┌───────────────────────────────────────────────────────────────────────┐
│               HUGGING FACE SPACE CONTAINER (16 GB RAM)                │
│                                                                       │
│  FastAPI (Port 7860) ──> SecretRedactor ──> Mock/Gemini AI Engine     │
│         │                                         │                   │
│         └──> SQLite DB (opspilot.db) <────────────┘                   │
│                                                                       │
│  Public URL: https://<your-username>-opspilot-api.hf.space            │
└───────────────────────────────────────────────────────────────────────┘
```

---

## 2. Why Hugging Face Spaces is Ideal for OpsPilot

| Feature | Hugging Face Spaces | Render / Railway / Heroku Free |
| :--- | :--- | :--- |
| **Free Hardware** | **16 GB RAM & 2 vCPUs** | 512 MB RAM & 0.1 CPU |
| **Cold Starts** | **Never goes to sleep** (fast response) | Sleeps after 15m (30-40s delay) |
| **Container Tech** | Native Docker container | Limited runtime environments |
| **Cost** | **100% Free Forever** | Often requires credit card or expires |
| **Portfolio Value** | Premier AI & MLOps ecosystem | Generic web hosting |

---

## 3. Step 1: Create Your Free Space on Hugging Face

1. Go to **[https://huggingface.co](https://huggingface.co)** and sign in.
2. Click your profile avatar (top-right) → **"New Space"**.
3. Configure your Space:
   - **Space Name:** `opspilot-api`
   - **License:** `mit` or `apache-2.0`
   - **Select the Space SDK:** Click **Docker** *(Select "Blank")*.
   - **Space Hardware:** Select **Free (CPU basic · 2 vCPU · 16 GB RAM)**.
   - **Visibility:** Public.
4. Click **"Create Space"**.

---

## 4. Step 2: Deploy the Backend Code

Choose either of the two methods below:

### Method A: Automated GitHub Actions CI/CD (The DevOps Way)

OpsPilot already includes [.github/workflows/sync-to-huggingface.yml](file:///Users/shaik/Desktop/DevOpsProjects/OpsPilot/.github/workflows/sync-to-huggingface.yml). Whenever you push to your GitHub repo, GitHub Actions automatically deploys the backend to Hugging Face!

1. **Create a Hugging Face Access Token:**
   - Go to **[https://huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)**.
   - Click **"Create new token"** → Name: `github-actions` → Role: **Write** → Click **Create Token**.
   - Copy the token string (starts with `hf_...`).
2. **Add Secrets to Your GitHub Repository:**
   - In your GitHub repo, go to **Settings** → **Secrets and variables** → **Actions**.
   - Add Secret: `HF_TOKEN` = *(paste your `hf_...` token)*
   - Add Secret: `HF_SPACE_REPO` = `<your-hf-username>/opspilot-api`
3. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "feat: deploy to hugging face"
   git push origin main
   ```
   GitHub Actions will automatically extract `apps/api` and push it to Hugging Face Spaces!

---

### Method B: Direct Git Push from Your Terminal

If you prefer to deploy manually without GitHub Actions:

```bash
# 1. Copy the Hugging Face Dockerfile to apps/api
cp apps/api/Dockerfile.hf apps/api/Dockerfile

# 2. Split apps/api into a deploy branch and push to HF:
git subtree split --prefix=apps/api -b hf-release
git push https://huggingface.co/spaces/<YOUR-HF-USERNAME>/opspilot-api hf-release:main --force
```
*(When prompted for password, paste your Hugging Face Access Token).*

---

## 5. Step 3: Configure Space Variables & Secrets (Optional)

In your Hugging Face Space:
1. Click the **"Settings"** tab (top right of your Space page).
2. Scroll to **"Variables and secrets"**:
   - **New variable:**
     - `AI_PROVIDER` = `mock` *(default)*
     - `ENVIRONMENT` = `production`
   - **New secret (if you want real AI models):**
     - `GEMINI_API_KEY` = `your_gemini_api_key`
     - `OPENAI_API_KEY` = `your_openai_api_key`
3. If you add or modify variables, click **Restart Space** to apply.

---

## 6. Step 4: Verify Your Live Backend

When the Space finishes building, the top badge will turn green and say **"Running"**.

Your backend URL is:
`https://<YOUR-HF-USERNAME>-opspilot-api.hf.space`

### 1. Test Health Endpoint:
```bash
curl https://<YOUR-HF-USERNAME>-opspilot-api.hf.space/health
```
Response:
```json
{
  "status": "healthy",
  "service": "OpsPilot API",
  "version": "1.0.0",
  "environment": "production",
  "ai_provider": "mock"
}
```

### 2. Test Swagger Interactive Documentation:
Open in browser:
`https://<YOUR-HF-USERNAME>-opspilot-api.hf.space/docs`

---

## 7. Step 5: Connect Your Vercel Frontend to Hugging Face

Now connect your Next.js frontend on Vercel to your live Hugging Face backend:

1. Open your project on **[Vercel](https://vercel.com)**.
2. Go to **Settings** → **Environment Variables**.
3. Add:
   - **Key:** `NEXT_PUBLIC_API_URL`
   - **Value:** `https://<YOUR-HF-USERNAME>-opspilot-api.hf.space`
4. Click **Redeploy** on your latest Vercel deployment.

Your frontend on Vercel is now talking live to your entire AI incident investigation engine running on Hugging Face Spaces!
