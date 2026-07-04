#!/usr/bin/env python3
"""
build_compounds.py — Generate src/data/compounds.json: the cross-process compound
pattern layer (collective intelligence).

Each per-process pattern (patterns.json) lives inside one process. Some behaviours
only become visible when several patterns co-occur for the SAME entity within a time
window — e.g. #1 (29th-Day Tactic, Collections) + #22 (Bureau Downgrade, Credit) +
#25 (Duplicate Payment Bait, Cash App) inside 90 days = a bust-out fraud setup that
no single process sees. This file encodes those compound rules; engine.correlate()
evaluates them against a per-entity firing history.

Deterministic (no randomness) so the demo is identical each build.
Re-run:  python scripts/build_compounds.py

Component pattern IDs are verified against patterns.json at build time. Where the
brief's approximate IDs conflicted with the actual library, they were corrected to
keep each compound thematically coherent (see notes on individual compounds).
"""
import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "src", "data", "compounds.json")
PATTERNS = os.path.join(ROOT, "src", "data", "patterns.json")

# Logic: "ALL" = every component must fire; {"min": N, "of": M} = at least N of M.
ALL = "ALL"


def n_of(n, m):
    return {"min": n, "of": m}


COMPOUNDS = [
    {
        "id": "CP-001",
        "name": "Bust-Out Fraud Setup",
        "severity": "critical",
        "description": "Customer simultaneously gaming dispute timing (Collections), requesting duplicate refunds (Cash App), and showing credit deterioration (Credit) — the classic bust-out precursor. No single process sees all three.",
        "componentPatternIds": [1, 22, 25],   # 29th-Day Tactic + Bureau Downgrade + Duplicate Payment Bait
        "logic": ALL,
        "windowDays": 90,
        "entityKey": "KUNNR",
        "themeId": "customer-risk",
        "recommendation": "Immediate credit hold + joint review by Collections, Credit, and Cash App teams. Do not process any refunds until the investigation completes.",
        "kpiImpact": ["DSO", "Bad Debt"],
        "estimatedExposure": 2500000,
    },
    {
        "id": "CP-002",
        "name": "Systematic Revenue Leakage",
        "severity": "high",
        "description": "Dispute splitting, Friday-afternoon slicing, and month-end RMA dumps recurring for the same account — deductions engineered to slip through under review thresholds and close-day noise.",
        "componentPatternIds": [3, 4, 8],   # Dispute Splitting + Friday Afternoon Slicing + Month-End RMA Dump
        "logic": n_of(2, 3),
        "windowDays": 60,
        "entityKey": "KUNNR",
        "themeId": "revenue-leakage",
        "recommendation": "Consolidate the account's deductions into a single dispute case, freeze auto-approval below threshold, and require substantiation before any credit memo posts.",
        "kpiImpact": ["Deduction Auto", "Dispute Cycle"],
        "estimatedExposure": 1400000,
    },
    {
        "id": "CP-003",
        "name": "Credit Deterioration Cascade",
        "severity": "critical",
        "description": "Bust-out precursor velocity, partial breadcrumb payments, and a bureau downgrade stacking up over a quarter — three independent credit-risk tells converging on the same customer.",
        "componentPatternIds": [19, 20, 22],   # Bust-Out Fraud Precursor + Partial Breadcrumbing + Bureau Downgrade
        "logic": n_of(2, 3),
        "windowDays": 120,
        "entityKey": "KUNNR",
        "themeId": "customer-risk",
        "recommendation": "Re-underwrite the account: reduce the credit limit, move to prepay/COD on new orders, and route open AR to priority collections before exposure grows.",
        "kpiImpact": ["Bad Debt", "DSO"],
        "estimatedExposure": 1900000,
    },
    {
        "id": "CP-004",
        "name": "Stalling-to-Write-Off Pipeline",
        "severity": "high",
        "description": "Missing-PO traps, approval musical chairs, a system-migration stall, and portal sabotage chained across half a year — an aging campaign engineered to run the invoice to write-off.",
        "componentPatternIds": [10, 11, 12, 14],   # Missing PO Trap + Approval Musical Chairs + System Migration Stall + Portal Sabotage
        "logic": n_of(3, 4),
        "windowDays": 180,
        "entityKey": "KUNNR",
        "themeId": "collections-efficiency",
        "recommendation": "Escalate to the account owner and legal watch-list; set a hard resolution SLA, disable further stalling loops, and stop the clock before the balance reaches write-off age.",
        "kpiImpact": ["DSO", "Bad Debt"],
        "estimatedExposure": 1100000,
    },
    {
        "id": "CP-005",
        "name": "Cash Application Warfare",
        "severity": "high",
        # brief listed [25,26,27]; #27 (Creeping Payment Terms) is a relationship-abuse
        # pattern, not cash-app. Corrected the third leg to #24 (Remittance Decoupling)
        # so all three components are Cash Application & Remittance Friction patterns.
        "description": "Duplicate-payment bait, unapplied-cash weaponization, and remittance decoupling hitting the cash-application queue together — a deliberate assault on match rates and float.",
        "componentPatternIds": [24, 25, 26],   # Remittance Decoupling + Duplicate Payment Bait + Unapplied Cash Weaponization
        "logic": n_of(2, 3),
        "windowDays": 45,
        "entityKey": "KUNNR",
        "themeId": "cash-application",
        "recommendation": "Quarantine the customer's incoming payments for manual application, reconcile remittances against open items before posting, and claw back any duplicate refunds.",
        "kpiImpact": ["Auto-Match", "DSO"],
        "estimatedExposure": 900000,
    },
    {
        "id": "CP-006",
        "name": "Deduction-Dispute Double Play",
        "severity": "medium",
        "description": "Dispute splitting and Friday slicing on the deduction side, paired with duplicate-payment bait on the cash side — the same customer working both the dispute queue and the cash-app queue at once.",
        "componentPatternIds": [3, 4, 25],   # Dispute Splitting + Friday Afternoon Slicing + Duplicate Payment Bait
        "logic": ALL,
        "windowDays": 60,
        "entityKey": "KUNNR",
        "themeId": "revenue-leakage",
        "recommendation": "Cross-link the deduction and cash-application cases, hold refunds pending dispute resolution, and flag the account for coordinated behaviour review.",
        "kpiImpact": ["Deduction Auto", "Auto-Match"],
        "estimatedExposure": 700000,
    },
    {
        "id": "CP-007",
        "name": "Strategic Account Exploitation",
        "severity": "high",
        "description": "A strategic account using relationship shielding, 29th-day dispute timing, and partial breadcrumb payments — leveraging its importance to stretch terms with impunity.",
        "componentPatternIds": [29, 1, 20],   # Strategic Shielding + 29th-Day Tactic + Partial Breadcrumbing
        "logic": n_of(2, 3),
        "windowDays": 90,
        "entityKey": "KUNNR",
        "themeId": "customer-risk",
        "recommendation": "Elevate to the account executive and CFO sponsor: renegotiate terms, cap shielding, and make continued strategic pricing contingent on payment behaviour.",
        "kpiImpact": ["DSO", "CEI"],
        "estimatedExposure": 1600000,
    },
    {
        "id": "CP-008",
        "name": "Coordinated Payment Avoidance",
        "severity": "medium",
        "description": "A legal-entity shell game, portal sabotage, and partial breadcrumb payments moving in lock-step — a coordinated effort to make paying on time structurally impossible.",
        "componentPatternIds": [13, 14, 20],   # Legal Entity Shell Game + Portal Sabotage + Partial Breadcrumbing
        "logic": ALL,
        "windowDays": 120,
        "entityKey": "KUNNR",
        "themeId": "collections-efficiency",
        "recommendation": "Verify the paying legal entity, restore a working payment channel, and require a firm promise-to-pay with milestone tracking before extending further credit.",
        "kpiImpact": ["DSO", "CEI"],
        "estimatedExposure": 850000,
    },
]


