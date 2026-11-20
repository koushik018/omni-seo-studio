import asyncio
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, HttpUrl

from app.crawler import crawl_all_bots, CRAWLER_PROFILES
from app.robots_inspector import inspect_robots_and_llms
from app.schema_validator import extract_schemas_from_html
from app.analyzer import analyze_webpage
from app.generators import (
    generate_llms_txt,
    generate_robots_txt,
    generate_jsonld_snippet,
    generate_meta_snippet,
    generate_noscript_block,
    generate_defer_script_fix,
    generate_markdown_report,
    generate_auto_fixed_html,
    generate_syndication_playbook,
    generate_claude_prompt,
    generate_deepseek_prompt,
    generate_3d_canvas_fallback
)

app = FastAPI(
    title="OmniSEO & AI Studio API",
    description="The Generative Engine & Search Crawler Audit & Optimization Suite",
    version="2.0.0"
)

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files directory
STATIC_DIR = Path(__file__).resolve().parent / "static"
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

class AuditRequest(BaseModel):
    url: str
    selected_bots: Optional[List[str]] = None
    target_keyword: Optional[str] = None

class UploadAuditRequest(BaseModel):
    html_code: str
    target_url: Optional[str] = "https://example.com"
    target_keyword: Optional[str] = None
    site_title: Optional[str] = None

class AutoFixHtmlRequest(BaseModel):
    html_code: str
    target_url: Optional[str] = "https://example.com"
    target_keyword: Optional[str] = None
    site_title: Optional[str] = None
    description: Optional[str] = None

class SyndicationPlaybookRequest(BaseModel):
    site_title: str
    target_keyword: str
    url: Optional[str] = "https://example.com"
    description: Optional[str] = ""

class LLMsGenerateRequest(BaseModel):
    site_title: str
    summary: str
    sections: Optional[List[Dict[str, Any]]] = None

class RobotsGenerateRequest(BaseModel):
    preset: str = "ai_search_friendly"
    sitemap_url: Optional[str] = ""

class SchemaGenerateRequest(BaseModel):
    schema_type: str
    data: Dict[str, Any]

class MetaGenerateRequest(BaseModel):
    title: str
    description: str
    canonical: Optional[str] = ""
    og_image: Optional[str] = ""
    site_name: Optional[str] = ""

class NoScriptGenerateRequest(BaseModel):
    title: str
    description: str
    headings: Optional[List[str]] = None
    links: Optional[List[Dict[str, str]]] = None

class DeferGenerateRequest(BaseModel):
    scripts: List[str]

class ReportGenerateRequest(BaseModel):
    audit_data: Dict[str, Any]

class CanvasFallbackRequest(BaseModel):
    site_title: str
    target_keyword: str
    features: Optional[List[str]] = None

