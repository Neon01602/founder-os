from typing import Dict, Any


def score_session(brief: Dict[str, Any]) -> Dict[str, Any]:
    """Score each agent's output on accuracy, completeness, and coherence."""

    scores = {}

    # Score Strategist
    market = brief.get("market", {})
    strat_score = 0
    strat_notes = []

    if market.get("market_summary"):
        strat_score += 25
    else:
        strat_notes.append("Missing market summary")

    if market.get("tam", {}).get("value"):
        strat_score += 20
    else:
        strat_notes.append("Missing TAM estimate")

    competitors = market.get("competitors", [])
    if len(competitors) >= 3:
        strat_score += 25
    elif len(competitors) > 0:
        strat_score += 10
        strat_notes.append(f"Only {len(competitors)} competitors identified")
    else:
        strat_notes.append("No competitors identified")

    if market.get("market_gaps"):
        strat_score += 15
    if market.get("market_trends"):
        strat_score += 15

    scores["Strategist"] = {
        "score": min(strat_score, 100),
        "grade": _grade(strat_score),
        "notes": strat_notes or ["All checks passed"],
        "checks": {
            "market_summary": bool(market.get("market_summary")),
            "tam_present": bool(market.get("tam", {}).get("value")),
            "competitors_found": len(competitors) >= 3,
            "gaps_identified": bool(market.get("market_gaps")),
            "trends_identified": bool(market.get("market_trends")),
        },
    }

    # Score User Research
    research = brief.get("research", {})
    res_score = 0
    res_notes = []

    personas = research.get("personas", [])
    if len(personas) >= 3:
        res_score += 30
    elif len(personas) > 0:
        res_score += 15
        res_notes.append(f"Only {len(personas)} personas (need 3+)")
    else:
        res_notes.append("No personas generated")

    for p in personas:
        if p.get("interview_insights"):
            res_score += 5
            break

    if research.get("common_pain_points"):
        res_score += 20
    if research.get("jobs_to_be_done"):
        res_score += 20
    if research.get("buying_triggers"):
        res_score += 15

    scores["User Research"] = {
        "score": min(res_score, 100),
        "grade": _grade(res_score),
        "notes": res_notes or ["All checks passed"],
        "checks": {
            "personas_created": len(personas) >= 3,
            "interviews_simulated": any(p.get("interview_insights") for p in personas),
            "pain_points_found": bool(research.get("common_pain_points")),
            "jtbd_defined": bool(research.get("jobs_to_be_done")),
            "buying_triggers": bool(research.get("buying_triggers")),
        },
    }

    # Score Product
    product = brief.get("product", {})
    prod_score = 0
    prod_notes = []

    features = product.get("core_features", [])
    if len(features) >= 5:
        prod_score += 25
    elif len(features) > 0:
        prod_score += 10
        prod_notes.append(f"Only {len(features)} features defined")
    else:
        prod_notes.append("No features defined")

    if product.get("product_name") and product.get("tagline"):
        prod_score += 15
    if product.get("mvp_scope"):
        prod_score += 20
    if product.get("go_to_market"):
        prod_score += 20
    # FIX: was checking "wireframe_descriptions" which ProductAgent never emits.
    # Changed to "technical_stack" which is always present in the product output.
    if product.get("technical_stack"):
        prod_score += 10
    if product.get("milestones"):
        prod_score += 10

    scores["Product"] = {
        "score": min(prod_score, 100),
        "grade": _grade(prod_score),
        "notes": prod_notes or ["All checks passed"],
        "checks": {
            "features_prioritized": len(features) >= 5,
            "product_named": bool(product.get("product_name")),
            "mvp_scoped": bool(product.get("mvp_scope")),
            "gtm_defined": bool(product.get("go_to_market")),
            "tech_stack_defined": bool(product.get("technical_stack")),
        },
    }

    overall = sum(s["score"] for s in scores.values()) / len(scores)
    scores["overall"] = {
        "score": round(overall),
        "grade": _grade(overall),
    }

    return scores


def _grade(score: float) -> str:
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    elif score >= 60:
        return "D"
    else:
        return "F"
