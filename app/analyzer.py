import re
import math
import urllib.parse
from typing import Dict, Any, List, Optional
import lxml.html

def estimate_pixel_width(text: str) -> int:
    """Approximate Google SERP title pixel width based on proportional font metrics."""
    wide_chars = set("WMwGQm@%#&")
    narrow_chars = set("ijlItf!|:;,. '")
    width = 0
    for char in text:
        if char in wide_chars:
            width += 14
        elif char in narrow_chars:
            width += 4
        elif char.isupper():
            width += 11
        else:
            width += 8
    return width

def extract_clean_text_and_sentences(tree):
    """Extract clean text preserving natural block boundaries (p, h1-h6, li, tr) for realistic sentence counts."""
    # Append newline after block elements to prevent words running together
    for block in tree.xpath('//p | //h1 | //h2 | //h3 | //h4 | //h5 | //h6 | //li | //tr | //div | //br | //section | //article | //blockquote | //header | //footer | //dt | //dd'):
        if block.tail:
            block.tail = '\n' + block.tail
        else:
            block.tail = '\n'
            
    raw_text = tree.text_content()
    lines = [re.sub(r'[ \t]+', ' ', line).strip() for line in raw_text.splitlines()]
    lines = [line for line in lines if line]
    
    cleaned_text = " ".join(lines)
    words = cleaned_text.split()
    
    # Split sentences by punctuation (.!?) OR block line breaks
    sentences = []
    for line in lines:
        parts = re.split(r'[.!?]+', line)
        for p in parts:
            p_strip = p.strip()
            if len(p_strip.split()) >= 2:
                sentences.append(p_strip)
                
    if not sentences and words:
        sentences = [cleaned_text]
        
    return cleaned_text, words, sentences

def calculate_reading_ease(words: List[str], sentences_count: int) -> Dict[str, Any]:
    """Calculate Flesch Reading Ease estimate and grade level with block-boundary awareness."""
    word_count = max(len(words), 1)
    sentences_count = max(sentences_count, 1)
    
    syllable_count = 0
    for w in words:
        w_lower = w.lower()
        count = len(re.findall(r'[aeiouy]+', w_lower))
        if w_lower.endswith('e') and not w_lower.endswith('le') and count > 1:
            count -= 1
        syllable_count += max(1, count)
        
    avg_words_per_sentence = word_count / sentences_count
    avg_syllables_per_word = syllable_count / word_count
    
    score = 206.835 - (1.015 * avg_words_per_sentence) - (84.6 * avg_syllables_per_word)
    score = round(max(0, min(100, score)), 1)
    
    if score >= 80: grade = "Very Easy (Casual reader)"
    elif score >= 60: grade = "Standard / Accessible"
    elif score >= 40: grade = "Moderately Complex (Technical)"
    else: grade = "Difficult / Academic"
    
    return {
        "score": score,
        "grade": grade,
        "avg_words_per_sentence": round(avg_words_per_sentence, 1),
        "total_syllables": syllable_count,
        "sentences_count": sentences_count
    }

def detect_over_optimization(words: List[str]) -> List[Dict[str, Any]]:
    """Detect repetitive n-grams / keyword stuffing that triggers search engine spam filters."""
    if len(words) < 100:
        return []
        
    clean_tokens = [re.sub(r'[^a-zA-Z0-9]', '', w.lower()) for w in words]
    clean_tokens = [w for w in clean_tokens if len(w) > 3]
    
    phrases = {}
    total_phrases = 0
    for i in range(len(clean_tokens) - 1):
        p2 = f"{clean_tokens[i]} {clean_tokens[i+1]}"
        phrases[p2] = phrases.get(p2, 0) + 1
        total_phrases += 1
        
    flagged = []
    for phrase, count in phrases.items():
        density = (count / max(total_phrases, 1)) * 100
        if count >= 4 and density > 3.0:
            flagged.append({
                "phrase": phrase,
                "count": count,
                "density": round(density, 1)
            })
            
    return sorted(flagged, key=lambda x: x["density"], reverse=True)[:5]

