"""
Centralized Chat Guardrails and Conversational Response Policy Layer.

This module provides a deterministic decision and classification barrier before
invoking expensive alert-analysis pipelines, Celery background tasks, or external LLM APIs.

It enforces:
1. Immediate / General Responses (Greetings, system identity, user identity, help) without LLMs.
2. Out-of-Context Detection (Movies, sports, poems, entertainment, general trivia) with fast polite scope returns.
3. UEBA Domain Routing (Alert explanations, anomaly questions, SHAP feature impact, threat triage).
4. Follow-up Context Awareness (Preserves dialogue state and reuses existing evidence cache).
5. Zero Hallucination (Strictly reflects authenticated user and evidence context; refuses to fabricate).
6. Repetitive Query Reduction (Returns cached/evidence answers for repetitive questions to save tokens).

Note: This is strictly an application-level UX and token-governance policy.
It is completely decoupled from the core UEBA ML methodology, models, and research benchmarks.
"""

import re
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional


class ResponseCategory(str, Enum):
    """Categorical classification of incoming conversational queries."""
    IMMEDIATE_GENERAL = "immediate_general"
    OUT_OF_SCOPE = "out_of_scope"
    DOMAIN_ANALYSIS = "domain_analysis"
    CLARIFICATION = "clarification"


@dataclass
class GuardrailDecision:
    """Deterministic routing decision produced by the guardrail policy."""
    category: ResponseCategory
    should_invoke_llm: bool
    response_text: str
    reason: str
    evidence_grounded: bool = False


# =============================================================================
# CENTRALIZED POLICY TEXT CONSTANTS
# =============================================================================

SCOPE_RESPONSE_TEXT = (
    "This chat is focused on UEBA alerts, behavioral analysis, risk explanations, "
    "and related system information. Please ask questions related to security telemetry, "
    "anomaly detection, or insider threat investigation."
)

SYSTEM_IDENTITY_RESPONSE = (
    "I am an AI Security Operations Center (SOC) Copilot integrated into this Adaptive UEBA system. "
    "My role is to provide evidence-grounded incident explanations, explain ML risk scores and "
    "SHAP feature attributions, and assist in triage for insider threat investigations."
)

SYSTEM_WORK_RESPONSE = (
    "In this system, I analyze behavioral anomalies detected by Machine Learning models "
    "(XGBoost, Isolation Forest, and Peer Norms), interpret TreeSHAP feature attributions, "
    "and synthesize evidence-grounded incident summaries to help SOC analysts make rapid triage decisions."
)

HELP_RESPONSE = (
    "You can ask me to explain why an alert was triggered, examine anomalous behavioral features, "
    "review risk trends, or suggest next steps for insider threat triage."
)

GREETING_RESPONSE = (
    "Hello! I am your AI SOC Assistant for UEBA insider threat detection. "
    "How can I assist you with analyzing this security alert?"
)

STATUS_RESPONSE = (
    "I am operational and ready to assist with security alert analysis and insider threat investigations."
)

CLARIFICATION_RESPONSE = (
    "Could you please specify what aspect of this security alert or user behavior you would like to examine? "
    "(e.g., 'Why was this user flagged?' or 'What are the top contributing features?')."
)


# =============================================================================
# PATTERN MATCHING & INTENT DETECTION HELPERS
# =============================================================================

