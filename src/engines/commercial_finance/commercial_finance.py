"""PharmaLens AI - Project 19: Commercial Finance & Budget Intelligence."""
import numpy as np

def build_budget(target_gross_sales,gtn_rate,cogs_rate,commercial_spend):
    gtn=target_gross_sales*gtn_rate; net=target_gross_sales-gtn; cogs=net*cogs_rate
    contribution=net-cogs; after_spend=contribution-commercial_spend
    return {'target_gross_sales':target_gross_sales,'gtn':gtn,'target_net_sales':net,'cogs':cogs,'contribution':contribution,'commercial_spend':commercial_spend,'contribution_after_spend':after_spend,'roci':after_spend/commercial_spend if commercial_spend else np.nan}

def gtn_net_price(gross_sales,units,gtn_rate):
    gtn=gross_sales*gtn_rate; net=gross_sales-gtn
    return {'gross_sales':gross_sales,'gtn':gtn,'net_sales':net,'gross_price':gross_sales/units if units else np.nan,'net_price':net/units if units else np.nan}

def price_volume_analysis(base_price,base_volume,new_price,new_volume):
    base=base_price*base_volume; new=new_price*new_volume
    return {'base_revenue':base,'new_revenue':new,'price_effect':(new_price-base_price)*base_volume,'volume_effect':(new_volume-base_volume)*base_price,'interaction':(new_price-base_price)*(new_volume-base_volume),'total_variance':new-base,'variance_pct':(new-base)/base if base else np.nan}

def reforecast_ytd(ytd_actual,months_elapsed,annual_target):
    run_rate=ytd_actual/max(months_elapsed,1); forecast=ytd_actual+run_rate*(12-months_elapsed)
    return {'ytd_actual':ytd_actual,'annual_target':annual_target,'run_rate_monthly':run_rate,'fy_reforecast':forecast,'gap_vs_target':forecast-annual_target,'forecast_achievement':forecast/annual_target if annual_target else np.nan}

def fx_impact(foreign_sales,old_fx,new_fx):
    old=foreign_sales*old_fx; new=foreign_sales*new_fx
    return {'old_egp_sales':old,'new_egp_sales':new,'fx_impact_egp':new-old,'fx_impact_pct':(new-old)/old if old else np.nan}

def incentive_multiplier(achievement):
    if achievement<.80:return 0.0
    if achievement<1:return .50
    if achievement<1.10:return 1.00
    if achievement<1.20:return 1.25
    return 1.50

def commercial_decision(achievement,roci,commercial_spend):
    actions=[]
    if achievement<.90: actions.append('Review target realism, execution and regional/channel drivers.')
    elif achievement>=1.10: actions.append('Protect momentum; assess incremental investment using marginal ROCI.')
    if roci<.50: actions.append('Investigate commercial spend efficiency.')
    elif roci>1.50: actions.append('Consider scaling investment subject to marginal-return validation.')
    if commercial_spend>100_000_000: actions.append('Trigger commercial-spend deep dive and ROI validation.')
    return ' '.join(actions) if actions else 'Monitor performance.'
