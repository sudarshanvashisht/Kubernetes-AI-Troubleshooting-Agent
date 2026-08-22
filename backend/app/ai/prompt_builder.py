"""Prompt builder for the AI Kubernetes Troubleshooting Agent.

Generates structured system and user prompts to guide the LLM
in acting as a Senior Kubernetes SRE.
"""

import json
from typing import Any

class PromptBuilder:
    """Helper to build SRE-focused prompts for LLM cluster analysis."""

    def build_system_prompt(self) -> str:
        """Create the system prompt defining the SRE persona and response format."""
        return (
            "You are a Senior Kubernetes Site Reliability Engineer (SRE). Your task is to analyze "
            "the provided Kubernetes cluster investigation data, diagnose the root cause of any failures, "
            "recommend actionable, Kubernetes-specific fixes, and assign a confidence score to your diagnosis.\n\n"
            "Analyze the data carefully. Check pod statuses, container restart counts, error logs, Warning events, "
            "deployment replicas, service configurations, and missing endpoints. Correlate information to find "
            "the underlying problem instead of just summarizing logs. For example, if logs show connection failures, "
            "check if the corresponding service exists or if endpoints are missing.\n\n"
            "You MUST respond ONLY with a valid JSON object matching this structure. Do not include markdown blocks "
            "like ```json or any other text before/after the JSON. Just return the JSON object directly.\n\n"
            "{\n"
            '  "root_cause": "A concise description of the root cause",\n'
            '  "explanation": "A detailed explanation of why the failure occurred and how you correlated the evidence",\n'
            '  "fix": "A practical, beginner-friendly, actionable description of the suggested fix",\n'
            '  "kubectl_commands": [\n'
            '    "kubectl command 1",\n'
            '    "kubectl command 2"\n'
            '  ],\n'
            '  "prevention": "Recommendations on how to prevent this issue in the future",\n'
            '  "confidence": 95,\n'
            '  "confidence_reasoning": "Brief explanation of why you gave this confidence score (e.g. correlated pods, logs, and events)"\n'
            "}"
        )

    def build_user_prompt(self, investigation_data: dict[str, Any]) -> str:
        """Format the gathered Kubernetes evidence into the user prompt."""
        # Convert investigation data into a formatted string to pass to the LLM
        formatted_data = {
            "pods": investigation_data.get("pods", {}),
            "logs": investigation_data.get("logs", []),
            "events": investigation_data.get("events", {}),
            "deployments": investigation_data.get("deployments", {}),
            "network": investigation_data.get("network", {})
        }
        
        return (
            "Here is the collected Kubernetes investigation data for analysis:\n\n"
            f"{json.dumps(formatted_data, indent=2)}\n\n"
            "Please diagnose the cluster issues and return the structured JSON output."
        )

prompt_builder = PromptBuilder()
