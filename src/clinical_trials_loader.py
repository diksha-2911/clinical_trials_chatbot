import json
from langchain_core.documents import Document

def load_clinical_trials(json_path: str):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    documents = []

    studies = data.get("studies", [])

    for study in studies:
        protocol = study.get("protocolSection", {})

        identification = protocol.get("identificationModule", {})
        status_module = protocol.get("statusModule", {})
        design_module = protocol.get("designModule", {})
        conditions_module = protocol.get("conditionsModule", {})
        description_module = protocol.get("descriptionModule", {})
        eligibility_module = protocol.get("eligibilityModule", {})
        interventions_module = protocol.get("armsInterventionsModule", {})

        title = identification.get("briefTitle", "Unknown Title")

        conditions = conditions_module.get("conditions", [])

        phases = design_module.get("phases", [])

        status = status_module.get("overallStatus", "Unknown")

        summary = description_module.get("briefSummary", "")

        eligibility = eligibility_module.get("eligibilityCriteria", "")

        interventions = interventions_module.get("interventions", [])

        intervention_names = [
            i.get("name", "")
            for i in interventions
        ]

        text = f'''
Title: {title}

Conditions: {", ".join(conditions)}

Phase: {", ".join(phases)}

Status: {status}

Interventions: {", ".join(intervention_names)}

Summary:
{summary}

Eligibility:
{eligibility}
'''

        doc = Document(
            page_content=text,
            metadata={
                "title": title,
                "conditions": conditions,
                "phase": phases,
                "status": status
            }
        )

        documents.append(doc)

    return documents