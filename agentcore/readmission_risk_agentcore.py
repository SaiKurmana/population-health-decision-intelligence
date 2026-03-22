from mcp.server.fastmcp import FastMCP
from typing import Dict, List
from datetime import datetime

mcp = FastMCP(host="0.0.0.0", stateless_http=True)

def _normalize_conditions(conditions: List[str]) -> List[str]:
    return [c.strip().lower() for c in conditions if c and c.strip()]

@mcp.tool()
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
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    print("🚀 Starting Pop Health MCP Server...")
    mcp.run(transport="streamable-http")