def analyze_target_keyword(
    keyword: str,
    title: str,
    description: str,
    h1_list: List[str],
    h2_list: List[str],
    words: List[str],
    cleaned_text: str,
    target_url: str
) -> Dict[str, Any]:
    """Audit whether the page is optimized to rank #1 when users search for a specific target keyword."""
    kw = keyword.strip().lower()
    if not kw:
        return {"has_keyword": False, "score": 0, "checks": [], "suggestions": []}
        
    kw_words = kw.split()
    title_lower = title.lower()
    desc_lower = description.lower()
    cleaned_lower = cleaned_text.lower()
    url_lower = target_url.lower()
    
    # 1. Exact & Semantic Token Matches
    in_title = kw in title_lower or (len(kw_words) > 1 and all(w in title_lower for w in kw_words if len(w) > 2))
    in_title_front = title_lower.startswith(kw) or (in_title and title_lower.find(kw_words[0]) < 25)
    in_desc = kw in desc_lower or (len(kw_words) > 1 and all(w in desc_lower for w in kw_words if len(w) > 2))
    in_h1 = any(kw in h.lower() or (len(kw_words) > 1 and all(w in h.lower() for w in kw_words if len(w) > 2)) for h in h1_list)
    in_h2_count = sum(1 for h in h2_list if kw in h.lower() or (len(kw_words) > 1 and all(w in h.lower() for w in kw_words if len(w) > 2)))
    
    # First 100 words check (Crucial for AI citations & SERP snippets)
    first_100_text = " ".join(words[:100]).lower()
    in_first_100 = kw in first_100_text or (len(kw_words) > 1 and all(w in first_100_text for w in kw_words if len(w) > 2))
    
    # URL check
    kw_slug = re.sub(r'[^a-z0-9]+', '-', kw)
    in_url = kw_slug in url_lower or any(w in url_lower for w in kw_words if len(w) > 3)
    
    # Keyword Density
    kw_count = cleaned_lower.count(kw)
    total_words = max(len(words), 1)
    density = round(((kw_count * len(kw_words)) / total_words) * 100, 2)
    
    # Scoring
    score = 0
    checks = []
    suggestions = []
    
    # Check Title
    if in_title:
        score += 25
        if in_title_front:
            score += 5
            checks.append({"name": "Target keyword in Title tag", "status": "pass", "detail": "Front-loaded in title (Optimal for Google & CTR)"})
        else:
            checks.append({"name": "Target keyword in Title tag", "status": "pass", "detail": "Present in title"})
    else:
        suggestions.append(f"Add '{keyword}' into the first 30 characters of your <title> tag.")
        checks.append({"name": "Target keyword in Title tag", "status": "fail", "detail": f"Missing from title: '{title[:50]}...'"})

    # Check H1
    if in_h1:
        score += 25
        checks.append({"name": "Target keyword in primary <h1>", "status": "pass", "detail": "Matches main page topic"})
    else:
        suggestions.append(f"Include '{keyword}' inside your primary <h1> heading.")
        checks.append({"name": "Target keyword in primary <h1>", "status": "fail", "detail": "Missing from H1"})

    # Check Lead Paragraph
    if in_first_100:
        score += 15
        checks.append({"name": "Target keyword in first 100 words", "status": "pass", "detail": "Front-loaded in lead answer paragraph (Optimal for AI search citation)"})
    else:
        suggestions.append(f"Introduce '{keyword}' directly in your first sentence to allow ChatGPT and Perplexity to quote your definition.")
        checks.append({"name": "Target keyword in first 100 words", "status": "fail", "detail": "Not found in opening sentences"})

    # Check Meta Description
    if in_desc:
        score += 15
        checks.append({"name": "Target keyword in Meta Description", "status": "pass", "detail": "Bolded in search snippets"})
    else:
        suggestions.append(f"Add '{keyword}' into your meta description to increase click-through rate when searched.")
        checks.append({"name": "Target keyword in Meta Description", "status": "fail", "detail": "Missing from meta description"})

    # Check Subheadings
    if in_h2_count > 0:
        score += 10
        checks.append({"name": "Target keyword in <h2> subheadings", "status": "pass", "detail": f"Present in {in_h2_count} subheadings"})
    else:
        suggestions.append(f"Add a subheading such as 'Why Choose {keyword.title()}?' or 'How {keyword.title()} Works'.")
        checks.append({"name": "Target keyword in <h2> subheadings", "status": "fail", "detail": "None of your H2s use this keyword"})

    # Check Density
    if 0.8 <= density <= 3.0:
        score += 10
        checks.append({"name": "Keyword Density", "status": "pass", "detail": f"Optimal density: {density}% ({kw_count} occurrences)"})
    elif density > 3.0:
        checks.append({"name": "Keyword Density", "status": "warning", "detail": f"High density: {density}% (risk of keyword stuffing penalty)"})
    else:
        checks.append({"name": "Keyword Density", "status": "warning", "detail": f"Low density: {density}% ({kw_count} occurrences)"})

    # Search Intent classification
    intent = "Informational"
    if any(w in kw for w in ["buy", "price", "pricing", "discount", "order", "cost", "hire"]):
        intent = "Transactional"
    elif any(w in kw for w in ["best", "top", "review", "comparison", "vs", "alternative"]):
        intent = "Commercial Investigation"
    elif any(w in kw for w in ["how to", "what is", "why", "tutorial", "guide", "learn"]):
        intent = "Informational Guide"

    # Pre-generate Instant Ranking Code snippets
    clean_kw = keyword.strip()
    kw_t = clean_kw.title()
    generated_title = f"{kw_t} — Complete Guide & Top Solution"
    generated_h1 = f"The Definitive Solution for {kw_t}"
    generated_desc = f"Looking for the best {clean_kw}? Discover features, guides, and expert recommendations designed to give you the highest performance."

    # Generate Similar Searches ("People Also Search For")
    similar_searches = [
        f"best {clean_kw}",
        f"{clean_kw} tools",
        f"{clean_kw} open source",
        f"{clean_kw} free trial",
        f"{clean_kw} alternatives",
        f"{clean_kw} for developers",
        f"{clean_kw} comparison guide",
        f"how to choose a {clean_kw}"
    ]

    # Generate Question-Based Searches ("People Also Ask")
    people_also_ask = [
        {
            "question": f"What is a {clean_kw} and what is it used for?",
            "answer_template": f"A {clean_kw} is a platform designed to streamline performance, provide integrated tools, and automate core workflows."
        },
        {
            "question": f"How do I choose the best {clean_kw} in 2026?",
            "answer_template": f"Evaluate speed, crawlability, static fallback support, community recommendations, and pricing."
        },
        {
            "question": f"What are the top alternatives to popular {clean_kw} solutions?",
            "answer_template": f"Modern open-source and high-speed tools offer lower latency, better developer control, and comprehensive search indexing."
        },
        {
            "question": f"Is {clean_kw} worth it for small teams?",
            "answer_template": f"Yes, using a dedicated {clean_kw} reduces setup complexity and accelerates product delivery."
        }
    ]

    # Semantic LSI Vocabulary (Terms Google & AI look for on an authoritative page)
    lsi_terms = [
        "performance benchmarks",
        "integration guide",
        "security compliance",
        "api documentation",
        "developer workflow",
        "open source",
        "scalability & speed",
        "community review"
    ]

    # 7-Step Definitive Optimization Checklist
    optimization_steps = [
        {"step": 1, "title": "Front-load in <title>", "rule": "Place keyword in the first 25 characters; keep title under 580px width."},
        {"step": 2, "title": "Exact match in <h1>", "rule": "Use exact keyword once in your primary H1 heading at top of body."},
        {"step": 3, "title": "Direct definition in opening 100 words", "rule": "Answer 'What is [Keyword]?' in your very first sentence so Google AI Overviews and ChatGPT quote you directly."},
        {"step": 4, "title": "Include in Meta Description with Action CTA", "rule": "Between 120-160 characters with strong call to action ('Discover', 'Explore', 'Get started')."},
        {"step": 5, "title": "Use Similar Searches as <h2> subheadings", "rule": "Add subheadings like 'Why Choose [Keyword]?' and 'Key Features of [Keyword]'."},
        {"step": 6, "title": "Maintain 0.8% - 2.5% Keyword Density", "rule": "Repeat naturally throughout paragraphs; avoid keyword stuffing above 3.5%."},
        {"step": 7, "title": "Inject FAQ Schema & Static HTML Fallback", "rule": "Use FAQPage JSON-LD answering common questions, and ensure <noscript> contains plain text."}
    ]

    return {
        "has_keyword": True,
        "target_keyword": keyword,
        "score": min(100, score),
        "search_intent": intent,
        "density": density,
        "occurrences": kw_count,
        "checks": checks,
        "suggestions": suggestions,
        "similar_searches": similar_searches,
        "people_also_ask": people_also_ask,
        "lsi_terms": lsi_terms,
        "optimization_steps": optimization_steps,
        "auto_snippets": {
            "title": generated_title,
            "h1": generated_h1,
            "description": generated_desc
        }
    }

