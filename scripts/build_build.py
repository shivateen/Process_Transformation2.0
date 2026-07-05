#!/usr/bin/env python3
"""
build_build.py — Generate src/data/build.json
Action block decompositions (BPT integration layer, Stage 3 · Build).

Each abstract action block from the pattern library is decomposed into concrete,
activity-level executable blueprints with SIPOC, technology fitment (Agentic AI /
Workflow / RPA / Manual), and process-optimization opportunities.

20 key blocks are hand-crafted; every other block gets a template decomposition
derived from its verb + noun. Deterministic. Re-run:  python scripts/build_build.py
"""
import json, os, copy

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "src", "data", "build.json")
PATTERNS = os.path.join(ROOT, "src", "data", "patterns.json")

FIT_LABEL = {"agentic": "Agentic AI", "workflow": "Workflow", "rpa": "RPA / Rule-based", "manual": "Manual"}
FIT_REASON = {
    "agentic": "Structured, deterministic operation on the system of record — no human judgment required",
    "workflow": "AI-assisted, but requires structured review before proceeding",
    "rpa": "Codified business rules — rule-based execution, no judgment",
    "manual": "Human judgment or financial / legal authority required",
}
DUR = {"agentic": "< 1s", "workflow": "1-2s", "rpa": "< 1s", "manual": "Variable"}


def prettify(token):
    return token.replace("(", " (").replace("_", " ").replace("  ", " ").strip()


def gen_sipoc(name, category):
    src = {
        "communication": "Template Library / SMTP Gateway",
        "sap_posting": "SAP FI-AR / BAPI Connector",
        "escalation": "Pattern Engine / Approval Workflow",
        "credit": "SAP KNKK / Bureau API",
        "collections": "Collections tracker / SAP FSCM",
        "deductions": "Deduction register / SAP FI-AR",
        "cash_application": "SAP BSID / Matching Engine",
        "logistics": "SAP LIKP-LIPS / Carrier API",
        "notification": "Notification Engine",
        "general": "SAP / system of record",
    }.get(category, "SAP / system of record")
    return {
        "S": src,
        "I": "Transaction context, customer and document keys",
        "P": name,
        "O": "Operation result + audit entry",
        "C": "Downstream activity",
    }


def activity(seq, name, role, fitment, category="general", sipoc=None):
    return {
        "seq": seq, "name": name, "role": role, "duration": DUR[fitment],
        "sipoc": sipoc or gen_sipoc(name, category),
        "fitment": fitment, "fitmentLabel": FIT_LABEL[fitment], "fitmentReason": FIT_REASON[fitment],
    }


