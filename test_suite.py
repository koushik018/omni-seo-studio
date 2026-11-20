import asyncio
from app.analyzer import analyze_webpage, estimate_pixel_width, calculate_reading_ease, detect_over_optimization
from app.schema_validator import extract_schemas_from_html
from app.generators import (
    generate_llms_txt,
    generate_robots_txt,
    generate_jsonld_snippet,
    generate_meta_snippet,
    generate_noscript_block,
    generate_defer_script_fix,
    generate_markdown_report
)
from app.crawler import CRAWLER_PROFILES

sample_html = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>OmniSEO Enterprise - The Ultimate Search and AI Optimization Engine</title>
  <meta name="description" content="Discover the most advanced SEO and Generative Engine Optimization audit platform for Googlebot, GPTBot, and AI crawlers.">
  <link rel="canonical" href="https://example.com/test">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <script src="/js/blocking-bundle.js"></script>
  <script defer src="/js/deferred-bundle.js"></script>
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "Organization",
    "name": "OmniSEO Inc",
    "url": "https://example.com"
  }
  </script>
</head>
<body>
  <h1>OmniSEO System Overview</h1>
  <h2>Enterprise Capabilities for Search & AI</h2>
  <p>OmniSEO is a comprehensive platform designed to audit web pages for Googlebot and modern AI crawlers. It inspects both search engines and generative models.</p>
  <h3>Key Features and Performance</h3>
  <p>Our platform delivers multi-crawler simulation across 14 distinct user-agents, ensuring complete visibility across Google, OpenAI, Anthropic, and Perplexity.</p>
  <ul>
    <li>Multi-crawler simulation</li>
    <li>llms.txt validation</li>
    <li>Schema.org JSON-LD generation</li>
  </ul>
  <img src="/logo.png" alt="Company Logo" width="200" height="60">
  <noscript>
    <p>Please enable JavaScript to view interactive features. Here is our core content.</p>
  </noscript>