def analyze_webpage(
    html_str: str,
    target_url: str,
    robots_data: Optional[Dict[str, Any]] = None,
    schema_data: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    latency_ms: float = 0.0,
    target_keyword: Optional[str] = None
) -> Dict[str, Any]:
    """Perform an enterprise-grade multi-layer SEO, GEO, Technical, Content, and Security audit."""
    if not html_str:
        return {
            "error": "Empty or unparseable HTML content",
            "scores": {"overall": 0, "traditional": 0, "geo_ai": 0, "javascript": 0, "technical": 0, "content": 0, "schema": 0, "social": 0},
            "issues": [{"severity": "critical", "category": "General", "title": "No HTML content received", "fix": "Ensure the server responds with 200 OK and valid HTML."}],
            "warnings": [],
            "passes": [],
            "javascript_audit": {},
            "technical_audit": {},
            "content_audit": {},
            "target_keyword_audit": {}
        }

    try:
        tree = lxml.html.fromstring(html_str)
    except Exception as e:
        return {
            "error": f"Failed to parse HTML: {str(e)}",
            "scores": {"overall": 0, "traditional": 0, "geo_ai": 0, "javascript": 0, "technical": 0, "content": 0, "schema": 0, "social": 0},
            "issues": [{"severity": "critical", "category": "General", "title": "Corrupt or malformed HTML", "fix": "Verify that your server outputs valid HTML."}],
            "warnings": [],
            "passes": [],
            "javascript_audit": {},
            "technical_audit": {},
            "content_audit": {},
            "target_keyword_audit": {}
        }

    parsed_target = urllib.parse.urlparse(target_url)
    is_https = parsed_target.scheme == "https"
    resp_headers = headers or {}
    
    issues: List[Dict[str, str]] = []
    warnings: List[Dict[str, str]] = []
    passes: List[Dict[str, str]] = []

    # -------------------------------------------------------------
    # 1. TECHNICAL, SPEED & SECURITY SIGNALS
    # -------------------------------------------------------------
    tech_score = 100
    
    if not is_https:
        tech_score -= 30
        issues.append({
            "severity": "critical",
            "category": "Security",
            "title": "Insecure Connection (HTTP instead of HTTPS)",
            "fix": "Migrate to HTTPS with a valid TLS certificate. Google penalizes non-HTTPS websites in SERPs."
        })
    else:
        passes.append({"category": "Security", "title": "Secure HTTPS Connection Active", "detail": "Valid TLS encryption"})

    http_resources = tree.xpath('//img[starts-with(@src, "http://")] | //script[starts-with(@src, "http://")] | //link[starts-with(@href, "http://")]')
    if is_https and len(http_resources) > 0:
        tech_score -= 15
        warnings.append({
            "severity": "high",
            "category": "Security",
            "title": f"{len(http_resources)} Mixed Content Resources Detected",
            "fix": "Update all asset URLs (scripts, stylesheets, images) to use HTTPS or protocol-relative paths to prevent browser security blocks."
        })

    hsts = resp_headers.get("strict-transport-security")
    csp = resp_headers.get("content-security-policy")
    nosniff = resp_headers.get("x-content-type-options")
    frame_options = resp_headers.get("x-frame-options")
    referrer_policy = resp_headers.get("referrer-policy")

    if not hsts and is_https:
        tech_score -= 8
        warnings.append({"severity": "medium", "category": "Security", "title": "Missing HSTS Header (Strict-Transport-Security)", "fix": "Add 'Strict-Transport-Security: max-age=31536000; includeSubDomains' to enforce HTTPS."})
    else:
        passes.append({"category": "Security", "title": "HSTS Active", "detail": hsts or "Enforced"})

    if not nosniff:
        tech_score -= 5
        warnings.append({"severity": "low", "category": "Security", "title": "Missing X-Content-Type-Options: nosniff", "fix": "Add 'X-Content-Type-Options: nosniff' to prevent MIME-sniffing attacks."})
    else:
        passes.append({"category": "Security", "title": "MIME Sniffing Protected (nosniff)", "detail": "Active"})

    content_encoding = resp_headers.get("content-encoding", "none").lower()
    has_compression = any(c in content_encoding for c in ["gzip", "br", "zstd", "deflate"])
    if not has_compression:
        tech_score -= 15
        warnings.append({
            "severity": "medium",
            "category": "Performance",
            "title": "HTTP Compression Not Enabled",
            "fix": "Enable Brotli ('br') or Gzip compression on your web server / CDN to reduce payload transfer size by 60-80%."
        })
    else:
        passes.append({"category": "Performance", "title": f"HTTP Compression Enabled ({content_encoding})", "detail": content_encoding})

    if latency_ms > 0:
        if latency_ms > 800:
            tech_score -= 15
            warnings.append({
                "severity": "high",
                "category": "Performance",
                "title": f"Slow Server Response Time (TTFB: {latency_ms}ms)",
                "fix": "Google recommends a TTFB below 200ms. Consider database caching, edge CDN rendering, or server scaling."
            })
        elif latency_ms <= 300:
            passes.append({"category": "Performance", "title": f"Fast Server Response Time ({latency_ms}ms)", "detail": "Under 300ms optimal threshold"})

    charset_nodes = tree.xpath('//meta[@charset]/@charset | //meta[contains(@http-equiv, "Content-Type")]/@content')
    has_utf8 = any("utf-8" in str(c).lower() for c in charset_nodes) or "utf-8" in resp_headers.get("content-type", "").lower()
    if not has_utf8:
        warnings.append({"severity": "low", "category": "Technical", "title": "Missing or non-UTF-8 character encoding", "fix": "Include `<meta charset=\"UTF-8\">` inside `<head>` to ensure text decodes properly."})
    else:
        passes.append({"category": "Technical", "title": "UTF-8 Charset Configured", "detail": "UTF-8"})

    viewport_nodes = tree.xpath('//meta[@name="viewport"]/@content')
    viewport = viewport_nodes[0].strip() if viewport_nodes else ""
    if not viewport:
        tech_score -= 20
        issues.append({"severity": "high", "category": "Mobile", "title": "Missing Mobile Viewport Meta Tag", "fix": "Add `<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">` for mobile indexing."})
    else:
        passes.append({"category": "Mobile", "title": "Mobile Viewport Defined", "detail": viewport})

    tech_score = max(0, min(100, tech_score))

    # -------------------------------------------------------------
    # 2. JAVASCRIPT & STATIC HTML AI COMPLIANCE ENGINE
    # -------------------------------------------------------------
    head_scripts = tree.xpath('//head//script')
    all_scripts = tree.xpath('//script')
    
    render_blocking_scripts = []
    for s in head_scripts:
        src = s.get('src')
        is_async = s.get('async') is not None
        is_defer = s.get('defer') is not None
        script_type = (s.get('type') or '').lower()
        is_module = script_type == 'module'
        if src and not (is_async or is_defer or is_module):
            render_blocking_scripts.append(src)

    head_styles = tree.xpath('//head//link[@rel="stylesheet"]')
    render_blocking_styles = [s.get('href') for s in head_styles if s.get('href') and not s.get('media')]

    noscript_nodes = tree.xpath('//noscript')
    has_noscript = len(noscript_nodes) > 0
    noscript_text = ""
    noscript_is_boilerplate = False
    
    if has_noscript:
        noscript_text = " ".join([n.text_content().strip() for n in noscript_nodes]).strip()
        lower_ns = noscript_text.lower()
        if any(bp in lower_ns for bp in ["you need to enable javascript", "requires javascript", "enable javascript to run this app"]):
            noscript_is_boilerplate = True

    spa_containers = tree.xpath('//*[@id="root" or @id="app" or @id="__next" or @id="__nuxt"]')
    has_spa_container = len(spa_containers) > 0
    
    all_elements = tree.xpath('//*')
    total_dom_elements = len(all_elements)
    
    max_depth = 0
    for el in all_elements:
        depth = len(list(el.iterancestors()))
        if depth > max_depth:
            max_depth = depth

    # -------------------------------------------------------------
    # 3. ON-PAGE META & HEADINGS FORENSICS
    # -------------------------------------------------------------
    title_nodes = tree.xpath("//title/text()")
    title = title_nodes[0].strip() if title_nodes else ""
    title_len = len(title)
    title_pixel_width = estimate_pixel_width(title)
    
    if not title:
        issues.append({"severity": "critical", "category": "Meta", "title": "Missing <title> tag", "fix": "Add a descriptive <title> tag between 40-60 characters."})
    elif title_len < 30:
        warnings.append({"severity": "medium", "category": "Meta", "title": f"Title tag is short ({title_len} chars)", "fix": "Expand the title to 40-60 characters with relevant brand and core topic terms."})
    elif title_pixel_width > 580:
        warnings.append({"severity": "medium", "category": "Meta", "title": f"Title pixel width exceeds SERP display (~{title_pixel_width}px / 580px limit)", "fix": "Google cuts off titles exceeding ~580px width. Shorten slightly to avoid '...' truncation."})
    else:
        passes.append({"category": "Meta", "title": f"Optimal <title> length ({title_len} chars, ~{title_pixel_width}px)", "detail": title})

    desc_nodes = tree.xpath('//meta[@name="description" or @name="Description"]/@content')
    description = desc_nodes[0].strip() if desc_nodes else ""
    desc_len = len(description)
    
    has_cta = any(word in description.lower() for word in ["get", "discover", "learn", "explore", "find", "shop", "buy", "start", "join", "read", "see"])
    
    if not description:
        issues.append({"severity": "high", "category": "Meta", "title": "Missing meta description", "fix": "Add a compelling meta description between 120-160 characters to optimize SERP CTR."})
    elif desc_len < 80:
        warnings.append({"severity": "low", "category": "Meta", "title": f"Meta description is short ({desc_len} chars)", "fix": "Aim for 120-160 characters to maximize SERP real estate."})
    elif desc_len > 165:
        warnings.append({"severity": "medium", "category": "Meta", "title": f"Meta description exceeds optimal length ({desc_len} chars)", "fix": "Descriptions longer than 160 characters get truncated in search snippets."})
    else:
        passes.append({"category": "Meta", "title": f"Optimal meta description length ({desc_len} chars)", "detail": description})

    canonical_nodes = tree.xpath('//link[@rel="canonical"]/@href')
    canonical = canonical_nodes[0].strip() if canonical_nodes else ""
    if not canonical:
        warnings.append({"severity": "medium", "category": "Indexing", "title": "Missing canonical URL tag", "fix": "Add `<link rel=\"canonical\" href=\"...\">` to declare the authoritative URL."})
    else:
        passes.append({"category": "Indexing", "title": "Canonical URL tag declared", "detail": canonical})

    robots_meta_nodes = tree.xpath('//meta[@name="robots" or @name="googlebot"]/@content')
    robots_meta = robots_meta_nodes[0].strip().lower() if robots_meta_nodes else ""
    if "noindex" in robots_meta:
        issues.append({"severity": "critical", "category": "Indexing", "title": "Page contains 'noindex' directive", "fix": "Search engines and AI bots are instructed NOT to index this page."})
    else:
        passes.append({"category": "Indexing", "title": "Indexable (no 'noindex' restrictions found)", "detail": robots_meta or "Default index, follow"})

    html_lang_nodes = tree.xpath('//html/@lang')
    html_lang = html_lang_nodes[0].strip() if html_lang_nodes else ""
    if not html_lang:
        warnings.append({"severity": "low", "category": "Accessibility & SEO", "title": "Missing 'lang' attribute on <html>", "fix": "Specify language (e.g. `<html lang=\"en\">`) to assist search engines and screen readers."})
    else:
        passes.append({"category": "Accessibility & SEO", "title": f"HTML language defined ('{html_lang}')", "detail": html_lang})

    h1_list = [h.text_content().strip() for h in tree.xpath('//h1') if h.text_content().strip()]
    h2_list = [h.text_content().strip() for h in tree.xpath('//h2') if h.text_content().strip()]
    h3_list = [h.text_content().strip() for h in tree.xpath('//h3') if h.text_content().strip()]
    h4_list = [h.text_content().strip() for h in tree.xpath('//h4') if h.text_content().strip()]
    h5_list = [h.text_content().strip() for h in tree.xpath('//h5') if h.text_content().strip()]
    h6_list = [h.text_content().strip() for h in tree.xpath('//h6') if h.text_content().strip()]

    if len(h1_list) == 0:
        issues.append({"severity": "high", "category": "Content Structure", "title": "Missing <h1> heading", "fix": "Ensure the page has exactly one prominent <h1> describing the primary topic."})
    elif len(h1_list) > 1:
        warnings.append({"severity": "medium", "category": "Content Structure", "title": f"Multiple <h1> headings found ({len(h1_list)})", "fix": "Best practice is a single <h1> heading per page, using <h2> for sub-topics."})
    else:
        passes.append({"category": "Content Structure", "title": "Single clear <h1> heading found", "detail": h1_list[0]})

    has_skipped_levels = False
    if len(h1_list) > 0 and len(h2_list) == 0 and len(h3_list) > 0:
        has_skipped_levels = True
        warnings.append({"severity": "medium", "category": "Content Structure", "title": "Heading level skipped (H1 straight to H3 without H2)", "fix": "Maintain hierarchical order (H1 -> H2 -> H3) to preserve semantic document flow."})

    # -------------------------------------------------------------
    # 4. CONTENT QUALITY, READABILITY & TEXT METRICS (REFINED)
    # -------------------------------------------------------------
    for bad_tag in tree.xpath('//script | //style | //svg | //noscript'):
        bad_tag.drop_tree()
        
    cleaned_text, words, sentences = extract_clean_text_and_sentences(tree)
    word_count = len(words)
    char_count = len(cleaned_text)
    
    html_bytes = len(html_str)
    text_bytes = len(cleaned_text.encode('utf-8'))
    text_ratio = round((text_bytes / max(html_bytes, 1)) * 100, 1)

    reading_metrics = calculate_reading_ease(words, len(sentences))
    over_opt_phrases = detect_over_optimization(words)

    table_count = len(tree.xpath('//table'))
    ul_ol_count = len(tree.xpath('//ul | //ol'))
    li_count = len(tree.xpath('//li'))
    faq_question_count = len(tree.xpath('//details | //dt')) + sum(1 for h in h2_list + h3_list if "?" in h)

    # -------------------------------------------------------------
    # 5. JAVASCRIPT DEPENDENCY EVALUATION (AI RISK)
    # -------------------------------------------------------------
    is_spa_dependent = has_spa_container and word_count < 100 and len(all_scripts) > 0
    
    js_score = 100
    if is_spa_dependent:
        js_score -= 50
        issues.append({
            "severity": "critical",
            "category": "JavaScript & Static HTML",
            "title": "Client-Side Rendered (CSR) App Detected — Content Invisible to AI Crawlers",
            "fix": "OpenAI GPTBot, ClaudeBot, and PerplexityBot DO NOT execute JavaScript. They see an empty blank container (<div id='root'>). Implement Server-Side Rendering (SSR) or provide semantic static HTML fallback so AI can check and cite your page."
        })
    elif len(render_blocking_scripts) > 0:
        js_score -= min(30, len(render_blocking_scripts) * 10)
        warnings.append({
            "severity": "medium",
            "category": "JavaScript & Static HTML",
            "title": f"{len(render_blocking_scripts)} Render-Blocking Script(s) in <head>",
            "fix": "Scripts loaded in <head> without 'defer' or 'async' delay crawler parsing. Add 'defer' to scripts to unblock HTML parsing."
        })
    else:
        passes.append({
            "category": "JavaScript & Static HTML",
            "title": "Clean Script Delivery (No render-blocking scripts in <head>)",
            "detail": "HTML parsing is unblocked"
        })

    if not has_noscript:
        if len(all_scripts) >= 3:
            warnings.append({
                "severity": "medium",
                "category": "JavaScript & Static HTML",
                "title": "No <noscript> Static Fallback Detected",
                "fix": "Add a semantic <noscript> block containing your core H1, business summary, and key navigation links so non-JS AI scrapers can always check your content."
            })
    else:
        if noscript_is_boilerplate:
            warnings.append({
                "severity": "low",
                "category": "JavaScript & Static HTML",
                "title": "<noscript> tag contains generic boilerplate",
                "fix": "Replace 'You need to enable JavaScript' with actual semantic HTML (H1, paragraph description, and links) so AI crawlers get real data."
            })
        else:
            passes.append({
                "category": "JavaScript & Static HTML",
                "title": "Rich <noscript> Static Content Provided",
                "detail": f"{len(noscript_text)} characters of static fallback"
            })

    if total_dom_elements > 1500:
        js_score -= 10
        warnings.append({"severity": "medium", "category": "Performance", "title": f"Excessive DOM Node Count ({total_dom_elements} nodes)", "fix": "Google recommends fewer than 1,500 DOM elements to optimize memory and crawler DOM parsing."})
    else:
        passes.append({"category": "Performance", "title": f"Optimal DOM Node Count ({total_dom_elements} nodes)", "detail": "Under 1,500 threshold"})

    # 3D Canvas & WebGL Experience Forensics
    canvases = tree.xpath('//canvas')
    has_canvas = len(canvases) > 0
    canvas_scripts = [s.get('src', '').lower() for s in all_scripts if s.get('src')]
    is_3d_experience = has_canvas or any(
        lib in " ".join(canvas_scripts) or lib in html_str.lower()
        for lib in ["three.js", "three.min.js", "@react-three", "babylon", "spline", "@splinetool", "webgl", "a-frame", "playcanvas"]
    )
    
    canvas_has_fallback = False
    if has_canvas:
        for c in canvases:
            c_text = c.text_content().strip()
            if len(c_text) > 20:
                canvas_has_fallback = True
                break

    sr_only_elements = tree.xpath('//*[contains(@class, "sr-only") or contains(@class, "visually-hidden") or @aria-hidden="false"]')
    has_sr_only_layer = len(sr_only_elements) > 0

    if is_3d_experience:
        if not canvas_has_fallback and not has_sr_only_layer and word_count < 150:
            js_score -= 20
            issues.append({
                "severity": "critical",
                "category": "3D Canvas & WebGL SEO",
                "title": "3D Canvas/WebGL Experience Detected Without Crawlable Semantic DOM",
                "fix": "Googlebot, Bingbot, and LLMs cannot read text trapped inside 3D canvases or WebGL shaders. Inject a semantic fallback layer inside <canvas> and an accessible .sr-only container so search engines and AI can index your 3D site."
            })
        elif canvas_has_fallback or has_sr_only_layer:
            passes.append({
                "category": "3D Canvas & WebGL SEO",
                "title": "3D Canvas Accessible Semantic Fallback Active",
                "detail": f"{len(canvases)} canvas element(s) with crawlable semantic fallback text"
            })
        else:
            warnings.append({
                "severity": "medium",
                "category": "3D Canvas & WebGL SEO",
                "title": "3D WebGL Elements Found with Minimal Fallback Text",
                "fix": "Provide a descriptive .sr-only semantic text container explaining the 3D scene features for AI engines and screen readers."
            })

    js_score = max(0, min(100, js_score))

    # -------------------------------------------------------------
    # 6. AI & GEO (GENERATIVE ENGINE OPTIMIZATION) READINESS
    # -------------------------------------------------------------
    geo_score = 50
    has_llms_txt = False
    if robots_data and robots_data.get("llms_txt", {}).get("exists"):
        has_llms_txt = True
        geo_score += 20
        passes.append({"category": "AI / GEO", "title": "/llms.txt standard file detected", "detail": f"Score: {robots_data['llms_txt'].get('score', 0)}/100"})
    else:
        warnings.append({"severity": "medium", "category": "AI / GEO", "title": "No /llms.txt file detected", "fix": "Generate an /llms.txt file to help AI agents discover your key pages, docs, and APIs in standardized markdown."})

    facts_entities = re.findall(r'\b(?:\$\d+|\d+%(?:\.\d+)?|\b(?:19|20)\d{2}\b|\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b)', cleaned_text)
    fact_count = len(facts_entities)

    first_200_words = " ".join(words[:200]).lower()
    has_definitions = any(token in first_200_words for token in [" is a ", " are a ", " refers to ", " provides ", " allows ", " designed to ", " what is ", " defined as "])
    if has_definitions:
        geo_score += 10
        passes.append({"category": "AI / GEO", "title": "Direct definition/answer found in lead 200 words", "detail": "Inverted pyramid format optimized for Perplexity and ChatGPT Search citations."})
    else:
        warnings.append({"severity": "low", "category": "AI / GEO", "title": "No direct definition in top 200 words", "fix": "Front-load direct answers or definitions early in the article to improve LLM citation probability."})

    if word_count >= 500: geo_score += 10
    elif word_count >= 250: geo_score += 5
    if li_count >= 5: geo_score += 5
    if table_count >= 1: geo_score += 5
    if text_ratio >= 15.0: geo_score += 5
    if faq_question_count >= 2: geo_score += 5
    if is_spa_dependent: geo_score -= 35

    if robots_data and robots_data.get("robots_txt", {}).get("analysis"):
        ai_bots = [b for b in robots_data["robots_txt"]["analysis"].get("bot_permissions", []) if b.get("category") == "ai"]
        blocked_ai = sum(1 for b in ai_bots if "Blocked" in b.get("status", ""))
        if blocked_ai > 4:
            geo_score -= 25
            warnings.append({"severity": "high", "category": "AI / GEO", "title": f"{blocked_ai} AI crawlers are blocked in robots.txt", "fix": "If you want citations in ChatGPT or Perplexity, unblock GPTBot, ClaudeBot, and PerplexityBot in robots.txt."})
    geo_score = max(0, min(100, geo_score))

    avg_words_per_section = round(word_count / max(len(h2_list) + len(h3_list), 1))
    is_chunkable = 100 <= avg_words_per_section <= 450
    chunk_score = 90 if is_chunkable else (70 if avg_words_per_section < 600 else 50)

    # -------------------------------------------------------------
    # 7. IMAGES & ACCESSIBILITY AUDIT
    # -------------------------------------------------------------
    images = tree.xpath('//img')
    total_images = len(images)
    missing_alt = []
    missing_dimensions = []
    modern_formats = 0
    lazy_images = 0
    
    for img in images:
        src = img.get('src', '')
        alt = img.get('alt', None)
        w = img.get('width')
        h = img.get('height')
        loading = img.get('loading', '').lower()
        
        if alt is None or alt.strip() == '':
            missing_alt.append(src[:100] or 'Inline/Data image')
        if not (w and h):
            missing_dimensions.append(src[:100] or 'Image')
        if any(src.lower().endswith(ext) for ext in ['.webp', '.avif', '.svg']):
            modern_formats += 1
        if loading == 'lazy':
            lazy_images += 1

    if total_images > 0:
        if len(missing_alt) > 0:
            warnings.append({"severity": "medium", "category": "Images & Accessibility", "title": f"{len(missing_alt)} of {total_images} images missing 'alt' text", "fix": "Add descriptive alt attributes to all content images for accessibility and image search."})
        else:
            passes.append({"category": "Images & Accessibility", "title": "All images have 'alt' attributes", "detail": f"{total_images} images inspected"})

        if len(missing_dimensions) > 0:
            warnings.append({"severity": "low", "category": "Core Web Vitals", "title": f"{len(missing_dimensions)} images missing explicit width/height (CLS Risk)", "fix": "Specify explicit 'width' and 'height' on <img> tags to avoid Cumulative Layout Shift (CLS)."})
        else:
            passes.append({"category": "Core Web Vitals", "title": "Image Dimensions Specified (CLS Protected)", "detail": "All images sized"})
    else:
        passes.append({"category": "Images & Accessibility", "title": "No image issues", "detail": "0 images on page"})

    # -------------------------------------------------------------
    # 8. LINKS & ANCHOR TEXT FORENSICS
    # -------------------------------------------------------------
    links = tree.xpath('//a')
    total_links = len(links)
    internal_links = 0
    external_links = 0
    empty_links = 0
    generic_anchors = []
    
    generic_anchor_words = {"click here", "read more", "learn more", "here", "more", "link", "website", "page"}
    
    for a in links:
        href = a.get('href', '').strip()
        anchor_text = a.text_content().strip().lower()
        
        if anchor_text in generic_anchor_words:
            generic_anchors.append(anchor_text)
            
        if not href or href.startswith('#') or href.startswith('javascript:'):
            empty_links += 1
            continue
        if href.startswith('http://') or href.startswith('https://'):
            link_domain = urllib.parse.urlparse(href).netloc
            if link_domain == parsed_target.netloc:
                internal_links += 1
            else:
                external_links += 1
        else:
            internal_links += 1

    if len(generic_anchors) > 0:
        warnings.append({"severity": "low", "category": "Links", "title": f"{len(generic_anchors)} links use generic anchor text ('click here', 'read more')", "fix": "Use descriptive keywords in anchor text to give search engines context about the destination page."})
    else:
        passes.append({"category": "Links", "title": "Descriptive Anchor Texts", "detail": "No generic 'click here' links detected"})

    if empty_links > 0:
        warnings.append({"severity": "low", "category": "Links", "title": f"{empty_links} empty or JavaScript links found (e.g. href='#')", "fix": "Replace empty href attributes with real target URLs or semantic buttons."})

    passes.append({"category": "Links", "title": f"Link profile: {internal_links} internal, {external_links} external", "detail": f"Total links: {total_links}"})

    # -------------------------------------------------------------
    # 9. SOCIAL META (OPEN GRAPH & TWITTER)
    # -------------------------------------------------------------
    og_title = (tree.xpath('//meta[@property="og:title"]/@content') or [""])[0]
    og_desc = (tree.xpath('//meta[@property="og:description"]/@content') or [""])[0]
    og_image = (tree.xpath('//meta[@property="og:image"]/@content') or [""])[0]
    og_url = (tree.xpath('//meta[@property="og:url"]/@content') or [""])[0]
    og_type = (tree.xpath('//meta[@property="og:type"]/@content') or [""])[0]
    og_site_name = (tree.xpath('//meta[@property="og:site_name"]/@content') or [""])[0]

    tw_card = (tree.xpath('//meta[@name="twitter:card"]/@content') or [""])[0]
    tw_title = (tree.xpath('//meta[@name="twitter:title"]/@content') or [""])[0] or og_title
    tw_desc = (tree.xpath('//meta[@name="twitter:description"]/@content') or [""])[0] or og_desc
    tw_image = (tree.xpath('//meta[@name="twitter:image"]/@content') or [""])[0] or og_image

    social_score = 0
    if og_title: social_score += 25
    if og_desc: social_score += 25
    if og_image: social_score += 25
    if tw_card: social_score += 25
    social_score = min(100, social_score)

    if not og_title or not og_image:
        warnings.append({"severity": "medium", "category": "Social / Open Graph", "title": "Incomplete Open Graph tags", "fix": "Provide `og:title`, `og:description`, and `og:image` for rich previews on social media and messaging apps."})
    else:
        passes.append({"category": "Social / Open Graph", "title": "Open Graph tags configured", "detail": f"Image: {og_image[:60]}..."})

    # -------------------------------------------------------------
    # 10. TARGET KEYWORD / SEARCH QUERY DOMINANCE ANALYSIS
    # -------------------------------------------------------------
    kw_audit = {}
    if target_keyword:
        kw_audit = analyze_target_keyword(
            keyword=target_keyword,
            title=title,
            description=description,
            h1_list=h1_list,
            h2_list=h2_list,
            words=words,
            cleaned_text=cleaned_text,
            target_url=target_url
        )
        if kw_audit.get("score", 0) < 60:
            warnings.append({
                "severity": "high",
                "category": "Target Keyword",
                "title": f"Page Under-Optimized for Target Keyword: '{target_keyword}' (Score: {kw_audit['score']}/100)",
                "fix": f"Follow the Target Keyword Studio checklist to place '{target_keyword}' into your Title, H1, and first 100 words."
            })
        else:
            passes.append({
                "category": "Target Keyword",
                "title": f"Strongly Optimized for Target Keyword: '{target_keyword}'",
                "detail": f"Keyword Score: {kw_audit['score']}/100 ({kw_audit['search_intent']} Intent)"
            })

    # -------------------------------------------------------------
    # 11. OVERALL & MODULAR SCORES
    # -------------------------------------------------------------
    trad_score = 100
    if not title: trad_score -= 25
    elif title_len < 30 or title_len > 65: trad_score -= 5
    if not description: trad_score -= 20
    elif desc_len < 80 or desc_len > 165: trad_score -= 5
    if not canonical: trad_score -= 10
    if "noindex" in robots_meta: trad_score -= 40
    if len(h1_list) != 1: trad_score -= 10
    if len(missing_alt) > 0: trad_score -= min(10, len(missing_alt) * 2)
    trad_score = max(0, min(100, trad_score))

    content_score = 70
    if word_count >= 600: content_score += 15
    elif word_count >= 300: content_score += 10
    if reading_metrics["score"] >= 60: content_score += 10
    if not over_opt_phrases: content_score += 5
    content_score = max(0, min(100, content_score))

    schema_score = schema_data.get("score", 0) if schema_data else 0

    overall_score = round(
        (trad_score * 0.22) +
        (geo_score * 0.22) +
        (js_score * 0.18) +
        (tech_score * 0.15) +
        (schema_score * 0.13) +
        (social_score * 0.10)
    )

    if overall_score >= 90: executive_grade = "A+ (Industry Leader)"
    elif overall_score >= 80: executive_grade = "A (Strong Search & AI Health)"
    elif overall_score >= 70: executive_grade = "B (Good with Optimization Gaps)"
    elif overall_score >= 55: executive_grade = "C (Needs Immediate Action)"
    else: executive_grade = "F (High Crawl & Visibility Risk)"

    ai_status = "Ready & Inspectable"
    if is_spa_dependent:
        ai_status = "At Risk (Client-Side Rendered - Blank for AI Crawlers)"
    elif word_count < 100:
        ai_status = "Thin Static HTML"

    return {
        "url": target_url,
        "scores": {
            "overall": overall_score,
            "grade": executive_grade,
            "traditional": trad_score,
            "geo_ai": geo_score,
            "javascript": js_score,
            "technical": tech_score,
            "content": content_score,
            "schema": schema_score,
            "social": social_score
        },
        "meta": {
            "title": title,
            "title_length": title_len,
            "title_pixel_width": title_pixel_width,
            "description": description,
            "description_length": desc_len,
            "has_cta": has_cta,
            "canonical": canonical,
            "robots_meta": robots_meta or "index, follow",
            "viewport": viewport,
            "lang": html_lang,
            "charset": "UTF-8" if has_utf8 else "Missing"
        },
        "headings": {
            "h1": h1_list,
            "h2": h2_list,
            "h3": h3_list,
            "h4": h4_list,
            "h5": h5_list,
            "h6": h6_list,
            "total_h1": len(h1_list),
            "total_h2": len(h2_list),
            "total_h3": len(h3_list),
            "has_skipped_levels": has_skipped_levels
        },
        "content_metrics": {
            "word_count": word_count,
            "char_count": char_count,
            "sentences_count": len(sentences),
            "html_bytes": html_bytes,
            "text_ratio": text_ratio,
            "reading_ease": reading_metrics,
            "reading_time_mins": round(word_count / 200, 1),
            "over_optimized_phrases": over_opt_phrases,
            "tables_count": table_count,
            "list_items_count": li_count,
            "faq_questions_count": faq_question_count,
            "sample_snippet": cleaned_text[:400] + "..." if len(cleaned_text) > 400 else cleaned_text
        },
        "geo_ai_metrics": {
            "has_llms_txt": has_llms_txt,
            "has_lead_definition": has_definitions,
            "fact_density_count": fact_count,
            "sample_facts": facts_entities[:6],
            "chunkability_score": chunk_score,
            "avg_words_per_section": avg_words_per_section,
            "ai_indexing_status": ai_status
        },
        "javascript_audit": {
            "is_spa_dependent": is_spa_dependent,
            "has_spa_container": has_spa_container,
            "total_scripts": len(all_scripts),
            "render_blocking_count": len(render_blocking_scripts),
            "render_blocking_scripts": render_blocking_scripts[:10],
            "render_blocking_styles": render_blocking_styles[:5],
            "has_noscript": has_noscript,
            "noscript_is_boilerplate": noscript_is_boilerplate,
            "noscript_text": noscript_text[:300],
            "total_dom_elements": total_dom_elements,
            "max_dom_depth": max_depth,
            "static_html_score": js_score,
            "has_canvas": has_canvas,
            "is_3d_experience": is_3d_experience,
            "canvas_has_fallback": canvas_has_fallback,
            "has_sr_only_layer": has_sr_only_layer
        },
        "technical_audit": {
            "is_https": is_https,
            "hsts": bool(hsts),
            "csp": bool(csp),
            "nosniff": bool(nosniff),
            "content_encoding": content_encoding,
            "latency_ms": latency_ms,
            "mixed_content_count": len(http_resources)
        },
        "images": {
            "total": total_images,
            "missing_alt_count": len(missing_alt),
            "missing_alt_samples": missing_alt[:8],
            "missing_dimensions_count": len(missing_dimensions),
            "modern_formats_count": modern_formats,
            "lazy_images_count": lazy_images
        },
        "links": {
            "total": total_links,
            "internal": internal_links,
            "external": external_links,
            "empty": empty_links,
            "generic_anchors_count": len(generic_anchors),
            "generic_anchors_samples": list(set(generic_anchors))[:5]
        },
        "social": {
            "og_title": og_title or title,
            "og_description": og_desc or description,
            "og_image": og_image,
            "og_url": og_url or target_url,
            "og_type": og_type or "website",
            "og_site_name": og_site_name or parsed_target.netloc,
            "twitter_card": tw_card or "summary_large_image",
            "twitter_title": tw_title or title,
            "twitter_description": tw_desc or description,
            "twitter_image": tw_image or og_image
        },
        "target_keyword_audit": kw_audit,
        "issues": sorted(issues, key=lambda x: 0 if x["severity"] == "critical" else (1 if x["severity"] == "high" else 2)),
        "warnings": warnings,
        "passes": passes
    }
