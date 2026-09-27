from typing import Dict, Any
from ..utils.logger import get_logger

logger = get_logger("OutreachGenerator")

class OutreachGenerator:
    """
    Generates personalized cold email templates & pitch proposals for Salesforce consulting leads
    based on identified buying signals.
    """

    def generate_pitch(self, lead: Dict[str, Any], consultant_name: str = "Salesforce Solutions Team") -> Dict[str, str]:
        """
        Generates custom email subject and body tailored to the lead's specific Salesforce project needs.
        """
        company = lead.get("company_name", "your company")
        role = lead.get("hiring_signal")
        intent = lead.get("intent_signal")
        techs = ", ".join(lead.get("tech_footprint", [])) or "Salesforce ecosystem"

        if intent and "RFP" in intent:
            subject = f"Response to Salesforce Implementation RFP - {company}"
            body = (
                f"Hi {lead.get('contact_title', 'Decision Maker')},\n\n"
                f"I noticed {company} recently issued an RFP regarding '{intent}'. "
                f"Our team of certified Salesforce Solution Architects and CPQ Specialists has delivered "
                f"over 50+ successful implementations in similar industries.\n\n"
                f"We specialize in accelerating deployment timelines while reducing custom APEX technical debt.\n\n"
                f"Would you be open to a 15-minute intro call this Thursday to discuss how we can support your Salesforce milestone?\n\n"
                f"Best regards,\n{consultant_name}"
            )
        elif role:
            subject = f"Salesforce Consulting & Augmentation support for {role} at {company}"
            body = (
                f"Hi {lead.get('contact_title', 'Hiring Manager')},\n\n"
                f"I saw that {company} is currently recruiting for a {role}.\n\n"
                f"While you search for the right full-time candidate, our team can step in immediately to provide certified Salesforce "
                f"development, LWC custom component builds, and administrative support without long-term overhead.\n\n"
                f"Are you open to a brief conversation on how we can bridge your team's capacity gaps?\n\n"
                f"Best regards,\n{consultant_name}"
            )
        else:
            subject = f"Optimizing {company}'s Salesforce Stack ({techs})"
            body = (
                f"Hi {lead.get('contact_title', 'Team')},\n\n"
                f"Our tech intelligence team noticed that {company} relies on {techs}.\n\n"
                f"We help growth enterprises streamline their Salesforce workflows, integrate third-party APIs, and maximize ROI from Sales & Service Cloud.\n\n"
                f"Would next Tuesday work for a quick audit of your current Salesforce architecture?\n\n"
                f"Best regards,\n{consultant_name}"
            )

        return {
            "subject": subject,
            "body": body
        }
