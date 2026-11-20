import json
import re
from typing import Dict, Any, List
import lxml.html

SCHEMA_REQUIREMENTS = {
    "Article": {
        "required": ["headline", "author", "datePublished"],
        "recommended": ["image", "publisher", "dateModified", "description"],
        "purpose": "Eligible for Google News, Top Stories carousel, and AI summary citations"
    },
    "NewsArticle": {
        "required": ["headline", "author", "datePublished"],
        "recommended": ["image", "publisher", "dateModified"],
        "purpose": "Eligible for Google News and Top Stories"
    },
    "BlogPosting": {
        "required": ["headline", "author", "datePublished"],
        "recommended": ["image", "publisher", "description"],
        "purpose": "Enhances blog visibility and author citation in AI search"
    },
    "FAQPage": {
        "required": ["mainEntity"],
        "recommended": ["name"],
        "purpose": "Provides direct Question/Answer pairs directly ingested by ChatGPT, Perplexity, and SERP accordions"
    },
    "QAPage": {
        "required": ["mainEntity"],
        "recommended": ["name"],
        "purpose": "Optimized for community Q&A and technical solution engines"
    },
    "HowTo": {
        "required": ["name", "step"],
        "recommended": ["image", "totalTime", "description"],
        "purpose": "Rich step-by-step visual cards on Google and voice assistant instructions"
    },
    "Product": {
        "required": ["name", "offers"],
        "recommended": ["image", "description", "review", "aggregateRating", "brand"],
        "purpose": "Rich product snippets with prices, stock, ratings in SERPs and AI shopping engines"
    },
    "Organization": {
        "required": ["name", "url"],
        "recommended": ["logo", "sameAs", "contactPoint", "description"],
        "purpose": "Builds Brand Entity and Google Knowledge Graph recognition"
    },
    "LocalBusiness": {
        "required": ["name", "address"],
        "recommended": ["telephone", "openingHours", "image", "geo", "priceRange"],
        "purpose": "Powers Google Maps, local search packs, and AI local recommendations"
    },
    "BreadcrumbList": {
        "required": ["itemListElement"],
        "recommended": [],
        "purpose": "Enhances navigation links in search snippets and helps AI understand site hierarchy"
    },
    "WebSite": {
        "required": ["name", "url"],
        "recommended": ["potentialAction"],
        "purpose": "Enables Sitelinks Search Box and identifies official site identity"
    },
    "SoftwareApplication": {
        "required": ["name", "offers"],
        "recommended": ["operatingSystem", "applicationCategory", "aggregateRating"],
        "purpose": "Highlights app details, download options, and user reviews"
    },
    "SpeakableSpecification": {
        "required": ["xpath"],
        "recommended": [],
        "purpose": "Google Assistant, Siri & Voice Search Answer Engine Optimization (AEO)"
    },
    "VideoObject": {
        "required": ["name", "description", "thumbnailUrl", "uploadDate"],
        "recommended": ["contentUrl", "embedUrl"],
        "purpose": "Video carousels, Google Video search, and AI multimodal ingestion"
    },
    "Person": {
        "required": ["name"],
        "recommended": ["sameAs", "jobTitle", "worksFor", "image"],
        "purpose": "Establishes Google E-E-A-T (Experience, Expertise, Authoritativeness, Trustworthiness) author identity"
    }
}

def extract_schemas_from_html(html_str: str) -> Dict[str, Any]:
    """Extract and validate all JSON-LD and Microdata schemas embedded in HTML."""
    if not html_str:
        return {"schemas": [], "errors": [], "types_found": [], "score": 0, "recommendations": [], "has_same_as": False}
        
    try:
        tree = lxml.html.fromstring(html_str)
    except Exception as e:
        return {"schemas": [], "errors": [f"HTML parsing failed: {str(e)}"], "types_found": [], "score": 0, "recommendations": [], "has_same_as": False}
        
    script_nodes = tree.xpath('//script[@type="application/ld+json"]')
    
    schemas = []
    errors = []
    types_found = set()
    has_same_as = False
    
    for idx, node in enumerate(script_nodes):
        raw_text = node.text_content().strip() if node.text_content() else ""
        if not raw_text:
            continue
            
        try:
            parsed = json.loads(raw_text)
            
            entities = []
            if isinstance(parsed, list):
                entities.extend(parsed)
            elif isinstance(parsed, dict):
                if "@graph" in parsed and isinstance(parsed["@graph"], list):
                    entities.extend(parsed["@graph"])
                else:
                    entities.append(parsed)
                    
            for entity in entities:
                if not isinstance(entity, dict):
                    continue
                type_name = entity.get("@type")
                if isinstance(type_name, list):
                    types_found.update(type_name)
                    display_type = ", ".join(type_name)
                elif type_name:
                    types_found.add(type_name)
                    display_type = str(type_name)
                else:
                    display_type = "Unknown / Untyped"
                    
                # Check for knowledge graph authority links (sameAs)
                if entity.get("sameAs"):
                    has_same_as = True
                    
                # Field analysis
                rules = SCHEMA_REQUIREMENTS.get(display_type, None)
                missing_req = []
                missing_rec = []
                purpose = "Structured semantic data for search engines & AI agents"
                
                if rules:
                    purpose = rules["purpose"]
                    for req in rules["required"]:
                        if req not in entity or not entity[req]:
                            missing_req.append(req)
                    for rec in rules["recommended"]:
                        if rec not in entity or not entity[rec]:
                            missing_rec.append(rec)
                            
                schemas.append({
                    "type": display_type,
                    "data": entity,
                    "is_valid": len(missing_req) == 0,
                    "missing_required": missing_req,
                    "missing_recommended": missing_rec,
                    "purpose": purpose
                })
                
        except json.JSONDecodeError as err:
            errors.append(f"JSON-LD Block #{idx + 1} has invalid JSON syntax: {str(err)}")
            
    # Calculate score
    score = 0
    recommendations = []
    
    if schemas:
        score = 50
        valid_count = sum(1 for s in schemas if s["is_valid"])
        score += int((valid_count / len(schemas)) * 25)
        if "Organization" in types_found or "WebSite" in types_found:
            score += 10
        if "BreadcrumbList" in types_found or "FAQPage" in types_found or "Article" in types_found or "HowTo" in types_found:
            score += 10
        if has_same_as:
            score += 5
        score = min(100, score)
    else:
        recommendations.append({
            "severity": "high",
            "message": "No JSON-LD Structured Data detected.",
            "action": "Add Schema.org JSON-LD (such as Organization, WebSite, and FAQPage) to enable rich snippets and AI answer synthesis."
        })
        
    for s in schemas:
        if s["missing_required"]:
            recommendations.append({
                "severity": "medium",
                "message": f"Schema @type '{s['type']}' is missing required fields: {', '.join(s['missing_required'])}.",
                "action": f"Provide the missing required properties to make '{s['type']}' valid for rich Google results."
            })
            
    return {
        "schemas": schemas,
        "errors": errors,
        "types_found": list(types_found),
        "score": score,
        "has_same_as": has_same_as,
        "recommendations": recommendations
    }