</body>
</html>"""

def run_tests():
    print("1. Testing Crawler Profiles...")
    assert len(CRAWLER_PROFILES) >= 14, "Should have 14 crawler profiles"
    assert "gptbot" in CRAWLER_PROFILES
    assert "oai_searchbot" in CRAWLER_PROFILES
    assert "perplexitybot" in CRAWLER_PROFILES
    assert "claude_web" in CRAWLER_PROFILES
    print(f" -> {len(CRAWLER_PROFILES)} crawlers verified!")

    print("2. Testing Pixel Width & Readability Math...")
    px = estimate_pixel_width("OmniSEO Enterprise - The Ultimate Search")
    assert px > 200 and px < 580
    words = "This is an advanced test sentence designed to verify the reading ease calculation score.".split()
    ease = calculate_reading_ease(words, 1)
    assert ease["score"] > 0
    print(f" -> Pixel width: {px}px, Readability: {ease['score']} ({ease['grade']})")

    print("3. Testing Over-Optimization Detector...")
    spammy_words = ("best seo tool " * 35 + "random words here and there for testing " * 15).split()
    assert len(spammy_words) > 100
    flagged = detect_over_optimization(spammy_words)
    assert len(flagged) > 0
    print(f" -> Correctly flagged keyword stuffing: {flagged[0]['phrase']} ({flagged[0]['density']}%)")

    print("4. Testing Schema Validator...")
    schemas = extract_schemas_from_html(sample_html)
    assert "Organization" in schemas["types_found"]
    print(" -> Schemas found:", schemas["types_found"])

    print("5. Testing Comprehensive Analyzer...")
    headers = {
        "strict-transport-security": "max-age=31536000",
        "x-content-type-options": "nosniff",
        "content-encoding": "br"
    }
    analysis = analyze_webpage(sample_html, "https://example.com/test", schema_data=schemas, headers=headers, latency_ms=180.0)
    scores = analysis["scores"]
    print(" -> Scores breakdown:", scores)
    assert scores["overall"] >= 75, "Enterprise score should be high for compliant page"
    assert scores["technical"] >= 90
    assert analysis["meta"]["title_pixel_width"] > 0
    assert analysis["technical_audit"]["hsts"] is True
    assert analysis["technical_audit"]["content_encoding"] == "br"

    print("6. Testing Executive Markdown Report Generator...")
    mock_audit = {
        "final_url": "https://example.com/test",
        "status_code": 200,
        "analysis": analysis
    }
    md_report = generate_markdown_report(mock_audit)
    assert "# OmniSEO & AI Executive Audit Report" in md_report
    assert "Executive Score Breakdown" in md_report
    print(" -> Markdown executive report generated successfully!")

    print("7. Testing Target Keyword & Search Dominance Analyzer...")
    kw_analysis = analyze_webpage(
        sample_html,
        "https://example.com/test",
        schema_data=schemas,
        headers=headers,
        target_keyword="OmniSEO Enterprise"
    )
    kw_audit = kw_analysis.get("target_keyword_audit", {})
    assert kw_audit.get("has_keyword") is True
    assert "checks" in kw_audit
    assert "auto_snippets" in kw_audit
    assert kw_audit["score"] >= 50, f"Expected score >= 50 but got {kw_audit['score']}"
    print(f" -> Target keyword analyzed: Score {kw_audit['score']}/100, Intent: {kw_audit['search_intent']}")

    print("8. Testing 100/100 Auto-Optimized HTML Generator...")
    from app.generators import generate_auto_fixed_html, generate_syndication_playbook
    bare_html = "<html><head><script src='/app.js'></script></head><body><h1>My Product</h1><img src='/shot.png'></body></html>"
    fixed_html = generate_auto_fixed_html(bare_html, "https://myproduct.com", target_keyword="best dev platform")
    assert "<meta charset=\"UTF-8\">" in fixed_html
    assert "defer" in fixed_html
    assert "<noscript>" in fixed_html
    assert "application/ld+json" in fixed_html
    assert "alt=" in fixed_html
    print(" -> Auto-fixed HTML successfully injected all missing meta, defer, noscript, alt tags, and JSON-LD schemas!")

    print("9. Testing Authority Syndication & Directory Citation Playbook...")
    playbook = generate_syndication_playbook("developer tools", "MyDevTool", "https://mydevtool.com", "Next-gen dev tools for teams")
    assert len(playbook["directories"]) >= 5
    assert "awesome_list_snippet" in playbook
    assert "community_citations" in playbook
    assert "schema_sameas" in playbook
    print(f" -> Playbook generated with {len(playbook['directories'])} high-authority directories and AI citation prompts!")

    print("10. Testing FastAPI REST Endpoints Integration...")
    import httpx
    from app.main import app

    async def run_api_checks():
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            # Favicon
            r_fav = await client.get("/favicon.ico")
            assert r_fav.status_code == 200

            # Upload / Raw HTML audit
            r_up = await client.post("/api/audit-upload", json={
                "html_code": sample_html,
                "target_url": "https://example.com/test",
                "target_keyword": "OmniSEO Enterprise"
            })
            assert r_up.status_code == 200
            assert r_up.json()["success"] is True

            # Auto-Fixed HTML
            r_fix = await client.post("/api/generate/auto-fixed-html", json={
                "html_code": sample_html,
                "target_keyword": "OmniSEO Enterprise"
            })
            assert r_fix.status_code == 200
            assert "<noscript>" in r_fix.json()["content"]

            # Claude Prompt Generator
            r_claude = await client.post("/api/generate/claude-prompt", json={"audit_data": mock_audit})
            assert r_claude.status_code == 200
            assert "<system_role>" in r_claude.json()["content"]

            # DeepSeek Prompt Generator
            r_deepseek = await client.post("/api/generate/deepseek-prompt", json={"audit_data": mock_audit})
            assert r_deepseek.status_code == 200
            assert "DeepSeek R1 Reasoning Protocol" in r_deepseek.json()["content"]

            # 3D Canvas Fallback Generator
            r_3d = await client.post("/api/generate/3d-canvas-fallback", json={
                "site_title": "OmniSEO 3D",
                "target_keyword": "interactive webgl visualization"
            })
            assert r_3d.status_code == 200
            assert "sr-only-3d" in r_3d.json()["content"]

    asyncio.run(run_api_checks())
    print(" -> All API endpoints (/favicon.ico, /api/audit-upload, /api/generate/*) verified!")

    print("\n✅ ALL ENTERPRISE TEST SUITE CHECKS PASSED WITH 100% SUCCESS!")

if __name__ == "__main__":
    run_tests()
