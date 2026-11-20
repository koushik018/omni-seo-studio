import urllib.parse
import asyncio
from typing import Dict, Any, List, Optional
import httpx
import re

AI_BOT_LIST = [
    {"id": "GPTBot", "name": "OpenAI GPTBot", "purpose": "Model Training"},
    {"id": "OAI-SearchBot", "name": "OpenAI SearchBot", "purpose": "ChatGPT Live Search"},
    {"id": "ChatGPT-User", "name": "ChatGPT User Agent", "purpose": "ChatGPT Web Browsing"},
    {"id": "ClaudeBot", "name": "Anthropic ClaudeBot", "purpose": "Model Training & Indexing"},
    {"id": "PerplexityBot", "name": "PerplexityBot", "purpose": "Perplexity AI Search"},
    {"id": "Google-Extended", "name": "Google Extended", "purpose": "Gemini & Vertex AI Training"},
    {"id": "Bytespider", "name": "ByteDance Bytespider", "purpose": "Doubao & TikTok AI"},
    {"id": "CCBot", "name": "Common Crawl", "purpose": "Open LLM Training Datasets"},
    {"id": "Applebot-Extended", "name": "Applebot Extended", "purpose": "Apple Intelligence Training"}
]

SEARCH_BOT_LIST = [
    {"id": "*", "name": "Default Wildcard (*)", "purpose": "All Unspecified Crawlers"},
    {"id": "Googlebot", "name": "Googlebot", "purpose": "Google Search Index"},
    {"id": "bingbot", "name": "Bingbot", "purpose": "Bing & Copilot Index"},
    {"id": "DuckDuckBot", "name": "DuckDuckBot", "purpose": "DuckDuckGo Index"},
    {"id": "Yandex", "name": "YandexBot", "purpose": "Yandex Search Index"}
]

def parse_robots_txt_content(content: str) -> Dict[str, Any]:
    """Parse robots.txt text content into agent-specific directives."""
    lines = content.splitlines()
    rules: Dict[str, Dict[str, List[str]]] = {}
    sitemaps = []
    current_agents = []
    
    for raw_line in lines:
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
            
        if ":" in line:
            field, val = line.split(":", 1)
            field = field.strip().lower()
            val = val.strip()
            
            if field == "user-agent":
                agent = val
                current_agents = [agent]
                if agent not in rules:
                    rules[agent] = {"disallow": [], "allow": []}
            elif field == "disallow" and current_agents:
                for agent in current_agents:
                    if agent not in rules:
                        rules[agent] = {"disallow": [], "allow": []}
                    rules[agent]["disallow"].append(val)
            elif field == "allow" and current_agents:
                for agent in current_agents:
                    if agent not in rules:
                        rules[agent] = {"disallow": [], "allow": []}
                    rules[agent]["allow"].append(val)
            elif field == "sitemap":
                if val not in sitemaps:
                    sitemaps.append(val)
                    
    # Evaluate permissions for target bots
    bot_analysis = []
    
    # Check AI Bots
    for bot in AI_BOT_LIST:
        bot_id = bot["id"]
        status = "Allowed (Inherited)"
        explicit_rule = False
        
        # Exact match (case-insensitive)
        matched_key = next((k for k in rules if k.lower() == bot_id.lower()), None)
        if matched_key:
            explicit_rule = True
            disallows = rules[matched_key]["disallow"]
            allows = rules[matched_key]["allow"]
            if "/" in disallows and "/" not in allows:
                status = "Blocked (Explicit)"
            elif any(d for d in disallows if d in ["/", "/*"]):
                status = "Blocked (Explicit)"
            else:
                status = "Allowed (Explicit)"
        elif "*" in rules:
            disallows = rules["*"]["disallow"]
            allows = rules["*"]["allow"]
            if "/" in disallows and "/" not in allows:
                status = "Blocked (via wildcard *)"
            else:
                status = "Allowed (via wildcard *)"
                
        bot_analysis.append({
            **bot,
            "category": "ai",
            "status": status,
            "explicit": explicit_rule,
            "disallows": rules.get(matched_key or "", {}).get("disallow", []),
            "allows": rules.get(matched_key or "", {}).get("allow", [])
        })
        
    # Check Search Bots
    for bot in SEARCH_BOT_LIST:
        bot_id = bot["id"]
        status = "Allowed (Default)"
        explicit_rule = False
        
        matched_key = next((k for k in rules if k.lower() == bot_id.lower()), None)
        if matched_key:
            explicit_rule = True
            disallows = rules[matched_key]["disallow"]
            allows = rules[matched_key]["allow"]
            if "/" in disallows and "/" not in allows:
                status = "Blocked (Explicit)"
            else:
                status = "Allowed (Explicit)"
        elif "*" in rules and bot_id != "*":
            disallows = rules["*"]["disallow"]
            allows = rules["*"]["allow"]
            if "/" in disallows and "/" not in allows:
                status = "Blocked (via wildcard *)"
            else:
                status = "Allowed (via wildcard *)"
                
        bot_analysis.append({
            **bot,
            "category": "search",
            "status": status,
            "explicit": explicit_rule,
            "disallows": rules.get(matched_key or "", {}).get("disallow", []),
            "allows": rules.get(matched_key or "", {}).get("allow", [])
        })
        
    return {
        "raw_content": content,
        "rules": rules,
        "sitemaps": sitemaps,
        "bot_permissions": bot_analysis
    }

