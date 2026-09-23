def assess_eligibility(tender_requirements, company_facts):
    unmet = []
    checked = []
    for requirement in tender_requirements:
        checked.append(requirement)
        key = requirement.strip().lower().replace(" ", "_")
        if key in company_facts and not bool(company_facts[key]):
            unmet.append(requirement)
    return {
        "eligible": not unmet,
        "checked_requirements": checked,
        "unmet_requirements": unmet,
    }
