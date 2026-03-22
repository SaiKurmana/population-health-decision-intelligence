from mcp.server import FastMCP
from typing import Dict, List
from datetime import datetime

mcp = FastMCP("Population Health Risk Server")


def _normalize_conditions(conditions: List[str]) -> List[str]:
    return [c.strip().lower() for c in conditions if c and c.strip()]


@mcp.tool(description="Assess a patient's readmission risk using simple population health factors")
def assess_readmission_risk(
    age: int,
    chronic_conditions: List[str],
    ed_visits_last_6_months: int = 0,
    inpatient_admissions_last_12_months: int = 0,
    medication_count: int = 0,
    has_behavioral_health_condition: bool = False,
    has_transportation_barrier: bool = False,
    lives_alone: bool = False
) -> Dict:
    try:
        if age < 0:
            raise ValueError("Age cannot be negative")
        if ed_visits_last_6_months < 0 or inpatient_admissions_last_12_months < 0 or medication_count < 0:
            raise ValueError("Visit, admission, and medication counts cannot be negative")

        conditions = _normalize_conditions(chronic_conditions)
        score = 0
        drivers = []

        if age >= 75:
            score += 2
            drivers.append("age 75 or older")
        elif age >= 65:
            score += 1
            drivers.append("age 65 to 74")

        high_impact_conditions = {"chf", "copd", "ckd", "diabetes", "cad", "asthma"}
        matched_conditions = [c for c in conditions if c in high_impact_conditions]
        score += min(len(matched_conditions), 4)
        if matched_conditions:
            drivers.append(f"chronic conditions: {', '.join(matched_conditions)}")

        if ed_visits_last_6_months >= 3:
            score += 3
            drivers.append("frequent ED use")
        elif ed_visits_last_6_months >= 1:
            score += 1
            drivers.append("recent ED utilization")

        if inpatient_admissions_last_12_months >= 2:
            score += 3
            drivers.append("multiple inpatient admissions")
        elif inpatient_admissions_last_12_months == 1:
            score += 2
            drivers.append("recent inpatient admission")

        if medication_count >= 10:
            score += 2
            drivers.append("high medication burden")
        elif medication_count >= 5:
            score += 1
            drivers.append("moderate medication burden")

        if has_behavioral_health_condition:
            score += 2
            drivers.append("behavioral health comorbidity")

        if has_transportation_barrier:
            score += 1
            drivers.append("transportation barrier")

        if lives_alone:
            score += 1
            drivers.append("lives alone")

        if score >= 10:
            tier = "high"
        elif score >= 6:
            tier = "moderate"
        else:
            tier = "low"

        return {
            "success": True,
            "risk_score": score,
            "risk_tier": tier,
            "drivers": drivers,
            "summary": f"Estimated readmission risk is {tier} (score: {score}).",
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@mcp.tool(description="Recommend population health interventions based on risk tier and social/clinical factors")
def recommend_interventions(
    risk_tier: str,
    chronic_conditions: List[str],
    has_transportation_barrier: bool = False,
    medication_count: int = 0,
    lives_alone: bool = False,
    has_behavioral_health_condition: bool = False
) -> Dict:
    try:
        risk_tier = risk_tier.strip().lower()
        if risk_tier not in {"low", "moderate", "high"}:
            raise ValueError("risk_tier must be one of: low, moderate, high")

        conditions = _normalize_conditions(chronic_conditions)
        interventions = []

        if risk_tier == "high":
            interventions.extend([
                "Enroll in intensive care management",
                "Schedule post-discharge follow-up within 7 days",
                "Perform medication reconciliation",
                "Assign care coordinator outreach"
            ])
        elif risk_tier == "moderate":
            interventions.extend([
                "Provide care management outreach",
                "Schedule PCP follow-up",
                "Review adherence barriers"
            ])
        else:
            interventions.extend([
                "Continue routine preventive outreach",
                "Encourage primary care engagement"
            ])

        if "diabetes" in conditions:
            interventions.append("Close diabetes care gaps and monitor A1c follow-up")
        if "chf" in conditions:
            interventions.append("Provide heart failure symptom monitoring and weight check education")
        if "copd" in conditions or "asthma" in conditions:
            interventions.append("Review inhaler adherence and action plan")

        if medication_count >= 8:
            interventions.append("Conduct pharmacist-led polypharmacy review")
        if has_transportation_barrier:
            interventions.append("Arrange transportation support for visits")
        if lives_alone:
            interventions.append("Assess social support and home-based follow-up needs")
        if has_behavioral_health_condition:
            interventions.append("Coordinate behavioral health follow-up")

        return {
            "success": True,
            "risk_tier": risk_tier,
            "recommended_interventions": interventions,
            "intervention_count": len(interventions),
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@mcp.tool(description="Stratify a population health member into a utilization and care management segment")
def stratify_population_member(
    age: int,
    chronic_condition_count: int,
    ed_visits_last_6_months: int = 0,
    inpatient_admissions_last_12_months: int = 0,
    has_social_barriers: bool = False
) -> Dict:
    try:
        if age < 0 or chronic_condition_count < 0:
            raise ValueError("Age and chronic_condition_count must be non-negative")

        if inpatient_admissions_last_12_months >= 2 or ed_visits_last_6_months >= 3:
            segment = "rising_or_high_utilizer"
            rationale = "High recent utilization pattern"
        elif chronic_condition_count >= 3 and has_social_barriers:
            segment = "complex_chronic_with_social_needs"
            rationale = "Multiple chronic conditions plus social barriers"
        elif chronic_condition_count >= 2 or age >= 65:
            segment = "chronic_care_management"
            rationale = "Needs longitudinal chronic care support"
        else:
            segment = "prevention_and_wellness"
            rationale = "Lower complexity, focus on prevention"

        return {
            "success": True,
            "segment": segment,
            "rationale": rationale,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


if __name__ == "__main__":
    print(f"🚀 Starting {mcp.name}...")
    mcp.run(transport="stdio")