# Clean favicon handler so browser tabs never 404 or hang
FAVICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><rect width="100" height="100" rx="25" fill="#6366f1"/><path d="M50 20 L80 80 L60 80 L50 55 L40 80 L20 80 Z" fill="#ffffff"/></svg>"""

@app.get("/favicon.ico")
async def get_favicon():
    return Response(content=FAVICON_SVG, media_type="image/svg+xml")

@app.get("/")
async def serve_index():
    index_file = STATIC_DIR / "index.html"
    if not index_file.exists():
        raise HTTPException(status_code=404, detail="Frontend index.html not found")
    return FileResponse(str(index_file))

@app.get("/api/bots")
async def get_crawler_profiles():
    """Return list of supported crawlers and AI bots."""
    return {"bots": CRAWLER_PROFILES}

@app.post("/api/audit")
async def run_full_audit(req: AuditRequest):
    """Run full enterprise multi-crawler, AI/GEO, Technical, JavaScript compliance, Schema, and SEO audit."""
    target_url = req.url.strip()
    if not target_url.startswith(("http://", "https://")):
        target_url = "https://" + target_url

    try:
        # Run crawler and robots/llms inspection concurrently with fast timeouts
        crawl_future = crawl_all_bots(target_url, req.selected_bots)
        robots_future = inspect_robots_and_llms(target_url)
        
        crawl_res, robots_res = await asyncio.gather(crawl_future, robots_future)
        
        primary_html = crawl_res.get("primary_html", "")
        primary_headers = crawl_res.get("primary_headers", {})
        primary_latency = crawl_res.get("primary_latency", 0)
        
        # Schema validation
        schema_res = extract_schemas_from_html(primary_html)
        
        # Comprehensive page analysis including JavaScript, Performance & Security headers
        analysis_res = analyze_webpage(
            html_str=primary_html,
            target_url=crawl_res.get("primary_url", target_url),
            robots_data=robots_res,
            schema_data=schema_res,
            headers=primary_headers,
            latency_ms=primary_latency,
            target_keyword=req.target_keyword
        )
        
        return {
            "success": True,
            "target_url": target_url,
            "final_url": crawl_res.get("primary_url", target_url),
            "status_code": crawl_res.get("primary_status", 200),
            "crawler_matrix": crawl_res.get("matrix", {}),
            "robots_and_llms": robots_res,
            "schemas": schema_res,
            "analysis": analysis_res
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": f"Audit failed: {str(e)}"}
        )

@app.post("/api/audit-upload")
async def run_upload_audit(req: UploadAuditRequest):
    """
    Audits raw uploaded HTML code or pasted code directly without requiring a live public server.
    Validates SEO, GEO/AI readability, JavaScript compliance, target keyword dominance, and schemas.
    """
    raw_html = req.html_code.strip()
    if not raw_html:
        raise HTTPException(status_code=400, detail="HTML content cannot be empty")
        
    target_url = req.target_url.strip() if req.target_url else "https://example.com"
    if not target_url.startswith(("http://", "https://")):
        target_url = "https://" + target_url

    try:
        # Schema validation
        schema_res = extract_schemas_from_html(raw_html)
        
        # Synthetic robots/llms status for offline/uploaded HTML
        synthetic_robots = {
            "robots_txt": {"exists": True, "status": 200, "content": "User-agent: *\nAllow: /\nUser-agent: GPTBot\nAllow: /\nUser-agent: PerplexityBot\nAllow: /"},
            "llms_txt": {"exists": True, "status": 200, "content": "# " + (req.site_title or "Uploaded Project") + "\n> Offline Audit Mode\n"},
            "sitemap_xml": {"exists": True, "status": 200, "urls_count": 1}
        }
        
        # Comprehensive analysis
        analysis_res = analyze_webpage(
            html_str=raw_html,
            target_url=target_url,
            robots_data=synthetic_robots,
            schema_data=schema_res,
            headers={
                "strict-transport-security": "max-age=31536000; includeSubDomains",
                "x-content-type-options": "nosniff",
                "content-encoding": "br"
            },
            latency_ms=45.0,
            target_keyword=req.target_keyword
        )
        
        # Synthetic crawler matrix for uploaded HTML
        matrix = {
            "googlebot_desktop": {"name": "Googlebot Desktop", "allowed": True, "status_code": 200, "content_length": len(raw_html), "response_time_ms": 45.0, "cdn": "Local File / Code Upload", "content_encoding": "utf-8", "is_ai_bot": False},
            "gptbot": {"name": "OpenAI GPTBot", "allowed": True, "status_code": 200, "content_length": len(raw_html), "response_time_ms": 45.0, "cdn": "Local File / Code Upload", "content_encoding": "utf-8", "is_ai_bot": True},
            "claudebot": {"name": "Anthropic ClaudeBot", "allowed": True, "status_code": 200, "content_length": len(raw_html), "response_time_ms": 45.0, "cdn": "Local File / Code Upload", "content_encoding": "utf-8", "is_ai_bot": True},
            "perplexitybot": {"name": "PerplexityBot", "allowed": True, "status_code": 200, "content_length": len(raw_html), "response_time_ms": 45.0, "cdn": "Local File / Code Upload", "content_encoding": "utf-8", "is_ai_bot": True},
            "standard_browser": {"name": "Standard Chrome Desktop", "allowed": True, "status_code": 200, "content_length": len(raw_html), "response_time_ms": 45.0, "cdn": "Local File / Code Upload", "content_encoding": "utf-8", "is_ai_bot": False}
        }
        
        return {
            "success": True,
            "target_url": target_url,
            "final_url": target_url,
            "status_code": 200,
            "is_uploaded_code": True,
            "crawler_matrix": matrix,
            "robots_and_llms": synthetic_robots,
            "schemas": schema_res,
            "analysis": analysis_res
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": f"Upload audit failed: {str(e)}"}
        )

@app.post("/api/generate/auto-fixed-html")
async def generate_auto_fixed_html_endpoint(req: AutoFixHtmlRequest):
    content = generate_auto_fixed_html(
        raw_html=req.html_code,
        target_url=req.target_url or "https://example.com",
        target_keyword=req.target_keyword
    )
    return {"content": content}

@app.post("/api/generate/syndication-playbook")
async def generate_syndication_playbook_endpoint(req: SyndicationPlaybookRequest):
    playbook = generate_syndication_playbook(
        target_keyword=req.target_keyword,
        site_title=req.site_title,
        url=req.url or "https://example.com",
        description=req.description or ""
    )
    return playbook

@app.post("/api/generate/llms")
async def generate_llms_endpoint(req: LLMsGenerateRequest):
    content = generate_llms_txt(
        site_title=req.site_title,
        summary=req.summary,
        sections=req.sections
    )
    return {"content": content}

@app.post("/api/generate/robots")
async def generate_robots_endpoint(req: RobotsGenerateRequest):
    content = generate_robots_txt(
        preset=req.preset,
        sitemap_url=req.sitemap_url or ""
    )
    return {"content": content}

@app.post("/api/generate/schema")
async def generate_schema_endpoint(req: SchemaGenerateRequest):
    content = generate_jsonld_snippet(
        schema_type=req.schema_type,
        data=req.data
    )
    return {"content": content}

@app.post("/api/generate/meta")
async def generate_meta_endpoint(req: MetaGenerateRequest):
    content = generate_meta_snippet(data=req.model_dump())
    return {"content": content}

@app.post("/api/generate/noscript")
async def generate_noscript_endpoint(req: NoScriptGenerateRequest):
    content = generate_noscript_block(
        title=req.title,
        description=req.description,
        headings=req.headings,
        links=req.links
    )
    return {"content": content}

@app.post("/api/generate/defer")
async def generate_defer_endpoint(req: DeferGenerateRequest):
    content = generate_defer_script_fix(scripts=req.scripts)
    return {"content": content}

@app.post("/api/generate/markdown-report")
async def generate_markdown_report_endpoint(req: ReportGenerateRequest):
    content = generate_markdown_report(req.audit_data)
    return {"content": content}

@app.post("/api/generate/claude-prompt")
async def generate_claude_prompt_endpoint(req: ReportGenerateRequest):
    content = generate_claude_prompt(req.audit_data)
    return {"content": content}

@app.post("/api/generate/deepseek-prompt")
async def generate_deepseek_prompt_endpoint(req: ReportGenerateRequest):
    content = generate_deepseek_prompt(req.audit_data)
    return {"content": content}

@app.post("/api/generate/3d-canvas-fallback")
async def generate_3d_canvas_fallback_endpoint(req: CanvasFallbackRequest):
    content = generate_3d_canvas_fallback(req.site_title, req.target_keyword, req.features)
    return {"content": content}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
