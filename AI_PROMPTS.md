# 🤖 Inter-AI Prompting Architecture: Claude & DeepSeek Refactoring Engine

OmniSEO Studio includes a built-in **Inter-AI Code Generator**. It packages your website's exact audit diagnostics, keyword signals, and missing elements into specialized AI prompt wrappers tailored to each model's native reasoning architecture.

---

## 1. Claude (Anthropic XML Prompt Architecture)

Claude 3.5 Sonnet and Claude 3.7 excel when given structured XML tags. In OmniSEO Studio, click **"Claude Prompt"** or run:
```bash
python cli.py <url_or_file> --keyword "my keyword" --claude prompt_claude.xml
```

### Prompt Structure Sent to Claude:
```xml
<system_role>
You are an Elite Technical SEO Architect, Generative Engine Optimization (GEO) Engineer, and Senior Web Developer.
Your objective is to refactor the provided website code to achieve a 100/100 OmniSEO score, dominate Google Page 1 for the target keyword, and ensure full citation in AI engines (ChatGPT Search, Perplexity, Claude, Gemini).
</system_role>

<task>
Refactor and return the complete, production-ready, zero-regression HTML/CSS/JS code for this web application.
</task>

<context>
  <target_url>https://example.com</target_url>
  <target_keyword>developer platform</target_keyword>
  <current_overall_score>54/100 (Needs Optimization)</current_overall_score>
  <scores_breakdown>
    <traditional_seo>80/100</traditional_seo>
    <ai_geo>65/100</ai_geo>
    <javascript_compliance>80/100</javascript_compliance>
    <technical_speed>50/100</technical_speed>
    <structured_data>0/100</structured_data>
  </scores_breakdown>
</context>

<diagnosed_issues>
  <issue severity="critical">3D Canvas/WebGL Experience Detected Without Crawlable Semantic DOM</issue>
  <issue severity="high">Missing JSON-LD structured data schema</issue>
</diagnosed_issues>

<semantic_keyword_targets>
  <similar_queries_to_incorporate_in_h2_h3>
    <query>best developer platform</query>
    <query>developer platform tools</query>
  </similar_queries_to_incorporate_in_h2_h3>
  <lsi_entities_to_sprinkle_in_body_text>
    <entity>performance benchmarks</entity>
    <entity>api documentation</entity>
  </lsi_entities_to_sprinkle_in_body_text>
</semantic_keyword_targets>

<optimization_directives>
1. TITLE & H1: Front-load keyword in first 25 characters of <title> and match in <h1>.
2. AI DEFINITION: Direct definition in opening 100 words answering "What is [keyword]?".
3. 3D / CANVAS: Add .sr-only accessible fallback container and internal <canvas> DOM.
4. SCHEMA: Inject WebSite, Organization, and FAQPage JSON-LD.
5. SCRIPTS: Add 'defer' to render-blocking scripts in <head>.
</optimization_directives>
```

---

## 2. DeepSeek (DeepSeek R1 / V3 Chain-of-Thought Protocol)

DeepSeek R1 performs best when prompted with an algorithmic reasoning protocol (`<think>` process). In OmniSEO Studio, click **"DeepSeek Prompt"** or run:
```bash
python cli.py <url_or_file> --keyword "my keyword" --deepseek prompt_deepseek.md
```

### Prompt Structure Sent to DeepSeek:
```markdown
# DeepSeek R1 Reasoning Protocol: Autonomous SEO & Generative Optimization (GEO) Refactoring

You are DeepSeek R1 acting as a Principal Web Systems Engineer and Algorithmic Search Specialist.
Analyze the following technical audit diagnostic and refactor the target application's code to achieve flawless ranking and indexing performance.

## 1. Audit Context & Diagnostics
- Target URL: https://example.com
- Primary Search Keyword: "developer platform"
- Current Overall Health: 54/100 [Action Required]
- Traditional Search Engine Score: 80/100
- AI Crawler & GEO Score: 65/100
- JavaScript / DOM Rendering Score: 80/100
- Technical & Security Score: 50/100
- Schema / Entity Score: 0/100

## 2. Identified Bottlenecks & Audit Violations
- [CRITICAL] 3D Canvas/WebGL Experience Detected Without Crawlable Semantic DOM
- [HIGH] Missing JSON-LD structured data schema

## 3. High-Priority Search Queries & Entities
- Related Search Queries to Target: best developer platform, developer platform tools
- Required Semantic LSI Entities: performance benchmarks, integration guide

## 4. Chain-of-Thought Reasoning Protocol (<think>)
Before outputting code, analyze in detail:
1. How to structure the DOM tree so Googlebot and non-JS AI crawlers (GPTBot, ClaudeBot, PerplexityBot) parse topical authority in the critical render path.
2. If 3D canvases, Three.js, or WebGL are present, how to implement a dual-layer accessibility & SEO fallback (<canvas> internal DOM + visually-hidden semantic region) that satisfies Google search guidelines without causing layout shift.
3. How to mathematically optimize keyword density to stay in the sweet spot (1.0% - 2.2%) while incorporating the long-tail queries as H2 headings.
4. The exact JSON-LD @graph syntax for WebSite, Organization, and FAQPage.

## 5. Required Deliverable
Output your full step-by-step reasoning followed by the complete, production-grade refactored HTML code. Ensure the code is 100% self-contained and ready to deploy.
```

---

## How to Use With Your AI Assistant

1. Run an audit in **OmniSEO Studio** on your site (or local HTML file).
2. Click **"Claude Prompt"** or **"DeepSeek Prompt"** in the top action bar.
3. Click **"Copy Prompt"**.
4. Paste it into [Claude](https://claude.ai) or [DeepSeek](https://chat.deepseek.com).
5. The AI returns the fully refactored, production-ready code with a 100/100 score guarantee!
