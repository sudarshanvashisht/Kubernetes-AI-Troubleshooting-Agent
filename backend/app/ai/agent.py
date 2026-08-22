"""AI agent for Kubernetes cluster analysis.

Uses OpenRouter LLM capabilities to reason about cluster data
and generate actionable SRE diagnoses.
"""

import json
from typing import Any
from loguru import logger

from app.ai.prompt_builder import prompt_builder
from app.ai.llm_client import llm_client

class KubernetesAgent:
    """Orchestrates LLM cluster diagnosis using prompts and client."""

    async def analyze_cluster(self, cluster_data: dict[str, Any]) -> dict[str, Any]:
        """Analyze Kubernetes cluster data and produce a structured diagnosis.

        Args:
            cluster_data: Collected Kubernetes cluster information.

        Returns:
            Dict containing root cause, explanation, fix recommendations,
            kubectl commands, prevention recommendations, and confidence score.
        """
        logger.info("Starting AI cluster analysis...")

        try:
            # Build prompts
            system_prompt = prompt_builder.build_system_prompt()
            user_prompt = prompt_builder.build_user_prompt(cluster_data)

            # Query OpenRouter
            response_text = await llm_client.chat(system_prompt, user_prompt)
            
            # Parse response
            diagnosis = self._parse_response(response_text)
            logger.info("AI analysis complete and successfully parsed")
            return diagnosis

        except Exception as e:
            logger.error(f"AI cluster analysis failed: {e}")
            return {
                "root_cause": "Failed to run AI analysis",
                "explanation": f"An error occurred while communicating with the reasoning model: {str(e)}",
                "fix": "Ensure OPENROUTER_API_KEY is configured correctly and try again.",
                "kubectl_commands": [],
                "prevention": "Monitor the availability of the OpenRouter backend.",
                "confidence": 0,
                "confidence_reasoning": f"Error: {str(e)}"
            }

    def _parse_response(self, text: str) -> dict[str, Any]:
        """Clean and parse JSON from the raw LLM response."""
        # Find JSON boundaries in case the model included any markdown wrapping or preamble
        cleaned = text.strip()
        
        # Strip markdown codeblock if present
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
            
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
            
        cleaned = cleaned.strip()

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse LLM response as JSON. Raw text: {text}")
            logger.warning(f"JSON parsing error: {e}")
            # Return a fallback dict populated with the raw text
            return {
                "root_cause": "Raw AI Output (JSON Parse Failure)",
                "explanation": f"The model responded but the output was not valid JSON. Raw output: {text}",
                "fix": "Review the raw explanation to troubleshoot.",
                "kubectl_commands": [],
                "prevention": "Ensure prompts are guiding the model to output strict JSON.",
                "confidence": 50,
                "confidence_reasoning": "Could not parse JSON response from LLM."
            }

kubernetes_agent = KubernetesAgent()
