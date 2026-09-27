from typing import List, Dict, Any
from ..utils.logger import get_logger

logger = get_logger("LeadScorer")

class LeadScorer:
    """
    Evaluates and ranks Salesforce project leads based on multi-channel signals and confidence verification:
    - Lead Score (0-100): Buying intent & project value potential
    - Confidence Score (0-100%): Signal verification, email deliverability, and legal entity validation
    - Filters out low-confidence leads below threshold (default > 60%)
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
        and filters leads with confidence_score > min_confidence (default 60).
        """
        threshold = min_confidence if min_confidence is not None else self.min_confidence_score
        logger.info(f"Merging lead sources, calculating confidence scores, and filtering for confidence > {threshold}%...")
        
        lead_map: Dict[str, Dict[str, Any]] = {}

        # 1. Process Job Signals
        for lead in job_leads:
            company = lead["company_name"]
            domain = lead.get("domain", "")
            key = domain or company.lower()

            lead_map[key] = {
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

        # 2. Process Intent Signals
        for lead in intent_leads:
            company = lead["company_name"]
            domain = lead.get("domain", "")
            key = domain or company.lower()

            if key not in lead_map:
                lead_map[key] = {
                    "company_name": company,
                    "domain": domain,
                    "hiring_signal": None,
                    "hiring_count": 0,
                    "location": "N/A",
                    "project_description": lead["intent_signal"],
                    "timeline": lead.get("target_timeframe", "Q4 2026"),
                    "budget": lead.get("estimated_budget", "$100k - $250k"),
                    "contact_title": lead.get("contact_title", "VP of IT / Sales Operations"),
                    "contact_details": f"{lead.get('contact_title', 'VP of IT')} (contact@{domain})",
                    "tech_footprint": [],
                    "intent_signal": lead["intent_signal"],
                    "enrichment": lead.get("enrichment", {}),
                    "score": 50  # 50 pts for RFP/Intent signal
                }
            else:
                lead_map[key]["intent_signal"] = lead["intent_signal"]
                lead_map[key]["project_description"] = f"{lead_map[key]['project_description']} | RFP: {lead['intent_signal']}"
                lead_map[key]["timeline"] = lead.get("target_timeframe", lead_map[key]["timeline"])
                lead_map[key]["budget"] = lead.get("estimated_budget", lead_map[key]["budget"])
                lead_map[key]["contact_title"] = lead.get("contact_title", lead_map[key]["contact_title"])
                lead_map[key]["contact_details"] = f"{lead_map[key]['contact_title']} (contact@{domain})"
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
            confidence = 50  # Base confidence for signal detection
            enrichment = lead.get("enrichment", {})

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
