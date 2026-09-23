from app.services.newsletter import FACT, DERIVED, NARRATIVE, render_email

def test_provenance_kinds_are_explicit():
    assert {FACT, DERIVED, NARRATIVE} == {"SOURCED_FACT","DERIVED_ANALYTIC","AI_NARRATIVE"}

def test_email_renderer_is_email_ready_and_escapes_content():
    brief={"title":"AI Daily Intelligence Brief","items":[{"kind":FACT,"title":"A < B","body":"safe","source":{"name":"WHO"}}]}
    company={"title":"Company Performance & Financial Intelligence","items":[]}
    html=render_email(brief,company)
    assert "<!doctype html>" in html.lower()
    assert "A &lt; B" in html
    assert "SOURCED_FACT" in html

from app.services.newsletter import canonicalize_url, source_item_hash

def test_newsletter_url_canonicalization_strips_fragment_and_trailing_slash():
    assert canonicalize_url("HTTPS://Example.COM/a/#section") == "https://example.com/a"

def test_newsletter_dedup_hash_is_stable():
    a=source_item_hash("FDA approves Product X", "https://example.com/a", "FDA")
    b=source_item_hash("FDA approves Product X", "https://example.com/a", "FDA")
    assert a == b and len(a)==64

def test_email_excludes_unverified_sourced_facts():
    brief={"title":"AI Daily Intelligence Brief","items":[{"kind":FACT,"title":"Unverified","body":"x","source":{"name":"News"},"verification":{"status":"unverified","evidence_level":"E0"}},{"kind":FACT,"title":"Verified","body":"y","source":{"name":"FDA"},"verification":{"status":"verified","evidence_level":"E2"}}]}
    company={"title":"Company Performance & Financial Intelligence","items":[]}
    html=render_email(brief,company)
    assert "Verified" in html and "Unverified" not in html


from datetime import datetime, timezone, timedelta
from types import SimpleNamespace
from app.services.newsletter import delivery_is_due, make_unsubscribe_token, parse_unsubscribe_token

def test_delivery_due_respects_timezone_hour_and_frequency():
    pref=SimpleNamespace(email_enabled=True,suppressed_at=None,timezone="Asia/Riyadh",delivery_hour=8,frequency="daily")
    now=datetime(2026,9,22,6,0,tzinfo=timezone.utc)  # 09:00 Riyadh
    assert delivery_is_due(pref,now,None) is True
    assert delivery_is_due(pref,now,now-timedelta(hours=1)) is False

def test_delivery_not_due_when_suppressed():
    pref=SimpleNamespace(email_enabled=True,suppressed_at=datetime.now(timezone.utc),timezone="UTC",delivery_hour=0,frequency="daily")
    assert delivery_is_due(pref,datetime.now(timezone.utc),None) is False

def test_unsubscribe_token_round_trip(monkeypatch):
    from app import services
    monkeypatch.setattr(services.newsletter.settings,"newsletter_token_secret","test-secret")
    token=make_unsubscribe_token(7,11)
    assert parse_unsubscribe_token(token)==(7,11)