# --------------------------------------------------------------------------- #
# 20 hand-crafted decompositions (rich SIPOC + optimization opportunities)     #
# --------------------------------------------------------------------------- #
DECOMPOSITIONS = {

    "Generate_Contextual_Email": {
        "category": "communication",
        "activities": [
            {"seq": 1, "name": "Retrieve customer communication preferences", "role": "System", "duration": "< 1s",
             "sipoc": {"S": "SAP KNA1 / CRM Contact Master", "I": "Customer ID (KUNNR), contact records", "P": "Query preferred channel and language", "O": "Communication profile", "C": "Template Engine"},
             "fitment": "agentic", "fitmentLabel": "Agentic AI", "fitmentReason": "Structured data retrieval from system of record"},
            {"seq": 2, "name": "Pull invoice context and dunning history", "role": "System", "duration": "< 1s",
             "sipoc": {"S": "SAP BSID / BSAD, F150 dunning run", "I": "Document number (BELNR), company code", "P": "Fetch open items, prior dunning level, last contact date", "O": "Invoice context bundle", "C": "Template Engine"},
             "fitment": "agentic", "fitmentLabel": "Agentic AI", "fitmentReason": "Read-only ERP query with deterministic output"},
            {"seq": 3, "name": "Select template and generate personalised content", "role": "AI Agent", "duration": "2-3s",
             "sipoc": {"S": "Template Library / NLG Engine", "I": "Communication profile, invoice context, pattern diagnosis", "P": "Select template by dunning level; personalise with customer-specific tone and evidence", "O": "Populated email draft (subject + body)", "C": "Compliance Check"},
             "fitment": "agentic", "fitmentLabel": "Agentic AI", "fitmentReason": "NLG within template guardrails — structured inputs, constrained output"},
            {"seq": 4, "name": "Validate regulatory and contractual compliance", "role": "Compliance Engine", "duration": "< 1s",
             "sipoc": {"S": "Regulatory rules engine, contract terms DB", "I": "Draft email, customer jurisdiction, contract SLA", "P": "Check against dunning frequency limits, right-to-cure windows, contractual escalation clauses", "O": "Compliance verdict (pass / flag)", "C": "Dispatch Queue"},
             "fitment": "rpa", "fitmentLabel": "RPA / Rule-based", "fitmentReason": "Rule-based validation against codified regulatory and contractual constraints"},
            {"seq": 5, "name": "Attach supporting documents and dispatch", "role": "System", "duration": "1-2s",
             "sipoc": {"S": "DMS / Archive, SMTP Gateway", "I": "Approved email, invoice PDF, statement of account", "P": "Assemble attachment package; dispatch via preferred channel", "O": "Sent confirmation with message ID", "C": "Audit Log"},
             "fitment": "agentic", "fitmentLabel": "Agentic AI", "fitmentReason": "Deterministic assembly and dispatch — no decision required"},
        ],
        "optimized": {
            "eliminatedSteps": ["Validate regulatory and contractual compliance"],
            "opportunities": [
                {"type": "parallelization", "label": "Parallel context retrieval", "description": "Customer preferences and invoice context can be fetched concurrently", "impact": "medium", "lever": "Parallelization of processes"},
                {"type": "elimination", "label": "Inline compliance into template selection", "description": "Embed compliance rules directly into the template engine so compliant-by-design output removes a separate validation step", "impact": "high", "lever": "Early mistake proofing"},
            ]
        }
    },

    "Update_SAP_Dispute(Reject)": {
        "category": "sap_posting",
        "activities": [
            {"seq": 1, "name": "Validate dispute case status in UDM", "role": "System", "duration": "< 1s",
             "sipoc": {"S": "SAP UDM_DISPUTE", "I": "Dispute case GUID", "P": "Confirm case is open and rejection is permissible per case type", "O": "Case validation result", "C": "Rejection Payload Builder"},
             "fitment": "agentic", "fitmentLabel": "Agentic AI", "fitmentReason": "Status check against system of record — deterministic"},
            {"seq": 2, "name": "Assemble rejection payload with evidence", "role": "AI Agent", "duration": "1-2s",
             "sipoc": {"S": "Pattern Engine diagnosis, evidence chain", "I": "Pattern match result, feature scores, supporting documents", "P": "Map diagnosis to SAP reason code; compile evidence summary for audit trail", "O": "Rejection payload (reason code + narrative + attachments)", "C": "BAPI Connector"},
             "fitment": "workflow", "fitmentLabel": "Workflow", "fitmentReason": "Requires judgement in mapping diagnosis to reason code — assisted decision"},
            {"seq": 3, "name": "Post status change via BAPI_UDM_DISPUTE_CHANGE", "role": "SAP Connector", "duration": "1-3s",
             "sipoc": {"S": "SAP FSCM-DM", "I": "Rejection payload, case GUID", "P": "Call BAPI to update dispute status to Rejected; write change document", "O": "SAP return code + change doc number", "C": "Audit Log + Notification"},
             "fitment": "agentic", "fitmentLabel": "Agentic AI", "fitmentReason": "Deterministic BAPI call with structured payload — Saga-compensable"},
            {"seq": 4, "name": "Log audit trail and notify dispute originator", "role": "System", "duration": "< 1s",
             "sipoc": {"S": "Notification Engine", "I": "Rejection confirmation, originator contact", "P": "Write cryptographic audit entry; send notification with reason and evidence link", "O": "Audit record + notification confirmation", "C": "Customer / Internal Originator"},
             "fitment": "agentic", "fitmentLabel": "Agentic AI", "fitmentReason": "Template-driven notification — no judgment required"},
        ],
        "optimized": {
            "eliminatedSteps": [],
            "opportunities": [
                {"type": "parallelization", "label": "Parallel audit + notification", "description": "Audit log write and originator notification have no dependency — execute concurrently", "impact": "medium", "lever": "Parallelization of processes"},
            ]
        }
    },

    "Toggle_Dunning_Block(Remove)": {
        "category": "sap_posting",
        "activities": [
            {"seq": 1, "name": "Check current dunning block status on customer", "role": "System", "duration": "< 1s",
             "sipoc": {"S": "SAP KNB1", "I": "Customer number, company code", "P": "Read dunning block indicator (MANSP field)", "O": "Current block status", "C": "Block Toggle Logic"},
             "fitment": "agentic", "fitmentLabel": "Agentic AI", "fitmentReason": "Single-field read from customer master"},
            {"seq": 2, "name": "Remove dunning block via master data update", "role": "SAP Connector", "duration": "1-2s",
             "sipoc": {"S": "SAP KNB1 via BAPI_CUSTOMER_CHANGE", "I": "Customer number, MANSP = blank", "P": "Clear the dunning block indicator; write change document to CDHDR/CDPOS", "O": "Updated customer master + change doc", "C": "Dunning Run Engine"},
             "fitment": "agentic", "fitmentLabel": "Agentic AI", "fitmentReason": "Deterministic field update — Saga-compensable (can re-set block if needed)"},
            {"seq": 3, "name": "Trigger next dunning run inclusion check", "role": "System", "duration": "< 1s",
             "sipoc": {"S": "F150 dunning programme", "I": "Customer number, open items", "P": "Flag customer for inclusion in next scheduled dunning run", "O": "Dunning queue update", "C": "Collections Worklist"},
             "fitment": "agentic", "fitmentLabel": "Agentic AI", "fitmentReason": "Automated queue management — no human decision"},
        ],
        "optimized": {
            "eliminatedSteps": [],
            "opportunities": [
                {"type": "batch", "label": "Batch block removals", "description": "When multiple blocks are removed in the same cycle, batch into a single BAPI call", "impact": "medium", "lever": "Batch size optimization"},
            ]
        }
    },

    "Apply_Legal_Hold": {
        "category": "escalation",
        "activities": [
            {"seq": 1, "name": "Compile exposure summary and dispute history", "role": "System", "duration": "1-2s",
             "sipoc": {"S": "SAP BSID, UDM_DISPUTE, KNKK", "I": "Customer number, all open items and disputes", "P": "Aggregate total exposure, dispute count, pattern history, credit utilisation", "O": "Exposure summary report", "C": "Legal Hold Recommender"},
             "fitment": "agentic", "fitmentLabel": "Agentic AI", "fitmentReason": "Data aggregation from multiple SAP tables — deterministic"},
            {"seq": 2, "name": "Generate legal hold recommendation", "role": "AI Agent", "duration": "2-3s",
             "sipoc": {"S": "Pattern Engine, exposure summary", "I": "Diagnosis, confidence score, historical pattern frequency", "P": "Draft recommendation memo with evidence chain, risk assessment, and suggested hold scope", "O": "Legal hold recommendation document", "C": "VP Approval Queue"},
             "fitment": "workflow", "fitmentLabel": "Workflow", "fitmentReason": "AI-assisted drafting but requires structured evidence — not pure automation"},
            {"seq": 3, "name": "Route for VP / Legal approval", "role": "Approval Engine", "duration": "Variable",
             "sipoc": {"S": "Approval workflow", "I": "Recommendation document, approver matrix", "P": "Route to Collections VP or Legal Counsel based on exposure threshold; await explicit approval", "O": "Approval / rejection decision with comments", "C": "SAP Posting"},
             "fitment": "manual", "fitmentLabel": "Manual", "fitmentReason": "Human judgment required — legal and financial authority decision"},
            {"seq": 4, "name": "Post hold flag and block new orders", "role": "SAP Connector", "duration": "1-2s",
             "sipoc": {"S": "SAP KNB1 (MANSP), KNVV (order block)", "I": "Approved hold decision, customer number", "P": "Set dunning block (MANSP), set order block (AUFSD), write change documents", "O": "Customer master updated + change docs", "C": "Order Management / Sales"},
             "fitment": "agentic", "fitmentLabel": "Agentic AI", "fitmentReason": "Deterministic SAP updates — Saga-compensable on reversal"},
            {"seq": 5, "name": "Notify customer and internal stakeholders", "role": "System", "duration": "1-2s",
             "sipoc": {"S": "Notification Engine", "I": "Hold confirmation, stakeholder list, customer contacts", "P": "Send formal legal hold notice to customer; alert Sales, Credit, and Account Management", "O": "Notification confirmations", "C": "Customer / Sales / Credit teams"},
             "fitment": "workflow", "fitmentLabel": "Workflow", "fitmentReason": "Customer-facing communication requires tone calibration — assisted"},
        ],
        "optimized": {
            "eliminatedSteps": [],
            "opportunities": [
                {"type": "parallelization", "label": "Parallel exposure + recommendation", "description": "Exposure compilation and initial recommendation draft can overlap — recommendation refines as data arrives", "impact": "medium", "lever": "Parallelization of processes"},
            ]
        }
    },

    "Trigger_Credit_Review": {
        "category": "credit",
        "activities": [
            {"seq": 1, "name": "Pull current credit exposure from KNKK", "role": "System", "duration": "< 1s",
             "sipoc": {"S": "SAP KNKK (credit master)", "I": "Customer number, credit control area", "P": "Read credit limit, current exposure, last review date, payment index", "O": "Credit snapshot", "C": "Bureau Integration"},
             "fitment": "agentic", "fitmentLabel": "Agentic AI", "fitmentReason": "Structured read from SAP credit master segment"},
            {"seq": 2, "name": "Fetch external bureau data", "role": "Integration Layer", "duration": "3-5s",
             "sipoc": {"S": "D&B / Moody's / Bureau API", "I": "Customer DUNS number or tax ID", "P": "Pull latest credit score, payment behaviour index, bankruptcy flags, industry risk", "O": "External risk profile", "C": "Scoring Model"},
             "fitment": "agentic", "fitmentLabel": "Agentic AI", "fitmentReason": "API call to external service — deterministic integration"},
            {"seq": 3, "name": "Calculate revised credit risk score", "role": "Risk Model", "duration": "1-2s",
             "sipoc": {"S": "Credit scoring model", "I": "SAP credit snapshot + external risk profile + pattern diagnosis", "P": "Weighted scoring: 40% bureau, 30% payment history, 20% pattern signals, 10% industry", "O": "Revised credit score + recommended limit", "C": "Credit Analyst"},
             "fitment": "agentic", "fitmentLabel": "Agentic AI", "fitmentReason": "Model-driven scoring with transparent weights — fully automatable"},
            {"seq": 4, "name": "Route review to Credit Analyst for decision", "role": "Approval Engine", "duration": "Variable",
             "sipoc": {"S": "Credit workflow", "I": "Revised score, recommended limit, full evidence package", "P": "Present scored recommendation; analyst approves, adjusts, or overrides the suggested limit", "O": "Approved credit decision + new limit", "C": "SAP Credit Master Update"},
             "fitment": "manual", "fitmentLabel": "Manual", "fitmentReason": "Credit limit decisions carry financial authority — human approval required"},
        ],
        "optimized": {
            "eliminatedSteps": [],
            "opportunities": [
                {"type": "parallelization", "label": "Parallel SAP + bureau fetch", "description": "Internal SAP credit data and external bureau data have no dependency — fetch simultaneously", "impact": "high", "lever": "Parallelization of processes"},
            ]
        }
    },

    "Escalate_Collections_Manager": {
        "category": "escalation",
        "activities": [
            {"seq": 1, "name": "Compile escalation package", "role": "AI Agent", "duration": "2-3s",
             "sipoc": {"S": "Pattern Engine, invoice data", "I": "Pattern diagnosis, confidence, action history, customer context", "P": "Generate escalation summary: pattern name, evidence, prior actions taken, recommended next steps", "O": "Escalation package (structured document)", "C": "Routing Engine"},
             "fitment": "agentic", "fitmentLabel": "Agentic AI", "fitmentReason": "Structured document generation from deterministic inputs"},
            {"seq": 2, "name": "Determine escalation routing", "role": "Routing Engine", "duration": "< 1s",
             "sipoc": {"S": "Org hierarchy, workload balancer", "I": "Customer segment, exposure amount, manager availability", "P": "Match to responsible Collections Manager based on customer segment and current workload", "O": "Assigned manager + priority level", "C": "Collections Manager"},
             "fitment": "rpa", "fitmentLabel": "RPA / Rule-based", "fitmentReason": "Rule-based routing by customer segment and manager assignment matrix"},
            {"seq": 3, "name": "Create work item and notify manager", "role": "System", "duration": "< 1s",
             "sipoc": {"S": "Task management / notification engine", "I": "Escalation package, assigned manager", "P": "Create prioritised work item; send notification with direct link to evidence", "O": "Work item ID + notification confirmation", "C": "Collections Manager"},
             "fitment": "agentic", "fitmentLabel": "Agentic AI", "fitmentReason": "Template-driven task creation and notification"},
        ],
        "optimized": {
            "eliminatedSteps": [],
            "opportunities": [
                {"type": "enrichment", "label": "Pre-populate resolution options", "description": "Include AI-suggested resolution strategies in the escalation package so the manager can act immediately", "impact": "high", "lever": "Reduction of process steps"},
            ]
        }
    },

    "Send_SMTP_Email": {
        "category": "communication",
        "activities": [
            {"seq": 1, "name": "Resolve recipient and sender addresses", "role": "System", "duration": "< 1s",
             "sipoc": {"S": "Customer master, org config", "I": "Customer ID, communication type", "P": "Look up recipient email from KNA1/CRM; select sender address by company code and communication type", "O": "Resolved addresses", "C": "SMTP Gateway"},
             "fitment": "agentic", "fitmentLabel": "Agentic AI", "fitmentReason": "Address resolution from master data — deterministic"},
            {"seq": 2, "name": "Dispatch via SMTP gateway", "role": "System", "duration": "1-3s",
             "sipoc": {"S": "SMTP Gateway / SES", "I": "Email payload, resolved addresses", "P": "Submit to outbound mail queue; handle retry on transient failure", "O": "Delivery receipt / message ID", "C": "Audit Log"},
             "fitment": "agentic", "fitmentLabel": "Agentic AI", "fitmentReason": "Infrastructure operation — fully automated with retry logic"},
            {"seq": 3, "name": "Log delivery status to audit trail", "role": "System", "duration": "< 1s",
             "sipoc": {"S": "Audit service", "I": "Message ID, delivery receipt, timestamp", "P": "Write immutable audit record with delivery status and hash", "O": "Audit log entry", "C": "Compliance / Reporting"},
             "fitment": "agentic", "fitmentLabel": "Agentic AI", "fitmentReason": "Automated logging with no decision required"},
        ],
        "optimized": {
            "eliminatedSteps": [],
            "opportunities": [
                {"type": "batch", "label": "Batch dispatch for same customer", "description": "If multiple emails queued for the same customer, consolidate into a single communication", "impact": "medium", "lever": "Batch size optimization"},
            ]
        }
    },

    "Soft_Email": {
        "category": "communication",
        "activities": [
            {"seq": 1, "name": "Select soft-touch template based on relationship tier", "role": "AI Agent", "duration": "1s",
             "sipoc": {"S": "Template Library, Customer segmentation", "I": "Customer segment (strategic/standard), relationship tenure", "P": "Choose diplomatic tone template appropriate for the customer's value and history", "O": "Selected template", "C": "Content Generator"},
             "fitment": "agentic", "fitmentLabel": "Agentic AI", "fitmentReason": "Rule-based template selection by customer segment"},
            {"seq": 2, "name": "Generate and dispatch soft reminder", "role": "System", "duration": "2-3s",
             "sipoc": {"S": "NLG Engine, SMTP", "I": "Template, invoice details, customer name", "P": "Personalise template; dispatch via preferred channel", "O": "Sent confirmation", "C": "Customer"},
             "fitment": "agentic", "fitmentLabel": "Agentic AI", "fitmentReason": "Templated communication — fully automated"},
        ],
        "optimized": {"eliminatedSteps": [], "opportunities": []}
    },

    "Alert_AE_Only": {
        "category": "notification",
        "activities": [
            {"seq": 1, "name": "Identify assigned Account Executive", "role": "System", "duration": "< 1s",
             "sipoc": {"S": "CRM / SAP partner function (KNVP)", "I": "Customer number, sales org", "P": "Look up AE from partner function table", "O": "AE contact details", "C": "Notification Engine"},
             "fitment": "agentic", "fitmentLabel": "Agentic AI", "fitmentReason": "Partner function lookup — deterministic"},
            {"seq": 2, "name": "Send contextual alert to AE", "role": "System", "duration": "< 1s",
             "sipoc": {"S": "Notification Engine", "I": "Pattern diagnosis summary, AE contact", "P": "Send Slack/Teams/email alert with pattern context and suggested talking points", "O": "Alert confirmation", "C": "Account Executive"},
             "fitment": "agentic", "fitmentLabel": "Agentic AI", "fitmentReason": "Template-driven alert with structured content"},
        ],
        "optimized": {"eliminatedSteps": [], "opportunities": []}
    },

    "Reject_Dispute(Auto)": {
        "category": "sap_posting",
        "activities": [
            {"seq": 1, "name": "Auto-validate rejection eligibility", "role": "System", "duration": "< 1s",
             "sipoc": {"S": "Dispute rules engine", "I": "Case type, dispute age, evidence score", "P": "Check auto-rejection criteria: evidence score > threshold, no contractual override, within SLA", "O": "Eligibility verdict", "C": "BAPI Connector"},
             "fitment": "rpa", "fitmentLabel": "RPA / Rule-based", "fitmentReason": "Codified business rules — no judgment required"},
            {"seq": 2, "name": "Post rejection to SAP UDM", "role": "SAP Connector", "duration": "1-2s",
             "sipoc": {"S": "SAP FSCM-DM", "I": "Case GUID, auto-rejection reason code", "P": "Call BAPI_UDM_DISPUTE_CHANGE to set status = Rejected; write change doc", "O": "SAP return code", "C": "Notification Engine"},
             "fitment": "agentic", "fitmentLabel": "Agentic AI", "fitmentReason": "Deterministic BAPI call — Saga-compensable"},
            {"seq": 3, "name": "Notify and log", "role": "System", "duration": "< 1s",
             "sipoc": {"S": "Notification + Audit", "I": "Rejection result", "P": "Notify customer/originator; write audit trail", "O": "Confirmation", "C": "Audit Log"},
             "fitment": "agentic", "fitmentLabel": "Agentic AI", "fitmentReason": "Automated post-processing"},
        ],
        "optimized": {"eliminatedSteps": [], "opportunities": []}
    },

    "Remove_Dunning_Block": {
        "category": "sap_posting",
        "activities": [
            {"seq": 1, "name": "Clear MANSP field on customer master", "role": "SAP Connector", "duration": "1-2s",
             "sipoc": {"S": "SAP KNB1", "I": "Customer number, company code", "P": "Update MANSP to blank via BAPI; write change document", "O": "Updated customer master", "C": "Dunning Programme"},
             "fitment": "agentic", "fitmentLabel": "Agentic AI", "fitmentReason": "Single-field master data update — Saga-compensable"},
        ],
        "optimized": {"eliminatedSteps": [], "opportunities": []}
    },

    "Notify_CFO_Office": {
        "category": "escalation",
        "activities": [
            {"seq": 1, "name": "Compile executive risk brief", "role": "AI Agent", "duration": "3-5s",
             "sipoc": {"S": "Pattern Engine, credit data, exposure data", "I": "Pattern diagnosis, total exposure, customer history, prior escalations", "P": "Generate one-page executive summary: risk, exposure, recommended action, timeline", "O": "Executive risk brief (PDF)", "C": "CFO Office"},
             "fitment": "workflow", "fitmentLabel": "Workflow", "fitmentReason": "Executive communication requires nuanced summarisation — AI-assisted with human review expected"},
            {"seq": 2, "name": "Route to CFO office via priority channel", "role": "System", "duration": "< 1s",
             "sipoc": {"S": "Executive notification channel", "I": "Risk brief, priority flag", "P": "Send via designated CFO alert channel (email + dashboard flag)", "O": "Delivery confirmation", "C": "CFO / VP Finance"},
             "fitment": "agentic", "fitmentLabel": "Agentic AI", "fitmentReason": "Templated routing to known recipient — automated"},
        ],
        "optimized": {"eliminatedSteps": [], "opportunities": []}
    },

    "Block_New_Orders": {
        "category": "sap_posting",
        "activities": [
            {"seq": 1, "name": "Set order block on customer master", "role": "SAP Connector", "duration": "1-2s",
             "sipoc": {"S": "SAP KNVV (sales area data)", "I": "Customer number, sales org, distribution channel", "P": "Set AUFSD (order block) field via BAPI; write change document", "O": "Customer master updated", "C": "Sales / Order Management"},
             "fitment": "agentic", "fitmentLabel": "Agentic AI", "fitmentReason": "Deterministic field update — Saga-compensable (reversible on resolution)"},
            {"seq": 2, "name": "Notify Sales and Account Management", "role": "System", "duration": "< 1s",
             "sipoc": {"S": "Notification Engine", "I": "Block confirmation, AE/sales contacts", "P": "Alert sales team of order block with reason and estimated duration", "O": "Notification delivery", "C": "Sales Team"},
             "fitment": "agentic", "fitmentLabel": "Agentic AI", "fitmentReason": "Automated notification to known stakeholders"},
        ],
        "optimized": {"eliminatedSteps": [], "opportunities": []}
    },

    "Freeze_Credit_Line": {
        "category": "credit",
        "activities": [
            {"seq": 1, "name": "Set credit limit to zero in KNKK", "role": "SAP Connector", "duration": "1-2s",
             "sipoc": {"S": "SAP KNKK", "I": "Customer number, credit control area", "P": "Update credit limit to 0 via UKM API or BAPI; set credit block flag", "O": "Updated credit master", "C": "Credit Management"},
             "fitment": "agentic", "fitmentLabel": "Agentic AI", "fitmentReason": "Deterministic credit master update — reversible"},
            {"seq": 2, "name": "Log freeze event and notify Credit team", "role": "System", "duration": "< 1s",
             "sipoc": {"S": "Audit + notification", "I": "Freeze confirmation", "P": "Write audit log; notify Credit Analyst and Credit Manager", "O": "Confirmation", "C": "Credit Team"},
             "fitment": "agentic", "fitmentLabel": "Agentic AI", "fitmentReason": "Automated post-processing"},
        ],
        "optimized": {"eliminatedSteps": [], "opportunities": []}
    },

    "Propose_Payment_Plan": {
        "category": "collections",
        "activities": [
            {"seq": 1, "name": "Analyse customer payment capacity", "role": "AI Agent", "duration": "2-3s",
             "sipoc": {"S": "SAP BSID, payment history, bureau data", "I": "Open items, historical payment patterns, D&B score", "P": "Model affordable instalment schedule based on cash flow indicators and total outstanding", "O": "Proposed payment plan (schedule + amounts)", "C": "AR Analyst"},
             "fitment": "workflow", "fitmentLabel": "Workflow", "fitmentReason": "AI models the plan but an analyst must review terms before customer offer"},
            {"seq": 2, "name": "Review and adjust plan terms", "role": "AR Analyst", "duration": "Variable",
             "sipoc": {"S": "Proposed plan", "I": "AI-generated schedule, customer relationship context", "P": "Analyst reviews, adjusts instalment amounts or duration, adds special conditions", "O": "Approved payment plan", "C": "Customer Communication"},
             "fitment": "manual", "fitmentLabel": "Manual", "fitmentReason": "Financial terms require human judgment and relationship awareness"},
            {"seq": 3, "name": "Generate and send plan offer to customer", "role": "System", "duration": "2-3s",
             "sipoc": {"S": "Document Engine, SMTP", "I": "Approved plan, customer contacts", "P": "Generate formal payment plan document; dispatch to customer for acceptance", "O": "Sent plan + tracking", "C": "Customer"},
             "fitment": "agentic", "fitmentLabel": "Agentic AI", "fitmentReason": "Document generation and dispatch — automated"},
        ],
        "optimized": {
            "eliminatedSteps": [],
            "opportunities": [
                {"type": "enrichment", "label": "Pre-approved plan templates", "description": "For standard scenarios (< $50K, good payment history), use pre-approved plan templates that skip analyst review", "impact": "high", "lever": "Reduction of process steps"},
            ]
        }
    },

    "Log_Promise_to_Pay": {
        "category": "collections",
        "activities": [
            {"seq": 1, "name": "Record promise details in collections system", "role": "System", "duration": "< 1s",
             "sipoc": {"S": "Collections tracker / SAP FSCM-COL", "I": "Customer number, promised amount, promised date, call notes", "P": "Create P2P record; set follow-up reminder for day after promised date", "O": "P2P record + scheduled follow-up", "C": "Collections Worklist"},
             "fitment": "agentic", "fitmentLabel": "Agentic AI", "fitmentReason": "Structured data entry with automated follow-up scheduling"},
            {"seq": 2, "name": "Set calendar reminder for broken-promise check", "role": "System", "duration": "< 1s",
             "sipoc": {"S": "Scheduling engine", "I": "Promised date + 1 day", "P": "Schedule automated check: was the payment received by the promised date?", "O": "Scheduled check event", "C": "Pattern Engine (broken-p2p detector)"},
             "fitment": "agentic", "fitmentLabel": "Agentic AI", "fitmentReason": "Calendar-based automation — no human input needed"},
        ],
        "optimized": {"eliminatedSteps": [], "opportunities": []}
    },

    "Schedule_Follow_Up": {
        "category": "collections",
        "activities": [
            {"seq": 1, "name": "Calculate optimal follow-up timing", "role": "AI Agent", "duration": "< 1s",
             "sipoc": {"S": "Customer payment patterns, calendar", "I": "Payment history, business days calendar, customer time zone", "P": "Determine optimal follow-up date and time based on historical responsiveness patterns", "O": "Scheduled date/time", "C": "Collections Worklist"},
             "fitment": "agentic", "fitmentLabel": "Agentic AI", "fitmentReason": "Pattern-based scheduling — deterministic model"},
            {"seq": 2, "name": "Create worklist item with context", "role": "System", "duration": "< 1s",
             "sipoc": {"S": "Worklist engine", "I": "Follow-up date, full case context", "P": "Create prioritised work item with pre-loaded customer context and suggested talking points", "O": "Queued work item", "C": "AR Analyst"},
             "fitment": "agentic", "fitmentLabel": "Agentic AI", "fitmentReason": "Automated worklist management"},
        ],
        "optimized": {"eliminatedSteps": [], "opportunities": []}
    },

    "Merge_Deductions": {
        "category": "deductions",
        "activities": [
            {"seq": 1, "name": "Identify related deductions for the same customer", "role": "AI Agent", "duration": "2-3s",
             "sipoc": {"S": "Deduction register, pattern analysis", "I": "Customer number, open deductions, pattern diagnosis", "P": "Cluster deductions by root cause, timing, and amount pattern; propose merge groups", "O": "Merge candidates (grouped deductions)", "C": "AR Analyst"},
             "fitment": "workflow", "fitmentLabel": "Workflow", "fitmentReason": "AI clusters but analyst must confirm the grouping logic"},
            {"seq": 2, "name": "Consolidate into single case and net amounts", "role": "System", "duration": "1-2s",
             "sipoc": {"S": "SAP FI-AR", "I": "Approved merge group", "P": "Create consolidated deduction case; net the amounts; link original items", "O": "Consolidated case + netted balance", "C": "Resolution Queue"},
             "fitment": "agentic", "fitmentLabel": "Agentic AI", "fitmentReason": "Deterministic netting and case creation once merge is approved"},
        ],
        "optimized": {"eliminatedSteps": [], "opportunities": []}
    },

    "Offset_Against_Invoice": {
        "category": "cash_application",
        "activities": [
            {"seq": 1, "name": "Match deduction to eligible invoices", "role": "AI Agent", "duration": "1-2s",
             "sipoc": {"S": "SAP BSID, matching rules", "I": "Deduction amount, customer open items", "P": "Find best-fit invoice(s) for offset — exact match first, then partial match with tolerance", "O": "Matched invoice(s) + offset amount", "C": "Posting Engine"},
             "fitment": "agentic", "fitmentLabel": "Agentic AI", "fitmentReason": "Rule-based matching with ML fallback — can run autonomously"},
            {"seq": 2, "name": "Post clearing document in SAP", "role": "SAP Connector", "duration": "1-2s",
             "sipoc": {"S": "SAP FI-AR (F-32 equivalent)", "I": "Matched items, offset amount", "P": "Create clearing document; update open item status on both deduction and invoice", "O": "Clearing doc number", "C": "Reconciliation"},
             "fitment": "agentic", "fitmentLabel": "Agentic AI", "fitmentReason": "Deterministic SAP posting — Saga-compensable"},
        ],
        "optimized": {"eliminatedSteps": [], "opportunities": []}
    },

    "Request_POD_From_Carrier": {
        "category": "logistics",
        "activities": [
            {"seq": 1, "name": "Identify carrier and shipment from delivery", "role": "System", "duration": "< 1s",
             "sipoc": {"S": "SAP LIKP/LIPS, carrier master", "I": "Delivery number, bill of lading", "P": "Look up carrier details and tracking information from logistics documents", "O": "Carrier ID + shipment reference", "C": "Carrier API"},
             "fitment": "agentic", "fitmentLabel": "Agentic AI", "fitmentReason": "Structured data lookup from logistics tables"},
            {"seq": 2, "name": "Submit POD request via carrier API or email", "role": "Integration Layer", "duration": "2-5s",
             "sipoc": {"S": "Carrier API / EDI / Email gateway", "I": "Shipment reference, delivery number", "P": "Call carrier API for digital POD; fall back to email request if no API available", "O": "POD document or request tracking number", "C": "Dispute Resolution"},
             "fitment": "agentic", "fitmentLabel": "Agentic AI", "fitmentReason": "API integration with email fallback — fully automated"},
            {"seq": 3, "name": "Attach POD to dispute case as evidence", "role": "System", "duration": "< 1s",
             "sipoc": {"S": "DMS / UDM_DISPUTE", "I": "POD document, dispute case GUID", "P": "Attach POD to dispute case record; update case with evidence received flag", "O": "Updated case with POD attached", "C": "Dispute Analyst"},
             "fitment": "agentic", "fitmentLabel": "Agentic AI", "fitmentReason": "Document attachment — deterministic"},
        ],
        "optimized": {"eliminatedSteps": [], "opportunities": []}
    },
}


