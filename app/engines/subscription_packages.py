TIER_ORDER = ["free_demo", "professional", "team", "enterprise"]

SUBSCRIPTION_PACKAGES = [
    {
        "id": "free_demo", "name": "Free Demo", "audience": "New users",
        "description": "Synthetic demonstrations and a limited evidence-to-decision trial.",
        "billingStatus": "not_configured",
        "entitlements": {"maxFilesPerBatch": 1, "maxFileSizeMb": 25, "maxRunsPerMonth": 5, "maxCopilotQuestionsPerMonth": 5, "canExportBrandedReports": True, "maxWorkspaceMembers": 1, "apiAccess": False, "sso": False},
    },
    {
        "id": "professional", "name": "Professional", "audience": "Individual pharma professionals",
        "description": "Private workspace analysis with expanded runs, Copilot, and branded exports.",
        "billingStatus": "not_configured",
        "entitlements": {"maxFilesPerBatch": 10, "maxFileSizeMb": 25, "maxRunsPerMonth": 100, "maxCopilotQuestionsPerMonth": 100, "canExportBrandedReports": True, "maxWorkspaceMembers": 1, "apiAccess": False, "sso": False},
    },
    {
        "id": "team", "name": "Team", "audience": "Cross-functional pharmaceutical teams",
        "description": "Shared workspace decision workflows with team membership and higher limits.",
        "billingStatus": "not_configured",
        "entitlements": {"maxFilesPerBatch": 10, "maxFileSizeMb": 50, "maxRunsPerMonth": 500, "maxCopilotQuestionsPerMonth": 500, "canExportBrandedReports": True, "maxWorkspaceMembers": 10, "apiAccess": False, "sso": False},
    },
    {
        "id": "enterprise", "name": "Enterprise", "audience": "Pharmaceutical organizations",
        "description": "Negotiated controls for organization-wide governance, SSO, and API access.",
        "billingStatus": "not_configured",
        "entitlements": {"maxFilesPerBatch": 10, "maxFileSizeMb": 250, "maxRunsPerMonth": 10000, "maxCopilotQuestionsPerMonth": 10000, "canExportBrandedReports": True, "maxWorkspaceMembers": 1000, "apiAccess": True, "sso": True},
    },
]


def get_subscription_package(package_id: str):
    return next((p for p in SUBSCRIPTION_PACKAGES if p["id"] == package_id), None)


def get_upgrade_state(current: str, target: str) -> str:
    if current == target:
        return "current"
    if target == "enterprise":
        return "contact_sales"
    return "upgrade_available" if TIER_ORDER.index(target) > TIER_ORDER.index(current) else "current"


def get_next_subscription_tier(current: str) -> str | None:
    next_index = TIER_ORDER.index(current) + 1
    return TIER_ORDER[next_index] if next_index < len(TIER_ORDER) else None
