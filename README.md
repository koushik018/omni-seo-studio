# OmniSEO & AI Studio 🌐🤖 (Enterprise Edition 2026)

> The Ultimate Enterprise Search Engine & Generative Engine Optimization (GEO) Audit Platform. Diagnoses every conceivable crawlability, indexing, semantic, performance, security, and AI scraping challenge across 14 search engines and AI models.

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/koushik018/omni-seo-studio)

🌐 **Live Landing Page**: [https://koushik018.github.io/omni-seo-studio/](https://koushik018.github.io/omni-seo-studio/)

---

## 🌟 Enterprise Feature Matrix

### 1. 14-Bot Multi-Agent Crawler & WAF Shield Simulator
Simultaneously audits the live HTTP response, latency, compression, and WAF firewall behaviors across:
- **Googlebot Desktop & Smartphone** (Google Search)
- **Microsoft Bingbot** (Bing & Copilot)
- **OpenAI GPTBot** (Foundational Model Training)
- **OpenAI SearchBot (OAI-SearchBot)** (ChatGPT Live Search & Citations)
- **ChatGPT-User Agent** (Active ChatGPT Web Browsing sessions)
- **Anthropic ClaudeBot** (Claude Model Training)
- **Anthropic Claude-Web Agent** (Live Claude Web Browsing)
- **PerplexityBot** (Perplexity AI Search & Citations)
- **ByteDance Bytespider** (Doubao & TikTok AI)
- **Common Crawl (CCBot)** (Open LLM Web Datasets)
- **Google-Extended** (Gemini & Vertex AI Training)
- **Applebot-Extended** (Apple Intelligence Foundation Models)
- **Standard Desktop Browser** (Chrome 131 with full JS comparison)

### 2. JavaScript & Static HTML AI Compliance (CSR vs SSR)
- **Client-Side Rendering (CSR) Trap Alert**: Detects if an empty `#root` or `#app` container delivers 0 text to AI crawlers.
- **Render-Blocking Scripts & Styles in `<head>`**: Identifies scripts without `defer` or `async` that halt HTML parsers.
- **Semantic `<noscript>` Quality Check**: Flags generic boilerplate ("Please enable JS") and auto-generates rich HTML fallbacks.
- **Side-by-Side Simulator**: Shows "What Chrome Sees (with JS)" vs "What GPTBot / ClaudeBot See (Raw HTML)".

### 3. Generative Engine Optimization (GEO) & RAG Readiness
- **`/llms.txt` and `/llms-full.txt` RFC Inspector**: Validates H1 title, summary blockquote, and section links.
- **Inverted Pyramid Lead Definition Check**: Evaluates if the primary definition or answer is front-loaded in the first 200 words for instant Perplexity/ChatGPT citation.
- **RAG Chunkability Score**: Verifies if content is structured into semantic sections between 150-450 words.
- **Named Fact & Entity Density Counter**: Audits statistical figures, percentages, dates, and proper nouns.

### 4. Technical, Speed & Security Signals
- **TTFB & Server Latency**: Real-time response speed grading (< 250ms optimal threshold).
- **HTTP Compression**: Brotli (`br`), Gzip, and Zstandard payload compression detection.
- **Security Headers**: HSTS, CSP, X-Content-Type-Options (`nosniff`), X-Frame-Options, Referrer-Policy.
- **Mixed Content**: Scans HTTPS pages for insecure HTTP asset calls.
- **Core Web Vitals CLS**: Detects images lacking explicit `width` & `height` attributes.

### 5. Content Quality & Over-Optimization Forensics
- **Title Tag Pixel Width Meter**: Approximates exact Google desktop SERP pixel width (~580px limit).
- **Meta Description Call-To-Action (CTA)**: Detects action-oriented conversion copy.
- **Headings Hierarchy Tree (H1-H6)**: Single H1 validation and skipped level detection (e.g. H1 -> H3).
- **Flesch Reading Ease**: Computes average sentence length, syllable count, and readability grade.
- **Keyword Stuffing / Over-Optimization Shield**: Flags repetitive phrase n-grams exceeding 3.5% density.
- **Generic Anchor Text Detector**: Flags links using generic words like "click here" or "read more".

### 6. Schema.org JSON-LD & Knowledge Graph
- Validates 15+ Schema types: `Organization`, `WebSite`, `Article`, `NewsArticle`, `FAQPage`, `Product`, `LocalBusiness`, `BreadcrumbList`, etc.
- Knowledge Graph verification: Checks for `sameAs` entity links to Wikipedia, LinkedIn, X, and GitHub.

### 7. 🎯 Target Keyword & Rank #1 Search Dominance Engine
- **Target Keyword Analysis**: Audits placement in `<title>` (frontloaded check), `<h1>`, `<meta description>`, lead 100-word definition, and URL slug.
- **Search Intent Classifier**: Classifies query intent as *Commercial Investigation*, *Informational Guide*, *Transactional*, or *Navigational*.
- **Pre-Generated Rank #1 Snippets**: 1-click copy optimized title, meta description, H1, and FAQ structured data snippet.

### 8. 🌐 Authority Directory Syndication & AI Citation Playbook
- **Where Websites Recommend & List Your Site**: Automated submission playbooks for high-authority directories (**GitHub Awesome Lists**, **ProductHunt**, **AlternativeTo**, **Slant.co**, **Dev.to**, and **G2**).
- **AI Recommendation Engine (AEO)**: Strategy for how Perplexity, ChatGPT Search, Claude, and Gemini cite external sources from community threads and directory roundups.
- **Knowledge Graph `sameAs` Entity Schema**: Pre-formatted JSON-LD graph tying brand profiles together.

### 9. 📁 Triple Input Modes & 1-Click 100/100 HTML Repair
- **Mode 1: Live Website URL** with concurrent 14-crawler probing.
- **Mode 2: Upload HTML File** (drag-and-drop `.html` files for instant offline audits).
- **Mode 3: Paste Raw HTML Code** for fast local iteration.
- **⚡ 100/100 Auto-Optimized HTML Generator**: 1-click downloads a completely repaired, production-ready `optimized-index.html` file with all missing meta, alt tags, script deferrals, semantic `<noscript>` blocks, and Schema JSON-LD.

### 10. 1-Click Code Generators & Executive Reports
- **AI `<noscript>` Fallback Generator**: Compiles semantic HTML with headings, summary, and links.
- **Script Deferral Optimizer**: Generates `<script defer>` tags for render-blocking assets.
- **`llms.txt` Standard Generator**: Exports RFC markdown file.
- **AI-Ready `robots.txt` Studio**: 4 presets (Hybrid AI Search, Open All, Strict Anti-Scraping, Custom).
- **Schema.org JSON-LD Builder**: Multi-type interactive builder.
- **Executive Markdown Report**: 1-click download of a full C-level audit report (`.md`).

---

## 🚀 Quick Start

```powershell
cd D:\omni-seo-studio
python run.py
```

Then visit:
👉 **`http://localhost:8000`**
