#!/usr/bin/env python3
"""
build_themes.py — Generate src/data/themes.json: the executive theme layer.

A CFO doesn't think "DSO" and "DPO" separately — they think "Cash Conversion Cycle"
= DSO + DIO − DPO across three processes. This file rolls the flat per-process KPIs
(roi.json) up into CFO-level outcome themes, each with a composite KPI, the per-
function components that compose it, and the patterns that drive it.

For cross-function themes (Working Capital, Customer Risk) the non-O2C components use
illustrative stub values (P2P DPO, SC DIO) until those function pattern libraries are
built out. patternContributors reference real ids from patterns.json (verified here).

Deterministic. Re-run:  python scripts/build_themes.py
"""
import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "src", "data", "themes.json")
PATTERNS = os.path.join(ROOT, "src", "data", "patterns.json")

# Theme definitions. Each composite KPI carries its per-function components and the
# pattern ids (from patterns.json) that drive the contributing KPIs. `method` selects
# how the composite before/after is computed from the components:
#   "signed"   — sum with per-component sign (CCC = DSO + DIO − DPO)
#   "weighted" — weighted average of component values (a blended %/index)
THEMES = [
    {
        "id": "working-capital",
        "name": "Working Capital Optimization",
        "icon": "$",
        "executiveQuestion": "How much cash is trapped in the receivables cycle?",
        "annualImpact": 4_200_000,
        "themeKPIs": [{
            "id": "ccc",
            "name": "Cash Conversion Cycle",
            "formula": "DSO + DIO − DPO",
            "unit": "days",
            "method": "signed",
            "components": [
                {"kpiId": "DSO", "functionId": "o2c", "functionName": "Order-to-Cash",
                 "direction": "down", "sign": 1, "weight": 0.4, "before": 45, "after": 35},
                {"kpiId": "DIO", "functionId": "sc", "functionName": "Supply Chain",
                 "direction": "down", "sign": 1, "weight": 0.3, "before": 62, "after": 55},
                {"kpiId": "DPO", "functionId": "p2p", "functionName": "Procure-to-Pay",
                 "direction": "up", "sign": -1, "weight": 0.3, "before": 38, "after": 45},
            ],
            "patternContributors": [1, 17, 20, 27, 30, 31],
        }],
    },
    {
        "id": "revenue-assurance",
        "name": "Revenue Assurance",
        "icon": "⊘",
        "executiveQuestion": "How much revenue are we leaking to disputes and deductions?",
        "annualImpact": 2_100_000,
        "themeKPIs": [{
            "id": "nrr",
            "name": "Net Revenue Retention",
            "formula": "Weighted(CEI, Dispute Win Rate, Deduction Recovery)",
            "unit": "%",
            "method": "weighted",
            "components": [
                {"kpiId": "CEI", "functionId": "o2c", "functionName": "Order-to-Cash",
                 "direction": "up", "sign": 1, "weight": 0.4, "before": 72, "after": 90},
                {"kpiId": "Dispute Win Rate", "functionId": "o2c", "functionName": "Order-to-Cash",
                 "direction": "up", "sign": 1, "weight": 0.3, "before": 58, "after": 80},
                {"kpiId": "Deduction Recovery", "functionId": "o2c", "functionName": "Order-to-Cash",
                 "direction": "up", "sign": 1, "weight": 0.3, "before": 40, "after": 72},
            ],
            "patternContributors": [3, 4, 5, 7, 8, 28],
        }],
    },
    {
        "id": "customer-risk",
        "name": "Customer Risk Exposure",
        "icon": "⚠",
        "executiveQuestion": "What's our concentration risk across the customer base?",
        "annualImpact": 1_900_000,
        "themeKPIs": [{
            "id": "wrs",
            "name": "Weighted Risk Score",
            "formula": "Weighted(Credit Score, Payment Behavior, Dispute Frequency)",
            "unit": "index",
            "method": "weighted",
            "components": [
                {"kpiId": "Credit Score Risk", "functionId": "o2c", "functionName": "Credit & Risk (O2C)",
                 "direction": "down", "sign": 1, "weight": 0.4, "before": 62, "after": 45},
                {"kpiId": "Payment Behavior", "functionId": "o2c", "functionName": "Collections (O2C)",
                 "direction": "down", "sign": 1, "weight": 0.35, "before": 55, "after": 38},
                {"kpiId": "Dispute Frequency", "functionId": "o2c", "functionName": "Disputes (O2C)",
                 "direction": "down", "sign": 1, "weight": 0.25, "before": 48, "after": 30},
            ],
            "patternContributors": [19, 20, 21, 22, 23],
        }],
    },
    {
        "id": "process-efficiency",
        "name": "Process Efficiency",
        "icon": "⚡",
        "executiveQuestion": "Are we scaling with automation or staffing with headcount?",
        "annualImpact": 1_500_000,
        "themeKPIs": [{
            "id": "touchless",
            "name": "Touchless Rate",
            "formula": "Weighted(Auto-Match, Auto-Deduction, STP Rate)",
            "unit": "%",
            "method": "weighted",
            "components": [
                {"kpiId": "Auto-Match", "functionId": "o2c", "functionName": "Cash Application (O2C)",
                 "direction": "up", "sign": 1, "weight": 0.4, "before": 35, "after": 85},
                {"kpiId": "Auto-Deduction", "functionId": "o2c", "functionName": "Deductions (O2C)",
                 "direction": "up", "sign": 1, "weight": 0.3, "before": 0, "after": 40},
                {"kpiId": "STP Rate", "functionId": "o2c", "functionName": "Order-to-Cash",
                 "direction": "up", "sign": 1, "weight": 0.3, "before": 48, "after": 82},
            ],
            "patternContributors": [24, 25, 26, 6, 9],
        }],
    },
]


def composite(kpi, phase):
    """phase = 'before' | 'after'. Compute the composite KPI from its components."""
    if kpi["method"] == "signed":
        return round(sum(c["sign"] * c[phase] for c in kpi["components"]))
    # weighted average
    return round(sum(c["weight"] * c[phase] for c in kpi["components"]))


def main():
    patterns = json.load(open(PATTERNS, encoding="utf-8"))["patterns"]
    ids = {p["id"] for p in patterns}
    by_id = {p["id"]: p for p in patterns}

    for th in THEMES:
        for kpi in th["themeKPIs"]:
            for pid in kpi["patternContributors"]:
                if pid not in ids:
                    raise SystemExit(f"{th['id']}: unknown pattern id {pid}")
            kpi["compositeBefore"] = composite(kpi, "before")
            kpi["compositeAfter"] = composite(kpi, "after")

    out = {
        "meta": {
            "title": "ProcessIQ — Executive Theme Layer",
            "note": "CFO-level outcome themes that roll up KPIs across functions and link to driving patterns.",
            "themeCount": len(THEMES),
        },
        "themes": THEMES,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

    print(f"Wrote themes.json -> {os.path.relpath(OUT, ROOT)}")
    print(f"{len(THEMES)} executive themes:")
    for th in THEMES:
        k = th["themeKPIs"][0]
        fns = ", ".join(sorted({c["functionId"] for c in k["components"]}))
        pats = ", ".join(f"#{pid}" for pid in k["patternContributors"])
        print(f"  {th['id']:<20} {k['name']:<26} {k['compositeBefore']}->{k['compositeAfter']} {k['unit']:<5} [{fns}]")
        print(f"        drivers: {pats}")


if __name__ == "__main__":
    main()