def main():
    patterns = json.load(open(PATTERNS, encoding="utf-8"))["patterns"]
    by_id = {p["id"]: p for p in patterns}

    # verify every component references a real pattern, and N-of-M shapes are sane
    for cp in COMPOUNDS:
        for pid in cp["componentPatternIds"]:
            if pid not in by_id:
                raise SystemExit(f"{cp['id']}: unknown pattern id {pid}")
        if isinstance(cp["logic"], dict):
            of = cp["logic"]["of"]
            if of != len(cp["componentPatternIds"]):
                raise SystemExit(f"{cp['id']}: logic.of={of} != {len(cp['componentPatternIds'])} components")
            if cp["logic"]["min"] > of:
                raise SystemExit(f"{cp['id']}: logic.min > logic.of")

    out = {
        "meta": {
            "title": "ProcessIQ — Cross-Process Compound Patterns",
            "note": "Collective intelligence layer. Each compound fires when specific per-process patterns co-occur for the same entity.",
            "compoundCount": len(COMPOUNDS),
        },
        "compounds": COMPOUNDS,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

    print(f"Wrote compounds.json -> {os.path.relpath(OUT, ROOT)}")
    print(f"{len(COMPOUNDS)} compound patterns (each verified against {len(patterns)} base patterns):")
    for cp in COMPOUNDS:
        logic = "ALL" if cp["logic"] == "ALL" else f"{cp['logic']['min']}-of-{cp['logic']['of']}"
        comps = ", ".join(f"#{pid} {by_id[pid]['name']}" for pid in cp["componentPatternIds"])
        print(f"  {cp['id']} {cp['name']:<30} [{logic}, {cp['windowDays']}d, {cp['severity']}]")
        print(f"        {comps}")


if __name__ == "__main__":
    main()
