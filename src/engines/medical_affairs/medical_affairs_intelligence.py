import pandas as pd
import numpy as np

def _norm(s):
    s=pd.to_numeric(s,errors="coerce").fillna(0)
    return pd.Series(np.where(s.max()==s.min(), (s>0).astype(float), (s-s.min())/(s.max()-s.min())),index=s.index)

def score_kols(df):
    x=df.copy(); weights={"publication_count":.25,"citation_count":.20,"clinical_trial_count":.20,"institutional_reach":.15,"conference_activity":.10,"digital_scientific_activity":.10}
    parts=[]; total=0
    for c,w in weights.items():
        if c in x: parts.append(_norm(x[c])*w); total+=w
    x["kol_influence_score"]=(sum(parts)/total*100) if parts else 0
    x["kol_tier"]=pd.cut(x["kol_influence_score"],[-.1,25,50,75,100.1],labels=["Emerging","Established","High Influence","Strategic KOL"])
    return x

def scientific_landscape(df):
    if "topic" not in df: raise ValueError("publications must contain topic")
    x=df.groupby("topic",dropna=False).size().reset_index(name="publication_count")
    x["topic_activity_score"]=_norm(x["publication_count"])*100
    return x.sort_values("topic_activity_score",ascending=False)

def publication_intelligence(df):
    x=df.copy()
    for c in ["citation_count","journal_impact_factor","recency_score"]:
        if c not in x: x[c]=0
    x["publication_score"]=(.4*_norm(x.citation_count)+.3*_norm(x.journal_impact_factor)+.3*_norm(x.recency_score))*100
    return x.sort_values("publication_score",ascending=False)

def clinical_trial_landscape(df):
    dims=[c for c in ["sponsor","indication","phase","status"] if c in df]
    return df.groupby(dims,dropna=False).size().reset_index(name="trial_count").sort_values("trial_count",ascending=False) if dims else pd.DataFrame({"trial_count":[len(df)]})

def competitor_pipeline(df):
    x=df.copy()
    for c in ["phase_score","commercial_potential","launch_probability"]:
        if c not in x: x[c]=0
    x["pipeline_opportunity_score"]=(.3*_norm(x.phase_score)+.4*_norm(x.commercial_potential)+.3*_norm(x.launch_probability))*100
    return x.sort_values("pipeline_opportunity_score",ascending=False)

def evidence_landscape(df):
    x=df.copy()
    for c in ["study_count","publication_count","guideline_mentions","evidence_quality"]:
        if c not in x: x[c]=0
    x["evidence_strength_score"]=(.25*_norm(x.study_count)+.25*_norm(x.publication_count)+.2*_norm(x.guideline_mentions)+.3*_norm(x.evidence_quality))*100
    x["evidence_gap_flag"]=np.where(x.evidence_strength_score<40,"High Gap",np.where(x.evidence_strength_score<65,"Moderate Gap","Low Gap"))
    return x.sort_values("evidence_strength_score")

def medical_education_opportunities(df):
    x=df.copy()
    for c in ["unmet_need","hcp_gap","scientific_momentum","target_reach"]:
        if c not in x: x[c]=0
    x["education_opportunity_score"]=(.3*_norm(x.unmet_need)+.25*_norm(x.hcp_gap)+.25*_norm(x.scientific_momentum)+.2*_norm(x.target_reach))*100
    return x.sort_values("education_opportunity_score",ascending=False)

def advisory_board_plan(kols,n=8):
    return score_kols(kols).nlargest(n,"kol_influence_score")

def medical_commercial_opportunities(market,medical,key="indication"):
    x=market.merge(medical,on=key,how="outer",suffixes=("_commercial","_medical")).fillna(0)
    cc=[c for c in ["growth","market_opportunity_score","market_share_gap"] if c in x]
    mc=[c for c in ["evidence_gap_score","scientific_momentum","kol_influence_score"] if c in x]
    x["commercial_signal"]=sum(_norm(x[c]) for c in cc)/max(1,len(cc))*100
    x["medical_signal"]=sum(_norm(x[c]) for c in mc)/max(1,len(mc))*100
    x["integrated_opportunity_score"]=.55*x.commercial_signal+.45*x.medical_signal
    return x.sort_values("integrated_opportunity_score",ascending=False)
