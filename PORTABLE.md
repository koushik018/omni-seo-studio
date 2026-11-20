# 🚀 OmniSEO Studio — Portable Edition & GitHub Setup Guide

Welcome to **OmniSEO Studio Portable**! This package is 100% self-contained and ready to run on any Windows, macOS, or Linux device, or be published directly to GitHub.

---

## 🌟 How to Share with Friends (Zero Setup Needed)

### Option 1: 1-Click Launch on Windows (Recommended for Friends)
1. Zip the `omni-seo-studio` folder and send it to your friend.
2. Your friend unzips the folder anywhere on their computer.
3. Double-click **`start.bat`**.
   - It automatically verifies Python (Python 3.9+).
   - It automatically installs all dependencies (`pip install -r requirements.txt`).
   - It starts the local server.
   - It automatically opens their default browser to `http://localhost:8000`.

### Option 2: 1-Click Launch on macOS & Linux
In terminal, navigate to the folder and run:
```bash
chmod +x start.sh
./start.sh
```
The server will start and open `http://localhost:8000` in the default browser.

### Option 3: Standalone Terminal CLI Runner
You and your friends can run full audits directly from the command line without opening a browser:
```bash
# Audit a live website with target keyword
python cli.py https://github.com --keyword "developer platform"

# Audit a local pre-launch HTML file before it goes live
python cli.py ./my-prelaunch-site/index.html --keyword "3d animation studio"

# Audit and export an Executive Markdown report and 100/100 Auto-Fixed HTML
python cli.py https://example.com --keyword "cloud hosting" --export report.md --fix-html fixed.html

# Generate Claude 3.5/3.7 & DeepSeek R1 optimization prompts directly
python cli.py https://example.com --keyword "ai agents" --claude prompt_claude.xml --deepseek prompt_deepseek.md
```

---

## 🐙 Publishing to Your GitHub Account (`koushik018`)

This folder has already been initialized as a clean Git repository on branch `main`.

To publish it to your GitHub profile:

### Step 1: Create a New Repository on GitHub
1. Go to [https://github.com/new](https://github.com/new).
2. Set the repository name to: **`omni-seo-studio`** (or any name you prefer).
3. Choose **Public** or **Private**.
4. **DO NOT** check "Add a README file" or ".gitignore" (we already have them created).
5. Click **Create repository**.

### Step 2: Push Your Code
Open your terminal inside `D:\omni-seo-studio` and run:

```bash
git remote add origin https://github.com/koushik018/omni-seo-studio.git
git branch -M main
git push -u origin main
```

Your repo will immediately be live at:
👉 **`https://github.com/koushik018/omni-seo-studio`**

---

## 📦 What is Included in this Package

| File / Folder | Purpose |
| :--- | :--- |
| `start.bat` | 1-Click Windows launcher (auto-installs deps & opens browser) |
| `start.sh` | 1-Click macOS/Linux launcher |
| `run.py` | FastAPI server entrypoint (hot-reload enabled) |
| `cli.py` | Standalone terminal CLI runner for automated audits & CI/CD |
| `test_suite.py` | Enterprise test suite (100% passed across all 10 modules) |
| `app/analyzer.py` | Multi-dimensional scoring: SEO, GEO, JS, Security, 3D Canvas |
| `app/crawler.py` | 14-crawler user-agent matrix (Googlebot, GPTBot, ClaudeBot, etc.) |
| `app/generators.py` | 100/100 HTML, Claude XML prompts, DeepSeek prompts, 3D Fallbacks |
| `app/static/` | Clean, dark, responsive dashboard (no neon, no AI slop) |
| `3D_WEBSITES_SEO.md` | Complete architecture guide for 3D/Canvas/WebGL websites |
| `GOOGLE_SEARCH_CONSOLE.md`| Step-by-step Google Search Console ranking blueprint |
| `AI_PROMPTS.md` | Master prompt guides for Claude 3.5/3.7 and DeepSeek R1 |
