import re
from typing import List, Dict, Any
from ..utils.logger import get_logger

logger = get_logger("LeadScorer")

def is_example_lead(lead: Dict[str, Any]) -> bool:
    """
    Checks if a lead's domain, url, website, maps_url, contact_details, or any URL string
    contains 'example' (case-insensitive), so it can be filtered out from all scans.
    """
    if not isinstance(lead, dict):
        return False
    
    # Priority check on standard domain / URL fields
    for field in ["domain", "url", "website", "maps_url"]:
        val = lead.get(field)
        if val and "example" in str(val).lower():
            return True

    # Check contact details and values containing URLs with 'example'
    for key, val in lead.items():
        if isinstance(val, str):
            val_lower = val.lower()
            if "example" in val_lower:
                if key in ["domain", "url", "website", "maps_url", "contact_details"]:
                    return True
                if "example.com" in val_lower or "example.org" in val_lower or "example.net" in val_lower or "://example" in val_lower:
                    return True
            
    return False


class LeadScorer:
    """
    Evaluates and ranks Salesforce project leads based on multi-channel signals and confidence verification:
    - Lead Score (0-100): Buying intent & project value potential
    - Confidence Score (0-100%): Signal verification, email deliverability, and legal entity validation
    - Filters out low-confidence leads below threshold (default > 60%)
    - Filters out any lead or URL containing 'example'
    """

    def __init__(self, min_confidence_score: int = 60):
        self.min_confidence_score = min_confidence_score

    def score_and_merge_leads(
        self,
        job_leads: List[Dict[str, Any]],
        tech_scans: List[Dict[str, Any]],
        intent_leads: List[Dict[str, Any]],
        min_confidence: int = None
    ) -> List[Dict[str, Any]]:
        """
        Merges multi-source signals by domain / company, computes lead score & confidence score,
        ensures standard fields (project_description, timeline, budget, contact_details, confidence_score),
        filters leads with confidence_score > min_confidence (default 60),
        and ignores any lead containing 'example' in domain or URL.
        """
        # Ignore any lead containing 'example' in domain or URL across all scans
        job_leads = [l for l in job_leads if not is_example_lead(l)]
        intent_leads = [l for l in intent_leads if not is_example_lead(l)]
        tech_scans = [t for t in tech_scans if not is_example_lead(t)]

        threshold = min_confidence if min_confidence is not None else self.min_confidence_score
        logger.info(f"Merging lead sources, calculating confidence scores, and filtering for confidence > {threshold}%...")
        
        lead_map: Dict[str, Dict[str, Any]] = {}
        seen_phones: Dict[str, str] = {}  # phone -> key map for strict contact phone deduplication

        def compute_key(lead: Dict[str, Any]) -> str:
            phone = lead.get("phone", "")
            if phone:
                digits = re.sub(r'\D', '', str(phone))
                if len(digits) >= 8:
                    phone_key = f"phone_{digits[-10:]}"
                    if phone_key in seen_phones:
                        return seen_phones[phone_key]
            
            domain = lead.get("domain", "").strip().lower()
            if domain:
                clean_domain = re.sub(r'\d+', '', domain)
                key = f"domain_{clean_domain}"
                if phone:
                    digits = re.sub(r'\D', '', str(phone))
                    if len(digits) >= 8:
                        seen_phones[f"phone_{digits[-10:]}"] = key
                return key

            company = lead.get("company_name", "").strip().lower()
            clean_company = re.sub(r'#\d+|\(\d+\)', '', company).strip()
            key = f"company_{clean_company}"
            if phone:
                digits = re.sub(r'\D', '', str(phone))
                if len(digits) >= 8:
                    seen_phones[f"phone_{digits[-10:]}"] = key
            return key

        # 1. Process Job Signals
        for lead in job_leads:
            company = lead["company_name"]
            domain = lead.get("domain", "")
            key = compute_key(lead)

            item = {
                "company_name": company,
                "domain": domain,
                "hiring_signal": lead["role_posted"],
                "hiring_count": lead.get("hiring_count", 1),
                "location": lead.get("location", "N/A"),
                "project_description": f"Hiring {lead['role_posted']} ({lead.get('details', 'Salesforce Implementation & Support')})",
                "timeline": "Immediate (Active Hiring)",
                "budget": f"${lead.get('hiring_count', 1) * 60}k - ${lead.get('hiring_count', 1) * 120}k (Est.)",
                "contact_title": f"Hiring Manager - {lead['role_posted']}",
                "contact_details": f"Hiring Manager (contact@{domain})",
                "tech_footprint": [],
                "intent_signal": None,
                "enrichment": lead.get("enrichment", {}),
                "score": 40 + min(lead.get("hiring_count", 1) * 5, 15)  # 40 - 55 pts for hiring
            }
            if "source" in lead:
                item["source"] = lead["source"]
            if "verified_signal" in lead:
                item["verified_signal"] = lead["verified_signal"]
            lead_map[key] = item

        # 2. Process Intent & Freelance Marketplace Signals
        for lead in intent_leads:
            company = lead["company_name"]
            domain = lead.get("domain", "")
            key = compute_key(lead)
            intent_text = lead.get("intent_signal") or lead.get("project_description", "Salesforce Consulting Project")

            if key not in lead_map:
                lead_map[key] = {
                    "company_name": company,
                    "domain": domain,
                    "category": lead.get("category", "N/A"),
                    "rating": lead.get("rating"),
                    "review_count": lead.get("review_count"),
                    "phone": lead.get("phone"),
                    "latitude": lead.get("latitude"),
                    "longitude": lead.get("longitude"),
                    "maps_url": lead.get("maps_url"),
                    "lead_type": lead.get("lead_type"),
                    "website_status": lead.get("website_status"),
                    "hiring_signal": lead.get("hiring_signal"),
                    "hiring_count": lead.get("hiring_count", 0),
                    "source": lead.get("source"),
                    "verified_signal": lead.get("verified_signal"),
                    "location": lead.get("location", "N/A"),
                    "project_description": intent_text,
                    "timeline": lead.get("timeline") or lead.get("target_timeframe", "1-3 Months"),
                    "budget": lead.get("estimated_budget") or lead.get("budget", "$1,500 - $3,500"),
                    "estimated_budget": lead.get("estimated_budget") or lead.get("budget", "$1,500 - $3,500"),
                    "contact_title": lead.get("contact_title", "Project Owner"),
                    "contact_details": lead.get("contact_details") or f"{lead.get('contact_title', 'Project Owner')} (contact@{domain})",
                    "tech_footprint": [],
                    "intent_signal": intent_text,
                    "enrichment": lead.get("enrichment", {}),
                    "score": 50  # 50 pts for RFP/Intent signal
                }
            else:
                lead_map[key]["intent_signal"] = intent_text
                lead_map[key]["project_description"] = f"{lead_map[key]['project_description']} | RFP: {intent_text}"
                lead_map[key]["timeline"] = lead.get("timeline") or lead.get("target_timeframe", lead_map[key]["timeline"])
                lead_map[key]["budget"] = lead.get("budget") or lead.get("estimated_budget", lead_map[key]["budget"])
                lead_map[key]["contact_title"] = lead.get("contact_title", lead_map[key]["contact_title"])
                lead_map[key]["contact_details"] = lead.get("contact_details") or f"{lead_map[key]['contact_title']} (contact@{domain})"
                lead_map[key]["score"] += 40  # Stack intent onto hiring
                if not lead_map[key].get("enrichment") and lead.get("enrichment"):
                    lead_map[key]["enrichment"] = lead.get("enrichment")

        # 3. Process Tech Stack Scans
        tech_map = {item["domain"]: item for item in tech_scans}
        for key, lead in lead_map.items():
            domain = lead["domain"]
            if domain in tech_map and tech_map[domain]["has_salesforce"]:
                techs = tech_map[domain]["detected_technologies"]
                lead["tech_footprint"] = techs
                lead["score"] += 20 + min(len(techs) * 5, 10)  # Add points for existing SF tech

        # 4. Account for Free-Tier Enrichment & Calculate Confidence Score
        for key, lead in lead_map.items():
            # Base confidence: 70% for verified collector signals with source, 50% for raw/unverified inputs
            confidence = 70 if (lead.get("verified_signal") or lead.get("source")) else 50
            enrichment = lead.get("enrichment", {})

            # Special verification for Google Maps local business leads
            if lead.get("lead_type") == "google_maps_no_website" or "Missing Website" in str(lead.get("website_status", "")):
                if lead.get("phone") or lead.get("location"):
                    confidence += 20
                if lead.get("rating", 0) >= 4.0 and lead.get("review_count", 0) >= 15:
                    confidence += 15
                    review_bonus = min(int(lead.get("review_count", 0) / 4), 25)
                    lead["score"] = 65 + review_bonus

            # Email format verification (+20% confidence)
            emails = enrichment.get("hunter_email", {}).get("emails_found", [])
            if emails:
                confidence += 20
                lead["score"] += 10
                lead["contact_details"] = f"{lead.get('contact_title', 'Decision Maker')} ({emails[0]})"

            # Legal Entity Registration status (+15% confidence)
            if enrichment.get("opencorporates", {}).get("current_status") == "Active (Registered)":
                confidence += 15
                lead["score"] += 5

            # Verified Tech Stack Footprint (+15% confidence)
            if lead.get("tech_footprint"):
                confidence += 15

            lead["confidence_score"] = min(confidence, 100)

        # 5. Grade and Filter by Confidence Score Threshold (> min_confidence)
        consolidated_leads = []
        filtered_out_count = 0

        for lead in lead_map.values():
            final_score = min(lead["score"], 100)
            lead["score"] = final_score

            if final_score >= 85:
                lead["grade"] = "A+ (Hot Opportunity)"
            elif final_score >= 70:
                lead["grade"] = "A (High Priority)"
            elif final_score >= 50:
                lead["grade"] = "B (Moderate Priority)"
            else:
                lead["grade"] = "C (Nurture)"

            # Filter logic: confidence score must be strictly greater than threshold (default 60)
            if lead["confidence_score"] > threshold:
                consolidated_leads.append(lead)
            else:
                filtered_out_count += 1

        # Sort by highest score first
        consolidated_leads.sort(key=lambda x: (x["confidence_score"], x["score"]), reverse=True)
        logger.info(
            f"Scoring complete. Retained {len(consolidated_leads)} high-confidence leads (> {threshold}% confidence). "
            f"Filtered out {filtered_out_count} low-confidence leads."
        )
        return consolidated_leads
