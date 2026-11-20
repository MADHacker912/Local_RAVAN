#!/usr/bin/env python3
# target urls ko surf karke osint search aur business logic attack vectors prepare karne wala module

import sys
import os
import re
import json
import urllib.parse
from typing import Dict, Any, List, Optional
import requests
from bs4 import BeautifulSoup
import warnings

# faltu warning messages ko ignore kar rahe hain
warnings.filterwarnings("ignore")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

def search_web(query: str, max_results: int = 4) -> List[Dict[str, str]]:
    # duckduckgo se target ke bare me past writeups aur cve search karne ka function
    results = []
    try:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            hits = list(ddgs.text(query, max_results=max_results))
            for h in hits:
                results.append({
                    "title": h.get("title", ""),
                    "url": h.get("href", ""),
                    "snippet": h.get("body", "")
                })
    except Exception as e:
        results.append({
            "title": f"Search fallback for: {query}",
            "url": "",
            "snippet": f"Could not fetch search results: {str(e)}"
        })
    return results

def detect_business_category(text_lower: str, links: List[str], meta_desc: str) -> Dict[str, Any]:
    # target website kis category ki hai uska business model samajhne ka function
    combined = (text_lower + " " + meta_desc + " " + " ".join(links)).lower()

    category = "General Web Application"
    critical_flows = []
    recommended_attack_vectors = []

    # e commerce shopping portals ke attack vectors
    if any(k in combined for k in ["cart", "checkout", "add to cart", "shop", "shipping", "price", "store", "product", "coupon"]):
        category = "E-Commerce / Online Store"
        critical_flows = ["Shopping Cart", "Order Checkout", "Discount/Coupon Codes", "Payment Processing", "Shipping Address"]
        recommended_attack_vectors = [
            "Price Parameter Tampering (changing price/quantity in POST request)",
            "IDOR in Order History & Invoices (/order?id=123)",
            "Race Conditions on Coupon / Voucher Applications",
            "Negative Quantity or Currency Rounding Issues",
            "Payment Gateway Callback Manipulation"
        ]

    # banking aur crypto platforms ke attack vectors
    elif any(k in combined for k in ["bank", "transfer", "wallet", "crypto", "exchange", "deposit", "withdraw", "trading", "loan"]):
        category = "FinTech / Financial / Banking / Crypto"
        critical_flows = ["Fund Transfers", "Wallet Balance", "Deposit / Withdrawal Requests", "2FA / OTP Verification", "KYC Uploads"]
        recommended_attack_vectors = [
            "Broken Object Level Authorization (BOLA) in Account Balance / Transactions",
            "Race Conditions in Transfer / Withdrawal (double spending)",
            "OTP / 2FA Rate-Limit Bypass & Flawed Logic",
            "Negative Transfer Amount or Currency Switching Arbitrage",
            "IDOR in Financial Statements & KYC Documents"
        ]

    # saas aur cloud b2b platforms ke attack vectors
    elif any(k in combined for k in ["workspace", "team", "organization", "dashboard", "billing", "subscription", "invite", "webhook", "api keys"]):
        category = "SaaS / B2B Enterprise Platform"
        critical_flows = ["Workspace Management", "Team Member Invites", "Role-Based Access (Admin/Editor/Viewer)", "API Key Generation", "Webhooks"]
        recommended_attack_vectors = [
            "Multi-Tenant Isolation Bypass (accessing Org B data with Org A user)",
            "Privilege Escalation (Member promoting self to Admin)",
            "SSRF via Webhook Endpoints / Integrations",
            "CORS Misconfiguration on Sensitive API Endpoints",
            "IDOR in Billing Invoices & User Profiles"
        ]

    # social media aur chat platforms ke attack vectors
    elif any(k in combined for k in ["post", "feed", "comment", "chat", "profile", "follow", "messages", "community"]):
        category = "Social / Content / Community Platform"
        critical_flows = ["Direct Messaging", "User Profiles", "Post & Comment Feeds", "File/Avatar Uploads"]
        recommended_attack_vectors = [
            "Stored XSS in Markdown/Comments/Bio Fields",
            "IDOR in Private Chat Messages & Inbox",
            "Unrestricted File Upload via Profile Pictures",
            "Account Takeover via Flawed Password Reset Tokens",
            "CSRF in State-Changing Actions (Follow/Like/Post)"
        ]

    # medical aur health portals ke attack vectors
    elif any(k in combined for k in ["patient", "doctor", "health", "medical", "clinic", "prescription", "appointment"]):
        category = "Healthcare / MedTech"
        critical_flows = ["Patient Records (HIPAA)", "Doctor Appointments", "Prescription Management"]
        recommended_attack_vectors = [
            "IDOR & BOLA exposing sensitive patient records (PHI)",
            "Unauthenticated API endpoints leaking appointment data",
            "Insecure PDF generation / Medical report download"
        ]

    # general web apps aur standard api attack vectors
    else:
        critical_flows = ["User Authentication", "Session Management", "Profile Management", "API Interactions"]
        recommended_attack_vectors = [
            "Broken Authentication & Session Fixation",
            "SQL Injection & Cross-Site Scripting (XSS)",
            "API Authorization Flaws & Mass Assignment",
            "Information Disclosure via Verbose Error Messages"
        ]

    return {
        "category": category,
        "critical_flows": critical_flows,
        "tailored_attack_vectors": recommended_attack_vectors
    }