def template_decomposition(block_key):
    """Generic 3-activity decomposition derived from the block's verb + noun."""
    label = prettify(block_key)
    verb = block_key.split("_")[0] if "_" in block_key else block_key
    v = verb.lower()
    if any(x in v for x in ["send", "notify", "alert", "email", "comm"]):
        category = "communication"
        acts = [
            activity(1, "Resolve recipient and assemble payload", "System", "agentic", category),
            activity(2, "Dispatch " + label.lower(), "System", "agentic", category),
            activity(3, "Log delivery to audit trail", "System", "agentic", category),
        ]
    elif any(x in v for x in ["update", "post", "clear", "set", "toggle", "block", "freeze", "remove", "reject", "lower", "merge", "offset", "apply", "add", "disable", "adjust", "auto"]):
        category = "sap_posting"
        acts = [
            activity(1, "Validate preconditions in SAP", "System", "agentic", category),
            activity(2, "Execute " + label.lower() + " via BAPI", "SAP Connector", "agentic", category),
            activity(3, "Write audit record and notify stakeholders", "System", "agentic", category),
        ]
    elif any(x in v for x in ["escalate", "route", "propose", "request", "trigger", "demand", "certified", "bundle"]):
        category = "escalation"
        acts = [
            activity(1, "Compile context and evidence package", "AI Agent", "workflow", category),
            activity(2, "Route to appropriate approver", "Routing Engine", "rpa", category),
            activity(3, "Create work item and notify", "System", "agentic", category),
        ]
    elif any(x in v for x in ["log", "schedule", "track", "record", "flag"]):
        category = "collections"
        acts = [
            activity(1, "Record " + label.lower() + " in system", "System", "agentic", category),
            activity(2, "Set follow-up reminder", "System", "agentic", category),
        ]
    else:
        category = "general"
        acts = [
            activity(1, "Retrieve required data", "System", "agentic", category),
            activity(2, "Execute " + label.lower(), "AI Agent", "workflow", category),
            activity(3, "Log result and notify", "System", "agentic", category),
        ]
    return {"category": category, "activities": acts, "optimized": {"eliminatedSteps": [], "opportunities": []}}


