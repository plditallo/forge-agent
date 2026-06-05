import json
import anthropic

client = anthropic.Anthropic()

SCORING_PROMPT = """
You are the FORGE Data Asset Scoring Agent. Your job is to evaluate a data asset and score it 
across eight dimensions plus four monetization metrics using the FORGE Data Product Readiness 
Scorecard.

Each dimension is scored 0-5. Use the criteria below strictly.

DIMENSION SCORING CRITERIA:

1. Data Quality (weight 20%)
   0=Corrupt/unusable, 1=Significant missing values, 2=Frequent quality issues,
   3=Mostly accurate with some remediation, 4=High quality minor exceptions, 
   5=Trusted with automated validation

2. Reliability & Consistency (weight 15%)
   0=Unpredictable changes, 1=Major inconsistencies, 2=Reconciliation often required,
   3=Stable with occasional issues, 4=Consistent and auditable, 5=Highly reliable with monitoring

3. Refresh Frequency (weight 10%)
   0=Unknown, 1=Annual, 2=Quarterly, 3=Monthly, 4=Weekly/Daily, 5=Near real-time
   Also factor in refresh reliability.

4. Compliance & Regulatory (weight 15%)
   0=Unknown, 1=Significant violations, 2=Partial compliance, 3=Meets minimum,
   4=Auditable controls, 5=Certified/compliant

5. Governance & Lineage (weight 10%)
   0=No owner, 1=Informal ownership, 2=Partial documentation, 3=Assigned steward,
   4=Full lineage documented, 5=Automated lineage and stewardship

6. Accessibility & Usability (weight 10%)
   0=Personal spreadsheet, 1=Shared drive only, 2=Repository minimal docs,
   3=Structured repository, 4=Searchable catalog, 5=API or product-ready

7. Business Relevance (weight 10%)
   0=No identified use, 1=Historical curiosity, 2=Internal reporting only,
   3=Operational decision support, 4=Strategic value, 5=Direct monetization potential

8. Sustainability & Risk (weight 10%)
   0=Single person dependency, 1=High operational risk, 2=Limited backup,
   3=Supportable, 4=Team supported, 5=Institutionalized asset

MONETIZATION METRICS (scored 0-5, not weighted):

9. Uniqueness: Can competitors obtain this data elsewhere?
   0=Freely available, 3=Somewhat unique, 5=Proprietary and irreplaceable

10. Coverage: How complete is the market/population represented?
    0=Tiny sample, 3=Moderate coverage, 5=Comprehensive/national coverage

11. Historical Depth: How many years of data exist?
    0=Less than 1 year, 2=1-3 years, 3=3-5 years, 5=5+ years

12. Enrichment Potential: Can this be joined with other datasets to increase value?
    0=Isolated, no join potential, 3=Some enrichment possible, 5=High enrichment potential

METAL RATING SCALE:
0-49: Coal | 50-59: Iron | 60-69: Bronze | 70-79: Silver | 80-89: Gold | 90-95: Platinum | 96-100: Diamond

WEIGHTED SCORE FORMULA:
(Quality*0.20) + (Reliability*0.15) + (Refresh*0.10) + (Compliance*0.15) + 
(Governance*0.10) + (Accessibility*0.10) + (BusinessRelevance*0.10) + (Sustainability*0.10)
Multiply result by 20 to get 0-100 scale.

You will receive:
- File profile: column names, data types, row count, null rates, sample values
- Intake questionnaire answers

Respond ONLY with a JSON object, no preamble, no markdown fences. Structure:
{
  "scores": {
    "data_quality": <0-5>,
    "reliability": <0-5>,
    "refresh": <0-5>,
    "compliance": <0-5>,
    "governance": <0-5>,
    "accessibility": <0-5>,
    "business_relevance": <0-5>,
    "sustainability": <0-5>,
    "uniqueness": <0-5>,
    "coverage": <0-5>,
    "historical_depth": <0-5>,
    "enrichment": <0-5>
  },
  "weighted_score": <0-100>,
  "metal_rating": "<Coal|Iron|Bronze|Silver|Gold|Platinum|Diamond>",
  "score_reasoning": {
    "data_quality": "<one sentence explanation>",
    "reliability": "<one sentence explanation>",
    "refresh": "<one sentence explanation>",
    "compliance": "<one sentence explanation>",
    "governance": "<one sentence explanation>",
    "accessibility": "<one sentence explanation>",
    "business_relevance": "<one sentence explanation>",
    "sustainability": "<one sentence explanation>"
  },
  "recommended_actions": [
    "<action 1>",
    "<action 2>",
    "<action 3>"
  ],
  "monetization_potential": {
    "internal_reporting": "<High|Medium|Low>",
    "analytics_product": "<High|Medium|Low>",
    "api_product": "<High|Medium|Low>",
    "marketplace_product": "<High|Medium|Low>",
    "licensing_product": "<High|Medium|Low>"
  }
}
"""


def build_assessment_prompt(file_profile: dict, intake_answers: dict) -> str:
    return f"""
FILE PROFILE:
{json.dumps(file_profile, indent=2)}

INTAKE QUESTIONNAIRE ANSWERS:
{json.dumps(intake_answers, indent=2)}

Score this data asset using the FORGE rubric.
"""


def run_scoring(file_profile: dict, intake_answers: dict) -> dict:
    prompt = build_assessment_prompt(file_profile, intake_answers)

    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=2000,
        system=SCORING_PROMPT,
        messages=[{"role": "user", "content": prompt}]
    )

    raw = response.content[0].text.strip()

    try:
        result = json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"Scoring agent returned invalid JSON: {e}\nRaw response: {raw}")

    return result