def surf_webpage(url: str, extract_scope: bool = True, perform_osint_search: bool = True) -> Dict[str, Any]:
    # website ko surf karke security headers aur in scope assets nikalne ka main function
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url

    parsed = urllib.parse.urlparse(url)
    base_domain = parsed.netloc

    try:
        session = requests.Session()
        session.headers.update(HEADERS)
        resp = session.get(url, timeout=12, verify=False, allow_redirects=True)
    except Exception as e:
        return {"status": "error", "url": url, "error": f"Failed to connect to {url}: {str(e)}"}

    soup = BeautifulSoup(resp.text, "html.parser")
    title = soup.title.string.strip() if soup.title and soup.title.string else base_domain

    meta_desc = ""
    desc_tag = soup.find("meta", attrs={"name": "description"}) or soup.find("meta", attrs={"property": "og:description"})
    if desc_tag and desc_tag.get("content"):
        meta_desc = desc_tag["content"].strip()

    # target ke security headers check kar rahe hain jaise hsts csp aur x frame options
    csp = resp.headers.get("Content-Security-Policy", "")
    x_frame = resp.headers.get("X-Frame-Options", "")
    cors_origin = resp.headers.get("Access-Control-Allow-Origin", "")

    sec_headers = {
        "Strict-Transport-Security": resp.headers.get("Strict-Transport-Security", "Missing"),
        "Content-Security-Policy": csp[:120] if csp else "Missing",
        "X-Frame-Options": x_frame if x_frame else "Missing",
        "Access-Control-Allow-Origin": cors_origin if cors_origin else "Not Reflected",
        "X-Content-Type-Options": resp.headers.get("X-Content-Type-Options", "Missing"),
        "Server": resp.headers.get("Server", "Undisclosed"),
    }

    # check kar rahe hain ki site frame ho sakti hai ya clickjacking ka risk hai
    framing_allowed = False
    if not x_frame and "frame-ancestors" not in csp.lower():
        framing_allowed = True

    # client side javascript aur postmessage wildcard broadcast ka analysis
    postmessage_findings = []
    if "postMessage" in resp.text:
        # postmessage me star wildcard pattern dhoondh rahe hain
        pm_wildcards = re.findall(r'postMessage\([^,]+,\s*["\']\*["\']\)', resp.text)
        if pm_wildcards:
            postmessage_findings.append({
                "type": "Unrestricted PostMessage Broadcast (*)",
                "evidence": pm_wildcards[:3],
                "risk": "CWE-345: Sensitive state or payload can be intercepted by framing origin"
            })
        if "addEventListener" in resp.text and "message" in resp.text:
            postmessage_findings.append({
                "type": "Cross-Origin Message Listener Detected",
                "risk": "Potential missing event.origin validation in message handler"
            })

    # page ke sare links aur sensitive api routes nikal rahe hain
    links = set()
    api_endpoints = set()
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if href.startswith("javascript:") or href.startswith("#") or href.startswith("mailto:"):
            continue
        full_url = urllib.parse.urljoin(url, href)
        links.add(full_url)
        if any(api_k in full_url for api_k in ["/api/", "/v1/", "/v2/", "/graphql", "/auth", "/login", "/register", "/cart", "/checkout", "/admin"]):
            api_endpoints.add(full_url)

    # website ka tech stack pehchan rahe hain jaise react nginx wordpress
    technologies = []
    text_lower = resp.text.lower()
    if "wp-content" in text_lower or "wordpress" in text_lower:
        technologies.append("WordPress")
    if "react" in text_lower or "_next" in text_lower:
        technologies.append("React / Next.js")
    if "vue" in text_lower or "nuxt" in text_lower:
        technologies.append("Vue.js")
    if "shopify" in text_lower:
        technologies.append("Shopify")
    if "cloudflare" in resp.headers.get("Server", "").lower():
        technologies.append("Cloudflare CDN/WAF")
    if "nginx" in resp.headers.get("Server", "").lower():
        technologies.append("Nginx")

    # bug bounty program ke in scope domains aur wildcards extract kar rahe hain
    in_scope_candidates = set()
    domain_pattern = re.compile(r'(\*\.[a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,}|[a-zA-Z0-9\-\.]+\.' + re.escape(base_domain.split('.')[-2] if len(base_domain.split('.')) >= 2 else base_domain) + r')')
    for match in domain_pattern.findall(resp.text):
        match_clean = match.strip(".,;:\"'()[]{}")
        if match_clean:
            in_scope_candidates.add(match_clean)

    # html tags hata kar saaf text model ko padhne ke liye ready kar rahe hain
    for element in soup(["script", "style", "noscript", "svg"]):
        element.decompose()
    visible_text = soup.get_text(separator=" ", strip=True)
    clean_text = re.sub(r'\s+', ' ', visible_text)[:3500]

    # website kis category ki hai uska business model samajh rahe hain
    business_intel = detect_business_category(clean_text, list(links), meta_desc)

    # target ke past bug bounty writeups aur cve internet pe search kar rahe hain
    osint_results = []
    if perform_osint_search:
        clean_domain_name = base_domain.replace("www.", "")
        search_query = f"{clean_domain_name} bug bounty writeup vulnerabilities"
        osint_results = search_web(search_query, max_results=3)

    return {
        "status": "success",
        "url": url,
        "title": title,
        "meta_description": meta_desc,
        "business_intelligence": business_intel,
        "osint_search_writeups": osint_results,
        "technologies": technologies if technologies else ["Standard Web Architecture"],
        "security_headers": sec_headers,
        "framing_clickjacking_allowed": framing_allowed,
        "postmessage_findings": postmessage_findings,
        "in_scope_assets": sorted(list(in_scope_candidates))[:15],
        "sensitive_endpoints": sorted(list(api_endpoints))[:10],
        "discovered_links_count": len(links),
        "page_content_summary": clean_text[:1200]
    }

if __name__ == "__main__":
    test_url = sys.argv[1] if len(sys.argv) > 1 else "https://shopify.com"
    res = surf_webpage(test_url)
    print(json.dumps(res, indent=2))