async def inspect_robots_and_llms(target_url: str) -> Dict[str, Any]:
    """Inspect robots.txt, llms.txt, llms-full.txt, and sitemap.xml for target domain concurrently."""
    parsed = urllib.parse.urlparse(target_url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"
    
    robots_url = f"{base_url}/robots.txt"
    llms_url = f"{base_url}/llms.txt"
    llms_full_url = f"{base_url}/llms-full.txt"
    sitemap_url = f"{base_url}/sitemap.xml"
    
    headers = {"User-Agent": "Mozilla/5.0 (compatible; OmniSEOBot/1.0; +https://omni-seo.local)"}
    
    result = {
        "base_url": base_url,
        "robots_txt": {
            "url": robots_url,
            "exists": False,
            "status_code": 0,
            "raw": "",
            "analysis": None
        },
        "llms_txt": {
            "url": llms_url,
            "exists": False,
            "status_code": 0,
            "raw": "",
            "score": 0,
            "has_h1": False,
            "has_blockquote": False,
            "has_sections": False,
            "issues": []
        },
        "llms_full_txt": {
            "url": llms_full_url,
            "exists": False,
            "status_code": 0,
        },
        "sitemap_xml": {
            "url": sitemap_url,
            "exists": False,
            "status_code": 0,
            "count_urls": 0,
            "is_sitemap_index": False
        }
    }
    
    async with httpx.AsyncClient(verify=False, follow_redirects=True, timeout=4.0) as client:
        async def fetch_robots():
            try:
                r = await client.get(robots_url, headers=headers)
                result["robots_txt"]["status_code"] = r.status_code
                if r.status_code == 200 and r.text and "html" not in r.headers.get("content-type", "").lower():
                    result["robots_txt"]["exists"] = True
                    result["robots_txt"]["raw"] = r.text
                    result["robots_txt"]["analysis"] = parse_robots_txt_content(r.text)
            except Exception:
                pass

        async def fetch_llms():
            try:
                r = await client.get(llms_url, headers=headers)
                result["llms_txt"]["status_code"] = r.status_code
                if r.status_code == 200 and r.text and not ("<!doctype html" in r.text.lower() or "<html" in r.text.lower()):
                    result["llms_txt"]["exists"] = True
                    content = r.text
                    result["llms_txt"]["raw"] = content
                    
                    has_h1 = bool(re.search(r"^#\s+[^\n]+", content, re.MULTILINE))
                    has_bq = bool(re.search(r"^>\s+[^\n]+", content, re.MULTILINE))
                    has_sections = bool(re.search(r"^##\s+[^\n]+", content, re.MULTILINE))
                    
                    issues = []
                    score = 30
                    if has_h1: score += 25
                    else: issues.append("Missing primary project title (H1: `# Project Name`)")
                        
                    if has_bq: score += 25
                    else: issues.append("Missing summary blockquote (`> A fast, modern tool for...`)")
                        
                    if has_sections: score += 20
                    else: issues.append("Missing markdown section links (`## Documentation`, `## Guides`)")
                        
                    result["llms_txt"]["score"] = score
                    result["llms_txt"]["has_h1"] = has_h1
                    result["llms_txt"]["has_blockquote"] = has_bq
                    result["llms_txt"]["has_sections"] = has_sections
                    result["llms_txt"]["issues"] = issues
                else:
                    result["llms_txt"]["issues"] = ["File /llms.txt does not exist or returned HTML"]
            except Exception:
                result["llms_txt"]["issues"] = ["Could not connect to /llms.txt"]

        async def fetch_llms_full():
            try:
                r = await client.get(llms_full_url, headers=headers)
                result["llms_full_txt"]["status_code"] = r.status_code
                if r.status_code == 200 and r.text and not ("<!doctype html" in r.text.lower()):
                    result["llms_full_txt"]["exists"] = True
            except Exception:
                pass

        async def fetch_sitemap():
            try:
                r = await client.get(sitemap_url, headers=headers)
                result["sitemap_xml"]["status_code"] = r.status_code
                if r.status_code == 200 and ("xml" in r.headers.get("content-type", "") or "<urlset" in r.text or "<sitemapindex" in r.text):
                    result["sitemap_xml"]["exists"] = True
                    if "<sitemapindex" in r.text:
                        result["sitemap_xml"]["is_sitemap_index"] = True
                        result["sitemap_xml"]["count_urls"] = len(re.findall(r"<sitemap>", r.text))
                    else:
                        result["sitemap_xml"]["count_urls"] = len(re.findall(r"<url>", r.text))
            except Exception:
                pass

        # Run all 4 probes concurrently
        await asyncio.gather(fetch_robots(), fetch_llms(), fetch_llms_full(), fetch_sitemap())

    return result
