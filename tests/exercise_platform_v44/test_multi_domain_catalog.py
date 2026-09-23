from src.exercises.registry import registry
from src.exercises.catalog import (BUSINESS_DEVELOPMENT_EXERCISE_DEFINITIONS, MARKET_ACCESS_EXERCISE_DEFINITIONS, LAUNCH_EXERCISE_DEFINITIONS, PORTFOLIO_EXERCISE_DEFINITIONS, FINANCE_EXERCISE_DEFINITIONS)

CASES=[(BUSINESS_DEVELOPMENT_EXERCISE_DEFINITIONS,"BD",20,"Business Development"),(MARKET_ACCESS_EXERCISE_DEFINITIONS,"MAX",15,"Market Access"),(LAUNCH_EXERCISE_DEFINITIONS,"LCH",15,"Launch Excellence"),(PORTFOLIO_EXERCISE_DEFINITIONS,"PRT",15,"Portfolio Strategy"),(FINANCE_EXERCISE_DEFINITIONS,"FIN",15,"Commercial Finance")]

def test_multi_domain_ids_and_registration():
    for defs,prefix,count,domain in CASES:
        ids=[d.id for d in defs]
        assert ids == [f"{prefix}-{i:03d}" for i in range(1,count+1)]
        assert len(ids)==len(set(ids))
        for d in defs:
            assert d.domain==domain
            assert registry.get(d.id).version=="1.0"

def test_catalog_metadata_does_not_claim_verified_bindings():
    for defs,_,_,_ in CASES:
        for d in defs:
            assert "semantic verification" in d.methodology.lower()
            assert d.data_classification=="INTERNAL"

def test_fin_008_remains_registered():
    d=registry.get("FIN-008")
    assert d.name == "Price Volume Analysis"