def finalize(key, d):
    """Fill derived fields: key, label, asIsStepCount, optimized.stepCount/automationRate."""
    acts = d["activities"]
    elim = d["optimized"].get("eliminatedSteps", [])
    remaining = [a for a in acts if a["name"] not in elim]
    auto_all = sum(1 for a in acts if a["fitment"] in ("agentic", "rpa"))
    auto_rem = sum(1 for a in remaining if a["fitment"] in ("agentic", "rpa"))
    d["key"] = key
    d["label"] = prettify(key)
    d["asIsStepCount"] = len(acts)
    d["asIsAutomationRate"] = round(100 * auto_all / len(acts)) if acts else 0
    d["optimized"]["stepCount"] = len(remaining)
    d["optimized"]["automationRate"] = round(100 * auto_rem / len(remaining)) if remaining else 0
    return d


def extract_blocks(patterns):
    blocks = set()
    def add(tok):
        for raw in (tok or "").split(" + "):
            k = raw.strip()
            if k:
                blocks.add(k)
    for p in patterns:
        for s in p.get("originalDAG", []):
            add(s)
        for br in p.get("branchingDAG", []):
            for a in br.get("actions", []):
                add(a)
    return sorted(blocks)


def main():
    patterns = json.load(open(PATTERNS, encoding="utf-8"))["patterns"]
    real_blocks = extract_blocks(patterns)

    decompositions = {}
    handcrafted = template = 0
    for key in real_blocks:
        if key in DECOMPOSITIONS:
            decompositions[key] = finalize(key, copy.deepcopy(DECOMPOSITIONS[key]))
            handcrafted += 1
        else:
            decompositions[key] = finalize(key, template_decomposition(key))
            template += 1
    # include any hand-crafted example blocks not present in the current library
    for key, d in DECOMPOSITIONS.items():
        if key not in decompositions:
            decompositions[key] = finalize(key, copy.deepcopy(d))

    out = {
        "meta": {
            "title": "ProcessIQ — Action Block Decompositions",
            "note": "BPT-derived activity blueprints. Each action block is decomposed into concrete activities with SIPOC and technology fitment.",
            "blockCount": len(real_blocks),
            "decomposedCount": len(real_blocks),
            "handcraftedCount": handcrafted,
            "templateCount": template,
        },
        "decompositions": decompositions,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

    print(f"Wrote build.json -> {os.path.relpath(OUT, ROOT)}")
    print(f"{len(real_blocks)} total blocks, {handcrafted} hand-crafted, {template} template-generated")


if __name__ == "__main__":
    main()
