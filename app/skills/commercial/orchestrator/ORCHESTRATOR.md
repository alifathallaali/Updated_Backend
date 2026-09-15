# Pharma Marketing Orchestrator

## Purpose
Select and sequence pharmaceutical marketing skills based on the business question.

## Routing logic
- Market size/share/growth → market-analysis
- Customer/HCP grouping → hcp-segmentation
- Product/market grouping → pharma-segmentation
- Differentiation/value proposition → brand-positioning
- Competitor threat/messaging → competitive-intelligence
- Overall direction → brand-strategy
- Campaign execution → campaign-planning
- New product → launch-strategy
- Field force → sales-force-effectiveness
- Annual integrated plan → brand-plan

## Orchestration rules
1. Identify the business objective.
2. Identify available data.
3. Identify missing critical data.
4. Select minimum required skills.
5. Run skills in dependency order.
6. Validate contradictions.
7. Separate evidence, calculations, assumptions and recommendations.
8. Produce executive and detailed outputs.

## Example
Request: "Build the 2027 plan for Product X."

Suggested sequence:
market-analysis → hcp-segmentation → competitive-intelligence →
brand-positioning → brand-strategy → campaign-planning →
sales-force-effectiveness → brand-plan
