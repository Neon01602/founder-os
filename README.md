# FounderOS — Vercel Deployment

Multi-agent AI startup analyzer. Three AI agents (Strategist → User Research → Product) analyze your idea and produce a full startup brief.

## Project Structure

```
founderos-vercel/
├── api/                    # Python FastAPI backend (Vercel serverless)
│   ├── index.py            # Entry point + Mangum handler
│   ├── requirements.txt
│   ├── agents/
│   ├── orchestrator/
│   ├── eval/
│   └── schemas/
├── public/                 # Static frontend (served by Vercel CDN)
│   └── index.html
├── vercel.json             # Routing config
└── .env.example
```

## Deploy to Vercel

### Step 1 — Get your OpenRouter API key
1. Go to https://openrouter.ai/keys
2. Create a free account and copy your API key
3. The free DeepSeek V3 model is used (no billing needed)

### Step 2 — Push to GitHub
```bash
git init
git add .
git commit -m "FounderOS initial commit"
git remote add origin https://github.com/YOUR_USERNAME/founderos.git
git push -u origin main
```

### Step 3 — Deploy on Vercel
1. Go to https://vercel.com/new
2. Import your GitHub repository
3. **Framework Preset**: Other
4. **Root Directory**: `.` (leave as default)
5. Click **Add Environment Variable**:
   - Key: `OPENROUTER_API_KEY`
   - Value: `your_key_here`
6. Click **Deploy**

### Step 4 — Done!
Your app will be live at `https://your-project.vercel.app`

---

## Local Development

```bash
# Install Python deps
cd api
pip install -r requirements.txt

# Set env var
cp ../.env.example ../.env
# Edit .env and add your OPENROUTER_API_KEY

# Run backend
cd ..
uvicorn api.index:app --reload --port 8000

# Open frontend (in another terminal)
python -m http.server 3000 --directory public
# Then visit http://localhost:3000
# NOTE: Change const API = '' to const API = 'http://localhost:8000' in public/index.html for local dev
```

## Important Notes

- **Sessions**: Stored in `/tmp` on Vercel — ephemeral per serverless instance. Sessions tab may appear empty across requests (this is a Vercel free-tier limitation).
- **Timeout**: Vercel Pro gives 60s max per function. Free tier is 10s. Agent runs take ~30-60s. **Vercel Pro or a paid plan is recommended** for reliable use.
- **API Key**: Uses OpenRouter (`OPENROUTER_API_KEY`), NOT Anthropic — despite what the original README says.
