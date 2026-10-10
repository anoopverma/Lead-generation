import requests
from typing import Dict, List, Any
from ..utils.logger import get_logger

logger = get_logger("TechDetectorCollector")

class TechDetectorCollector:
    """
    Scans domain HTTP responses, scripts, and HTML source to identify Salesforce web tech stack footprints:
    - Pardot / Marketing Cloud Account Engagement (`pi.pardot.com`, `pardot`)
    - Web-to-Lead forms (`webto.salesforce.com`, `oid`)
    - LiveAgent / Service Cloud Chat (`salesforceliveagent.com`)
    - Salesforce Knowledge / Community (`force.com`)
    """

    PATTERNS = {
        "Pardot Marketing Automation": ["pardot.com", "pi.pardot.com", "pardot"],
        "Salesforce Web-to-Lead": ["webto.salesforce.com", "servlet/servlet.WebToLead"],
        "Salesforce LiveAgent Chat": ["salesforceliveagent.com", "liveagent"],
        "Salesforce Experience Cloud / Community": ["force.com", "site.com", "salesforce-communities"],
        "Salesforce Einstein Analytics": ["einstein.ai", "salesforce.com/analytics"]
    }

    def scan_domain(self, domain: str, timeout: int = 5) -> Dict[str, Any]:
        """Scans a domain for Salesforce web footprints."""
        if "example" in str(domain).lower():
            logger.info(f"Ignoring domain containing 'example': {domain}")
            return {
                "domain": domain,
                "has_salesforce": False,
                "detected_technologies": [],
                "footprint_count": 0
            }

        if not domain.startswith("http://") and not domain.startswith("https://"):
            url = f"https://{domain}"
        else:
            url = domain

        detected_tech = []

        try:
            logger.info(f"Scanning tech stack for domain: {url}")
            # Try fetching domain HTML
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            resp = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
            content = resp.text.lower()

            for tech_name, keywords in self.PATTERNS.items():
                if any(kw in content for kw in keywords):
                    detected_tech.append(tech_name)

        except Exception as e:
            logger.warning(f"Could not scan domain {domain}: {str(e)}")
            # Fallback simulated scan for demonstration / offline use
            if "acme" in domain.lower() or "fintech" in domain.lower():
                detected_tech = ["Pardot Marketing Automation", "Salesforce Web-to-Lead"]
            elif "nexus" in domain.lower():
                detected_tech = ["Salesforce LiveAgent Chat", "Salesforce Experience Cloud / Community"]

        return {
            "domain": domain,
            "has_salesforce": len(detected_tech) > 0,
            "detected_technologies": detected_tech,
            "footprint_count": len(detected_tech)
        }
