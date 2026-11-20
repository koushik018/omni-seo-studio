import time
import asyncio
from typing import Dict, Any, List, Optional
import httpx

# Comprehensive registry of 14 modern search engines, AI scrapers, and agents
CRAWLER_PROFILES = {
    "standard_browser": {
        "name": "Standard Chrome Desktop",
        "category": "browser",
        "vendor": "Google Chrome",
        "description": "Standard user desktop browser with full client execution",
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    },
    "googlebot_desktop": {
        "name": "Googlebot (Desktop)",
        "category": "search",
        "vendor": "Google",
        "description": "Primary Google search indexer for desktop sites",
        "user_agent": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
    },
    "googlebot_mobile": {
        "name": "Googlebot (Smartphone)",
        "category": "search",
        "vendor": "Google",
        "description": "Google mobile-first indexing crawler",
        "user_agent": "Mozilla/5.0 (Linux; Android 6.0.1; Nexus 5X Build/MMB29P) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.86 Mobile Safari/537.36 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
    },
    "bingbot": {
        "name": "Bingbot",
        "category": "search",
        "vendor": "Microsoft",
        "description": "Microsoft Bing and Copilot search crawler",
        "user_agent": "Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)"
    },
    "gptbot": {
        "name": "OpenAI GPTBot",
        "category": "ai",
        "vendor": "OpenAI",
        "description": "OpenAI foundational model training & content scraper",
        "user_agent": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; GPTBot/1.2; +https://openai.com/gptbot)"
    },
    "oai_searchbot": {
        "name": "OpenAI SearchBot",
        "category": "ai",
        "vendor": "OpenAI",
        "description": "Crawler specifically powering live ChatGPT search & citations",
        "user_agent": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; OAI-SearchBot/1.0; +https://openai.com/searchbot)"
    },
    "chatgpt_user": {
        "name": "ChatGPT-User",
        "category": "ai",
        "vendor": "OpenAI",
        "description": "Direct user browsing agent from active ChatGPT sessions",
        "user_agent": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; ChatGPT-User/1.0; +https://openai.com/bot)"
    },
    "claudebot": {
        "name": "Anthropic ClaudeBot",
        "category": "ai",
        "vendor": "Anthropic",
        "description": "Anthropic training & data crawler for Claude models",
        "user_agent": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; ClaudeBot/1.0; +https://www.anthropic.com/claudebot)"
    },
    "claude_web": {
        "name": "Claude-Web Agent",
        "category": "ai",
        "vendor": "Anthropic",
        "description": "Live browsing crawler when Claude users request a URL",
        "user_agent": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; Claude-Web/1.0; +https://www.anthropic.com/claudebot)"
    },
    "perplexitybot": {
        "name": "PerplexityBot",
        "category": "ai",
        "vendor": "Perplexity AI",
        "description": "Crawler powering live answers & citations on Perplexity",
        "user_agent": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; PerplexityBot/1.0; +https://perplexity.ai/perplexitybot)"
    },
    "bytespider": {
        "name": "ByteDance Bytespider",
        "category": "ai",
        "vendor": "ByteDance",
        "description": "ByteDance crawler used for Doubao, TikTok, and AI training",
        "user_agent": "Mozilla/5.0 (compatible; Bytespider; https://zhanzhang.toutiao.com/)"
    },
    "ccbot": {
        "name": "Common Crawl (CCBot)",
        "category": "ai",
        "vendor": "Common Crawl",
        "description": "Open web archive dataset utilized heavily in LLM training",
        "user_agent": "CCBot/2.0 (https://commoncrawl.org/faq/)"
    },
    "google_extended": {
        "name": "Google-Extended",
        "category": "ai",
        "vendor": "Google",
        "description": "Crawler used by Google to train Gemini and Vertex AI models",
        "user_agent": "Mozilla/5.0 (compatible; Google-Extended/1.0; +https://developers.google.com/search/docs/crawling-indexing/google-extended)"
    },
    "applebot_extended": {
        "name": "Applebot-Extended",
        "category": "ai",
        "vendor": "Apple",
        "description": "Crawler used to train Apple Intelligence foundational models",
        "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15 (Applebot-Extended/0.1)"
    }
}

