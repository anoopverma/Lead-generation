from typing import List, Dict, Any
from ..utils.logger import get_logger

logger = get_logger("LeadScorer")

class LeadScorer:
    """
    Evaluates and ranks Salesforce project leads based on multi-channel signals:
    - Hiring Signal Weight (e.g. 40 points)
    - Tech Stack Footprint Weight (e.g. 30 points)
    - Buyer Intent / RFP Weight (e.g. 30 points)
    """

    def score_and_merge_leads(
        self,
        job_leads: List[Dict[str, Any]],
        tech_scans: List[Dict[str, Any]],
        intent_leads: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Merges multi-source signals by domain / company and assigns a consolidated lead score (0-100).
        """
        logger.info("Merging lead sources and calculating Salesforce project lead scores...")
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
                "tech_footprint": [],
                "intent_signal": None,
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
                    "tech_footprint": [],
                    "intent_signal": lead["intent_signal"],
                    "budget": lead.get("estimated_budget", "Unknown"),
                    "contact_title": lead.get("contact_title", "VP of IT / Sales Ops"),
                    "score": 50  # 50 pts for RFP/Intent signal
                }
            else:
                lead_map[key]["intent_signal"] = lead["intent_signal"]
                lead_map[key]["budget"] = lead.get("estimated_budget", "Unknown")
                lead_map[key]["contact_title"] = lead.get("contact_title", "VP of IT / Sales Ops")
                lead_map[key]["score"] += 40  # Stack intent onto hiring

        # 3. Process Tech Stack Scans
        tech_map = {item["domain"]: item for item in tech_scans}
        for key, lead in lead_map.items():
            domain = lead["domain"]
            if domain in tech_map and tech_map[domain]["has_salesforce"]:
                techs = tech_map[domain]["detected_technologies"]
                lead["tech_footprint"] = techs
                lead["score"] += 20 + min(len(techs) * 5, 10)  # Add points for existing SF tech

        # Convert to list and grade
        consolidated_leads = []
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

            consolidated_leads.append(lead)

        # Sort by highest score first
        consolidated_leads.sort(key=lambda x: x["score"], reverse=True)
        logger.info(f"Scored {len(consolidated_leads)} unique Salesforce project leads.")
        return consolidated_leads
