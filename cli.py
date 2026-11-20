#!/usr/bin/env python3
"""
OmniSEO Studio - Standalone CLI Runner
Audit any website URL or local HTML file directly from terminal.
"""

import sys
import os
import argparse
import asyncio
import json
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.analyzer import analyze_webpage
from app.crawler import crawl_all_bots
from app.robots_inspector import inspect_robots_and_llms
from app.schema_validator import extract_schemas_from_html
from app.generators import (
    generate_markdown_report,
    generate_auto_fixed_html,
    generate_claude_prompt,
    generate_deepseek_prompt,
    generate_3d_canvas_fallback
)


def format_score(score: int) -> str:
    if score >= 90:
        return f"\033[92m{score}/100 (Excellent)\033[0m"
    elif score >= 75:
        return f"\033[93m{score}/100 (Good)\033[0m"
    else:
        return f"\033[91m{score}/100 (Action Required)\033[0m"


async def run_audit(
    target: str,
    keyword: str = "",
    export_md: str = "",
    export_json: str = "",
    fix_html: str = "",
    claude_prompt: str = "",
    deepseek_prompt: str = "",
    canvas_fallback: str = ""
):
    print("\n" + "=" * 60)
    print("  🚀 OmniSEO Studio - Standalone CLI Audit Engine")
    print("=" * 60)
    print(f"[*] Target : {target}")
    if keyword:
        print(f"[*] Keyword: '{keyword}'")

    is_local = os.path.isfile(target) or target.endswith((".html", ".htm"))
    
    if is_local:
        print(f"[*] Reading local HTML file: {target} ...")
        try:
            with open(target, "r", encoding="utf-8", errors="replace") as f:
                primary_html = f.read()
        except Exception as e:
            print(f"[!] Error reading file: {e}")
            return 1

        primary_url = f"file:///{os.path.abspath(target).replace(os.sep, '/')}"
        primary_headers = {}
        primary_latency = 1.0
        robots_res = {"robots_txt": {"found": False, "status": 404}, "llms_txt": {"found": False, "status": 404}}
        schema_res = extract_schemas_from_html(primary_html)
        matrix = {}
    else:
        if not target.startswith(("http://", "https://")):
            target = "https://" + target
        print(f"[*] Auditing live URL: {target} ...")

        crawl_future = crawl_all_bots(target, None)
        robots_future = inspect_robots_and_llms(target)
        crawl_res, robots_res = await asyncio.gather(crawl_future, robots_future)

        primary_html = crawl_res.get("primary_html", "")
        primary_url = crawl_res.get("primary_url", target)
        primary_headers = crawl_res.get("primary_headers", {})
        primary_latency = crawl_res.get("primary_latency", 0.0)
        matrix = crawl_res.get("matrix", {})
        schema_res = extract_schemas_from_html(primary_html)

    print("[*] Running multi-dimensional ranking & crawler audits...")
    analysis = analyze_webpage(
        html_str=primary_html,
        target_url=primary_url,
        robots_data=robots_res,
        schema_data=schema_res,
        headers=primary_headers,
        latency_ms=primary_latency,
        target_keyword=keyword if keyword else None
    )

    scores = analysis.get("scores", {})

    print("\n" + "-" * 60)
    print("  📊 AUDIT SCORE SUMMARY")
    print("-" * 60)
    print(f"  Overall Score   : {format_score(scores.get('overall', 0))} — {scores.get('grade', '')}")
    print(f"  Traditional SEO : {format_score(scores.get('traditional', 0))}")
    print(f"  AI / GEO Score  : {format_score(scores.get('geo_ai', 0))}")
    print(f"  JS vs Static    : {format_score(scores.get('javascript', 0))}")
    print(f"  Speed & Security: {format_score(scores.get('technical', 0))}")
    print(f"  Content Quality : {format_score(scores.get('content', 0))}")
    print(f"  Structured Data : {format_score(scores.get('schema', 0))}")

    # Keyword analysis
    kw_audit = analysis.get("target_keyword_audit", {})
    if kw_audit and kw_audit.get("has_keyword"):
        print("\n" + "-" * 60)
        print(f"  🎯 TARGET KEYWORD ANALYSIS: '{kw_audit.get('target_keyword')}'")
        print("-" * 60)
        print(f"  Intent: {kw_audit.get('search_intent')} | Density: {kw_audit.get('density')}% ({kw_audit.get('occurrences')}x)")
        
        sim_searches = kw_audit.get("similar_searches", [])
        if sim_searches:
            print("\n  🔍 Similar / Long-Tail Searches ('People Also Search For'):")
            for s in sim_searches[:5]:
                print(f"    - {s}")

        paa = kw_audit.get("people_also_ask", [])
        if paa:
            print("\n  ❓ Top User Questions ('People Also Ask'):")
            for q in paa[:3]:
                print(f"    - Q: {q.get('question')}")

        lsi = kw_audit.get("lsi_terms", [])
        if lsi:
            print(f"\n  🏷️ Semantic LSI Entities: {', '.join(lsi[:6])}")

    # Critical issues
    crit = analysis.get("critical_issues", [])
    if crit:
        print("\n" + "-" * 60)
        print(f"  ⚠️ CRITICAL ISSUES ({len(crit)})")
        print("-" * 60)
        for issue in crit[:5]:
            print(f"  [{issue.get('category')}] {issue.get('title')}")
            print(f"    Fix: {issue.get('fix')}")

    # Full payload for generators
    full_data = {
        "success": True,
        "target_url": primary_url,
        "final_url": primary_url,
        "status_code": 200,
        "crawler_matrix": matrix,
        "robots_and_llms": robots_res,
        "schemas": schema_res,
        "analysis": analysis
    }

    # Export Markdown
    if export_md:
        md_content = generate_markdown_report(full_data)
        Path(export_md).write_text(md_content, encoding="utf-8")
        print(f"\n[✓] Executive Markdown report saved to: {export_md}")

    # Export JSON
    if export_json:
        Path(export_json).write_text(json.dumps(full_data, indent=2), encoding="utf-8")
        print(f"[✓] Raw audit JSON saved to: {export_json}")

    # Export 100/100 HTML
    if fix_html:
        fixed = generate_auto_fixed_html(primary_html, primary_url, keyword, analysis)
        Path(fix_html).write_text(fixed, encoding="utf-8")
        print(f"[✓] 100/100 Auto-Optimized HTML saved to: {fix_html}")

    # Export Claude Prompt
    if claude_prompt:
        cp = generate_claude_prompt(full_data)
        Path(claude_prompt).write_text(cp, encoding="utf-8")
        print(f"[✓] Claude 3.5/3.7 XML optimization prompt saved to: {claude_prompt}")

    # Export DeepSeek Prompt
    if deepseek_prompt:
        dp = generate_deepseek_prompt(full_data)
        Path(deepseek_prompt).write_text(dp, encoding="utf-8")
        print(f"[✓] DeepSeek R1 reasoning prompt saved to: {deepseek_prompt}")

    # Export 3D Canvas Fallback
    if canvas_fallback:
        meta_title = analysis.get("meta", {}).get("title", "")
        site_name = meta_title.split("-")[0].split("|")[0].strip() or "3D Web Application"
        snippet_3d = generate_3d_canvas_fallback(site_name, keyword or "interactive 3d web experience")
        Path(canvas_fallback).write_text(snippet_3d, encoding="utf-8")
        print(f"[✓] 3D Canvas SEO & Accessibility fallback saved to: {canvas_fallback}")

    print("\n" + "=" * 60)
    print("  Audit Complete! Run 'python run.py' for interactive web UI.")
    print("=" * 60 + "\n")
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="OmniSEO Studio CLI - Audit, optimize, and generate reports from terminal."
    )
    parser.add_argument("target", help="Website URL (e.g. https://github.com) or local HTML file path")
    parser.add_argument("-k", "--keyword", default="", help="Target keyword to optimize for (e.g. 'developer platform')")
    parser.add_argument("-e", "--export", default="", help="Path to save executive Markdown report (.md)")
    parser.add_argument("-j", "--json", default="", help="Path to save raw audit JSON (.json)")
    parser.add_argument("-f", "--fix-html", default="", help="Path to save 100/100 auto-fixed HTML file (.html)")
    parser.add_argument("--claude", default="", help="Path to save Claude 3.5/3.7 XML prompt file (.xml or .txt)")
    parser.add_argument("--deepseek", default="", help="Path to save DeepSeek R1 reasoning prompt file (.md or .txt)")
    parser.add_argument("--canvas-3d", default="", help="Path to save 3D Canvas fallback HTML snippet (.html)")

    args = parser.parse_args()
    asyncio.run(run_audit(
        target=args.target,
        keyword=args.keyword,
        export_md=args.export,
        export_json=args.json,
        fix_html=args.fix_html,
        claude_prompt=args.claude,
        deepseek_prompt=args.deepseek,
        canvas_fallback=args.canvas_3d
    ))


if __name__ == "__main__":
    main()