async def fetch_single_bot(url: str, bot_key: str, profile: Dict[str, str], timeout: float = 4.5) -> Dict[str, Any]:
    """Fetch URL simulating a specific bot User-Agent with high-speed async HTTP."""
    headers = {
        "User-Agent": profile["user_agent"],
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
    }
    
    start_time = time.perf_counter()
    try:
        async with httpx.AsyncClient(follow_redirects=True, verify=False, timeout=timeout) as client:
            resp = await client.get(url, headers=headers)
            duration_ms = round((time.perf_counter() - start_time) * 1000, 1)
            
            # Inspect response headers
            resp_headers = {k.lower(): v for k, v in resp.headers.items()}
            content_encoding = resp_headers.get("content-encoding", "none")
            server = resp_headers.get("server", "")
            x_robots_tag = resp_headers.get("x-robots-tag")
            cache_control = resp_headers.get("cache-control", "")
            
            # Detect CDN from headers
            cdn = "Direct / Unknown"
            if "cf-ray" in resp_headers or "cloudflare" in server.lower():
                cdn = "Cloudflare CDN"
            elif "x-amz-cf-id" in resp_headers or "cloudfront" in server.lower():
                cdn = "Amazon CloudFront"
            elif "fastly-debug-digest" in resp_headers or "fastly" in server.lower():
                cdn = "Fastly CDN"
            elif "x-vercel-id" in resp_headers:
                cdn = "Vercel Edge Network"
            elif "x-nf-request-id" in resp_headers:
                cdn = "Netlify Edge"
            elif "akamai" in server.lower() or "x-akamai-transformed" in resp_headers:
                cdn = "Akamai CDN"
            elif server:
                cdn = server
                
            # Detect bot blocking / Cloudflare / CAPTCHA challenge in body
            content_lower = resp.text[:4000].lower() if resp.text else ""
            is_blocked = resp.status_code in [403, 401, 429, 503] or any(
                indicator in content_lower for indicator in [
                    "cf-browser-verification", "attention required! | cloudflare",
                    "just a moment...", "security check to access", "ddos-guard",
                    "checking if the site connection is secure", "access denied",
                    "challenge-platform", "cf-turnstile"
                ]
            )
            
            block_reason = None
            if is_blocked:
                if resp.status_code == 403:
                    block_reason = "HTTP 403 Forbidden (Bot blocked or WAF active)"
                elif resp.status_code == 429:
                    block_reason = "HTTP 429 Rate Limited / Throttled"
                elif "cloudflare" in content_lower or "just a moment" in content_lower:
                    block_reason = "Cloudflare WAF / Bot Management challenge active"
                else:
                    block_reason = f"Access Blocked (Status {resp.status_code})"
            
            return {
                "bot_key": bot_key,
                "name": profile["name"],
                "category": profile["category"],
                "vendor": profile.get("vendor", "Standard"),
                "status_code": resp.status_code,
                "response_time_ms": duration_ms,
                "content_length": len(resp.content),
                "is_blocked": is_blocked,
                "block_reason": block_reason,
                "content_type": resp_headers.get("content-type", ""),
                "content_encoding": content_encoding,
                "x_robots_tag": x_robots_tag,
                "server": server,
                "cdn": cdn,
                "cache_control": cache_control,
                "headers": dict(resp_headers),
                "html": resp.text if (resp.status_code == 200 and not is_blocked) else "",
                "final_url": str(resp.url),
                "error": None
            }
    except Exception as e:
        duration_ms = round((time.perf_counter() - start_time) * 1000, 1)
        err_str = str(e) or "Timeout or connection dropped"
        return {
            "bot_key": bot_key,
            "name": profile["name"],
            "category": profile["category"],
            "vendor": profile.get("vendor", "Standard"),
            "status_code": 0,
            "response_time_ms": duration_ms,
            "content_length": 0,
            "is_blocked": True,
            "block_reason": f"Connection Timed Out: {err_str[:60]}",
            "content_type": "",
            "content_encoding": "none",
            "x_robots_tag": None,
            "server": "",
            "cdn": "Unknown",
            "cache_control": "",
            "headers": {},
            "html": "",
            "final_url": url,
            "error": err_str
        }

async def crawl_all_bots(url: str, selected_bots: Optional[List[str]] = None) -> Dict[str, Any]:
    """Crawl a URL using multiple bot user-agents simultaneously with fast timeouts."""
    if not selected_bots:
        selected_bots = list(CRAWLER_PROFILES.keys())
    
    tasks = []
    for bot_key in selected_bots:
        if bot_key in CRAWLER_PROFILES:
            tasks.append(fetch_single_bot(url, bot_key, CRAWLER_PROFILES[bot_key]))
            
    results = await asyncio.gather(*tasks)
    
    matrix = {}
    primary_html = ""
    primary_status = 200
    primary_url = url
    primary_headers = {}
    primary_latency = 0
    
    for r in results:
        matrix[r["bot_key"]] = r
        if r["bot_key"] == "standard_browser" and r["html"]:
            primary_html = r["html"]
            primary_status = r["status_code"]
            primary_url = r["final_url"]
            primary_headers = r.get("headers", {})
            primary_latency = r.get("response_time_ms", 0)
            
    # Fallback to any working bot's HTML
    if not primary_html:
        for r in results:
            if r["html"]:
                primary_html = r["html"]
                primary_status = r["status_code"]
                primary_url = r["final_url"]
                primary_headers = r.get("headers", {})
                primary_latency = r.get("response_time_ms", 0)
                break
                
    return {
        "url": url,
        "primary_url": primary_url,
        "primary_status": primary_status,
        "primary_html": primary_html,
        "primary_headers": primary_headers,
        "primary_latency": primary_latency,
        "matrix": matrix
    }
