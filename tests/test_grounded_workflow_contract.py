from app.schemas import CopilotAsk, ProductRunRefreshRequest

def test_copilot_grounding_defaults():
    body=CopilotAsk(workspace_id=1,message="why did sales decline?")
    assert body.auto_run is True
    assert body.persona is None

def test_refresh_contract():
    body=ProductRunRefreshRequest(workspace_id=1,dataset_version_id=3)
    assert body.dataset_version_id==3