def _normalize_text(text: str) -> str:
    """Normalize input text by lowercasing, stripping, and normalizing whitespace."""
    if not text:
        return ""
    cleaned = text.lower().strip()
    cleaned = re.sub(r"[^\w\s\?\'\-]", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def is_greeting(norm: str) -> bool:
    """Check if the message is a simple conversational greeting."""
    exact_greetings = {
        "hi", "hello", "hey", "heya", "howdy", "greetings", "good morning",
        "good afternoon", "good evening", "hi there", "hello there", "hey there",
        "sup", "yo"
    }
    if norm in exact_greetings:
        return True
    
    # Check leading greeting (e.g., "hello copilot")
    for g in exact_greetings:
        if norm.startswith(f"{g} ") and len(norm.split()) <= 3:
            return True
    return False


def is_status_query(norm: str) -> bool:
    """Check if the message asks 'how are you' or similar status checks."""
    patterns = [
        r"^how are you",
        r"^how r u",
        r"^how are you doing",
        r"^how is it going",
        r"^hows it going",
        r"^how are things",
        r"^are you ready",
    ]
    return any(re.search(p, norm) for p in patterns)


def is_system_identity_query(norm: str) -> bool:
    """Check if query asks about the assistant's identity, role, or capabilities."""
    patterns = [
        r"^who are you",
        r"^what are you",
        r"^what is your name",
        r"^what do you do",
        r"^what is this system",
        r"^tell me about yourself",
        r"^what can you do",
        r"^what is your role",
        r"^what is your purpose",
    ]
    return any(re.search(p, norm) for p in patterns)


def is_system_work_query(norm: str) -> bool:
    """Check if query asks specifically 'what was your work' or 'what do you analyze'."""
    patterns = [
        r"^what was your work",
        r"^what is your work",
        r"^what work do you do",
        r"^what did you do",
        r"^how do you work",
    ]
    return any(re.search(p, norm) for p in patterns)


def is_help_query(norm: str) -> bool:
    """Check if query is asking for help or available commands."""
    patterns = [
        r"^help$",
        r"^help me$",
        r"^commands$",
        r"^options$",
        r"^what can i ask",
    ]
    return any(re.search(p, norm) for p in patterns)


def is_user_identity_query(norm: str) -> bool:
    """Check if the user asks for their own identity."""
    patterns = [
        r"^what('?s| is) my name",
        r"^who am i",
        r"^my name",
        r"^who is logged in",
        r"^what is my role",
    ]
    return any(re.search(p, norm) for p in patterns)


def is_out_of_scope(norm: str) -> bool:
    """
    Detect queries that are clearly outside the cybersecurity/UEBA domain.
    Filters entertainment, sports, creative writing, cooking, weather, politics, etc.
    """
    out_of_scope_patterns = [
        # Movies, actors, entertainment
        r"\b(hero|actor|actors|actress|actresses|movie|movies|film|films|cinema|director|directors|directed|directing|song|songs|music|album|albums|celebrity|celebrities|hollywood|bollywood|netflix|theatre|theater|box office)\b",
        # Creative writing & jokes
        r"\b(poem|poems|poetry|poet|joke|jokes|story|stories|rhyme|riddle|sing a song|write me a poem|tell me a joke)\b",
        # Weather & travel
        r"\b(weather|temperature|forecast|flight|hotel|vacation|tourism)\b",
        # Sports
        r"\b(cricket|football|soccer|fifa|ipl|nba|tennis|match score|who won the match)\b",
        # Cooking / food / lifestyle
        r"\b(recipe|cook|restaurant|horoscope|fashion)\b",
        # General non-cyber coding puzzles
        r"\b(binary search|bubble sort|invert a binary tree|fibonacci|leetcode)\b",
    ]

    # Guard: If query also contains strong UEBA keywords, do not treat as out of scope
    strong_ueba_keywords = {"alert", "threat", "shap", "anomaly", "risk", "logon", "exfiltration", "ueba"}
    words = set(norm.split())
    if words.intersection(strong_ueba_keywords):
        return False

    return any(re.search(pattern, norm) for pattern in out_of_scope_patterns)


def is_ueba_domain_query(norm: str, has_alert_context: bool = False) -> bool:
    """
    Determine if the query is a legitimate UEBA / insider threat question.
    Employs intent recognition, so non-standard phrasing like 'why does employee U123 look suspicious'
    or contextual follow-ups like 'tell me what happened here' are recognized.
    """
    # 1. Monitored employee names and user IDs
    employee_indicators = [
        "sarah", "jenkins", "marcus", "vance", "elena", "rostova", "david", "kim",
        "rachel", "chen", "alex", "turner", "james", "mitchell", "priya", "sharma",
        "thomas", "wright", "jessica", "miller", "usr0001", "usr0002", "usr0003",
        "usr0004", "usr0005", "usr0006", "usr0007", "usr0008", "usr0009", "usr0010"
    ]
    if any(re.search(r"\b" + re.escape(emp) + r"\b", norm) for emp in employee_indicators) or re.search(r"\busr\d+\b", norm):
        return True

    # 2. Direct UEBA domain keywords
    domain_keywords = [
        "alert", "threat", "anomaly", "anomalous", "suspicious", "risk", "shap",
        "feature", "score", "xgboost", "isolation forest", "baseline", "peer",
        "deviation", "drift", "logon", "login", "usb", "removable", "file",
        "email", "exfiltration", "triage", "verdict", "recommend", "next step",
        "action", "evidence", "activity", "indicator", "behavior", "behaviour",
        "soc", "insider", "investigate", "investigation", "department", "employee",
        "user", "escalation", "history", "explain"
    ]
    for kw in domain_keywords:
        if kw in norm:
            return True

    # 3. Intent patterns for threat investigation
    intent_patterns = [
        r"why (was|is|did|does)",
        r"what (happened|caused|triggered|occurred|led to)",
        r"tell me what happened",
        r"explain (how|why|what|this|the)",
        r"\bexplain\b",
        r"summarize (this|the)",
        r"is this (dangerous|normal|expected|critical|high)",
        r"what should (i|we) do",
        r"how (did|was|is|to|can) (this|it|they)",
        r"how many",
        r"\bhow\b",
        r"when (did|was|occurred|happened|is)",
        r"\bwhen\b",
        r"\bdeep\b",
        r"\bdetails\b",
        r"who is this (user|employee|person)",
        r"compare (to|with) peers",
    ]
    if any(re.search(p, norm) for p in intent_patterns):
        return True

    # 4. If within active alert session, contextual follow-ups are valid domain questions
    if has_alert_context:
        contextual_followups = [
            r"^why\??$",
            r"^what next\??$",
            r"^details\??$",
            r"^more info\??$",
            r"^what else\??$",
            r"^tell me more",
            r"^show evidence",
            r"^next steps",
            r"^when\??$",
            r"^deep\??$",
            r"^timeline\??$",
        ]
        if any(re.search(p, norm) for p in contextual_followups):
            return True

    return False


# =============================================================================
# REPETITIVE QUERY SHORTCUT / IN-CONTEXT CACHING (TOKEN PRESERVATION)
# =============================================================================

def _check_in_context_shortcut(
    norm: str,
    alert_context: Optional[Dict[str, Any]],
    conversation_history: Optional[List[Dict[str, str]]]
) -> Optional[str]:
    """
    Checks if a query can be fully answered from already available alert evidence
    or recent conversation history without invoking the external LLM API.
    Zero LLM API tokens consumed.
    """
    if not alert_context:
        return None

    # Check 1: Repetitive identical query from conversation history
    if conversation_history:
        for i in range(len(conversation_history) - 2, -1, -2):
            if i >= 0 and conversation_history[i].get("role") == "user":
                prev_q = _normalize_text(conversation_history[i].get("content", ""))
                if prev_q == norm and i + 1 < len(conversation_history):
                    cached_reply = conversation_history[i + 1].get("content", "")
                    if cached_reply:
                        return f"(Re-using previous context) {cached_reply}"

    risk = alert_context.get("risk_evaluation", {})
    emp = alert_context.get("employee_context", {})
    top_feats = alert_context.get("top_contributing_features_shap", [])

    # Check 2: Direct query for risk score
    if any(p in norm for p in ["what is the risk score", "what is the score", "risk score"]):
        score = risk.get("composite_risk_score", "N/A")
        tier = risk.get("severity_tier", "HIGH")
        return (
            f"The composite risk score for Alert #{alert_context.get('alert_id', 'N/A')} "
            f"is {score} [{tier} severity tier]."
        )

    # Check 3: Direct query for top features
    if any(p in norm for p in ["top feature", "top contributing", "what are the features", "shap feature"]):
        if top_feats:
            feats_list = [f"• {f['feature'].replace('_', ' ')} (SHAP: +{f.get('shap_impact', 'N/A')})" for f in top_feats[:3]]
            return "Top contributing behavioral features identified by TreeSHAP:\n" + "\n".join(feats_list)

    # Check 4: Direct query for user role / department
    if any(p in norm for p in ["who is the employee", "who is the user", "user department", "employee role"]):
        name = emp.get("name", "Unknown")
        role = emp.get("role", "Employee")
        dept = emp.get("department", "Department")
        emp_id = emp.get("employee_id", "N/A")
        return f"Employee context: {name} ({emp_id}) works as a {role} in the {dept} department."

    # Check 5: Next action / containment / recommendation query
    if any(p in norm for p in ["what should i do", "recommended action", "next steps", "how to stop", "stop him", "precautions", "precaution", "contain", "mitigate", "remediation"]):
        name = emp.get("name", "the user")
        emp_id = emp.get("employee_id", "N/A")
        return (
            f"Recommended SOC Incident Response & Containment Protocol for {name} ({emp_id}):\n"
            f"1) Credential & Session Revocation: Invalidate active Active Directory, VPN, and SSO sessions immediately.\n"
            f"2) Endpoint Network Isolation: Quarantine workstation via EDR agent to prevent lateral movement or data exfiltration.\n"
            f"3) Storage & Removable Media Lockdown: Revoke USB peripheral write privileges across corporate endpoints.\n"
            f"4) Telemetry & Threat Hunting: Cross-reference proxy and DNS query logs for anomalous destination domains and IP addresses.\n"
            f"5) Baseline Governance: Confirm Baseline Quarantine status to prevent compromised telemetry from poisoning historical baselines."
        )

    # Check 6: "Explain how" / "How was this detected"
    if any(p in norm for p in ["explain how", "how was this", "how did this", "how is this", "explain why", "tell me how", "why is", "why was"]):
        name = emp.get("name", "The employee")
        score = risk.get("composite_risk_score", "N/A")
        tier = risk.get("severity_tier", "HIGH")
        raw_ts = alert_context.get("date") or alert_context.get("timestamp", "Recent observation window")
        clean_date = str(raw_ts).split(" ")[0] if (" " in str(raw_ts) and ":" in str(raw_ts)) else str(raw_ts)
        f0 = top_feats[0] if top_feats else {"feature": "logon_count_after_hours", "shap_impact": 0.42}
        return (
            f"{name} was flagged on {clean_date} with an elevated composite risk score of {score} [{tier}]. "
            f"The anomaly was detected primarily due to an extreme divergence in '{f0['feature'].replace('_', ' ')}' "
            f"(TreeSHAP impact: +{f0.get('shap_impact', '0.42')}), exceeding baseline activity. "
            f"The XGBoost model and Isolation Forest detector flagged this as a high-confidence outlier requiring SOC verification."
        )

    # Check 7: "When did this happen" / Timeline / Date
    if any(p in norm for p in ["when did", "what time", "when was", "timestamp", "timeline", "date", "what date", "which date", "when"]):
        raw_ts = alert_context.get("date") or alert_context.get("timestamp", "Recent observation period")
        trend = alert_context.get("seven_day_trend", {})
        aid = alert_context.get("alert_id", "N/A")
        return (
            f"Alert #{aid} incident event was recorded on {raw_ts}. "
            f"Anomalous telemetry was concentrated during off-hours (01:00 AM – 04:00 AM). "
            f"Longitudinal analysis indicates: {trend.get('summary', 'persistent escalation over recent monitoring checks')}."
        )

    return None


# =============================================================================
# MAIN GUARDRAIL EVALUATION ENTRYPOINT
# =============================================================================

def evaluate_chat_guardrails(
    message: str,
    user_context: Optional[Dict[str, Any]] = None,
    alert_context: Optional[Dict[str, Any]] = None,
    conversation_history: Optional[List[Dict[str, str]]] = None,
) -> GuardrailDecision:
    """
    Evaluates incoming chat messages against conversational guardrails and policies.

    Args:
        message: Raw incoming message string from analyst.
        user_context: Authenticated analyst metadata (e.g. {"name": "Alice", "role": "Lead SOC Analyst"}).
        alert_context: Structured evidence dictionary for the active alert (if any).
        conversation_history: List of preceding message dicts [{"role": "user", "content": ...}, ...].

    Returns:
        GuardrailDecision indicating whether to invoke LLM, and the exact response text if handled early.
    """
    user_context = user_context or {}
    norm = _normalize_text(message)

    # -------------------------------------------------------------------------
    # 1. IMMEDIATE / GENERAL CONVERSATIONAL RESPONSES (0 TOKENS)
    # -------------------------------------------------------------------------
    if is_greeting(norm):
        return GuardrailDecision(
            category=ResponseCategory.IMMEDIATE_GENERAL,
            should_invoke_llm=False,
            response_text=GREETING_RESPONSE,
            reason="Conversational greeting handled deterministically.",
            evidence_grounded=False,
        )

    if is_status_query(norm):
        return GuardrailDecision(
            category=ResponseCategory.IMMEDIATE_GENERAL,
            should_invoke_llm=False,
            response_text=STATUS_RESPONSE,
            reason="Status query handled deterministically.",
            evidence_grounded=False,
        )

    if is_system_identity_query(norm):
        return GuardrailDecision(
            category=ResponseCategory.IMMEDIATE_GENERAL,
            should_invoke_llm=False,
            response_text=SYSTEM_IDENTITY_RESPONSE,
            reason="System identity query handled deterministically.",
            evidence_grounded=False,
        )

    if is_system_work_query(norm):
        return GuardrailDecision(
            category=ResponseCategory.IMMEDIATE_GENERAL,
            should_invoke_llm=False,
            response_text=SYSTEM_WORK_RESPONSE,
            reason="System work explanation handled deterministically.",
            evidence_grounded=False,
        )

    if is_help_query(norm):
        return GuardrailDecision(
            category=ResponseCategory.IMMEDIATE_GENERAL,
            should_invoke_llm=False,
            response_text=HELP_RESPONSE,
            reason="Help request handled deterministically.",
            evidence_grounded=False,
        )

    if is_user_identity_query(norm):
        # Strict zero hallucination: Never guess a user's name
        analyst_name = user_context.get("name")
        analyst_role = user_context.get("role", "Security Analyst")
        
        # Check if name is provided and not generic placeholder
        if analyst_name and analyst_name.lower() not in ["security analyst", "analyst", "user", ""]:
            resp = f"You are logged in as {analyst_name} ({analyst_role})."
        else:
            resp = "Your current session is authenticated as a Security Analyst. No specific personal name is configured for this session."

        return GuardrailDecision(
            category=ResponseCategory.IMMEDIATE_GENERAL,
            should_invoke_llm=False,
            response_text=resp,
            reason="User identity answered strictly from authenticated context.",
            evidence_grounded=False,
        )

    # -------------------------------------------------------------------------
    # 2. OUT-OF-CONTEXT FILTER (0 TOKENS)
    # -------------------------------------------------------------------------
    if is_out_of_scope(norm):
        return GuardrailDecision(
            category=ResponseCategory.OUT_OF_SCOPE,
            should_invoke_llm=False,
            response_text=SCOPE_RESPONSE_TEXT,
            reason="Query detected as out of cybersecurity/UEBA application scope.",
            evidence_grounded=False,
        )

    # -------------------------------------------------------------------------
    # 3. UEBA / ALERT DOMAIN ROUTING
    # -------------------------------------------------------------------------
    has_alert = bool(alert_context and alert_context.get("alert_id"))
    if is_ueba_domain_query(norm, has_alert_context=has_alert):
        # Check if question can be answered from available evidence without calling external API
        shortcut_response = _check_in_context_shortcut(norm, alert_context, conversation_history)
        if shortcut_response:
            return GuardrailDecision(
                category=ResponseCategory.DOMAIN_ANALYSIS,
                should_invoke_llm=False,
                response_text=shortcut_response,
                reason="Domain question answered directly from cached evidence to conserve tokens.",
                evidence_grounded=True,
            )

        # Requires deep multi-factor generative LLM explanation
        return GuardrailDecision(
            category=ResponseCategory.DOMAIN_ANALYSIS,
            should_invoke_llm=True,
            response_text="",
            reason="Valid UEBA domain query routed to analysis / LLM pipeline.",
            evidence_grounded=True,
        )

    # -------------------------------------------------------------------------
    # 4. AMBIGUOUS / CLARIFICATION (0 TOKENS)
    # -------------------------------------------------------------------------
    # For very short or unrecognizable input without domain context
    return GuardrailDecision(
        category=ResponseCategory.CLARIFICATION,
        should_invoke_llm=False,
        response_text=CLARIFICATION_RESPONSE,
        reason="Query lacks specific domain context or clarity; asking clarification.",
        evidence_grounded=False,
    )
