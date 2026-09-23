# ============================================================
# PharmaLens AI
# Project 09 - AI Agent
# ============================================================

import os
import json

from typing import Dict, Any, Optional

from .tools import (
    execute_tool,
    get_available_tools
)

from .prompts import SYSTEM_PROMPT


# ============================================================
# PHARMALENS AGENT
# ============================================================

class PharmaLensAgent:

    def __init__(
        self,
        model=None,
        provider=None
    ):

        self.model = model
        self.provider = provider

        self.system_prompt = SYSTEM_PROMPT

        self.tools = get_available_tools()


    # ========================================================
    # TOOL SELECTION
    # ========================================================

    def select_tool(
        self,
        question: str
    ) -> Optional[str]:

        question_lower = question.lower()

        # Market
        if any(
            word in question_lower
            for word in [
                "market",
                "market size",
                "market growth",
                "market share"
            ]
        ):
            return "market_tool"


        # Brand
        if any(
            word in question_lower
            for word in [
                "brand",
                "product performance"
            ]
        ):
            return "brand_tool"


        # Company
        if any(
            word in question_lower
            for word in [
                "company",
                "manufacturer"
            ]
        ):
            return "company_tool"


        # Forecast
        if any(
            word in question_lower
            for word in [
                "forecast",
                "future",
                "prediction",
                "predict"
            ]
        ):
            return "forecast_tool"


        # Launch
        if any(
            word in question_lower
            for word in [
                "launch",
                "launched",
                "new product"
            ]
        ):
            return "launch_tool"


        # GTM
        if any(
            word in question_lower
            for word in [
                "gtm",
                "go to market",
                "channel",
                "distribution"
            ]
        ):
            return "gtm_tool"


        # Recommendation
        if any(
            word in question_lower
            for word in [
                "recommend",
                "opportunity",
                "opportunities",
                "strategy"
            ]
        ):
            return "recommendation_tool"


        # Similarity
        if any(
            word in question_lower
            for word in [
                "similar",
                "competitor",
                "competition",
                "competitors"
            ]
        ):
            return "similarity_tool"


        # Molecule
        if any(
            word in question_lower
            for word in [
                "molecule",
                "active ingredient",
                "ingredient"
            ]
        ):
            return "molecule_tool"


        return "market_tool"


    # ========================================================
    # QUESTION ROUTING
    # ========================================================

    def route_question(
        self,
        question: str,
        parameters: Optional[Dict[str, Any]] = None
    ):

        tool_name = self.select_tool(question)

        parameters = parameters or {}

        result = execute_tool(
            tool_name,
            parameters
        )

        return {
            "question": question,
            "tool": tool_name,
            "result": result
        }


    # ========================================================
    # BASIC RESPONSE
    # ========================================================

    def basic_response(
        self,
        question: str,
        result: Dict[str, Any]
    ):

        tool = result["tool"]

        data = result["result"]

        if data.get("status") == "not_found":

            return (
                f"I could not find sufficient data for "
                f"the requested entity."
            )

        if data.get("status") == "no_data":

            return (
                "I could not find sufficient data to "
                "answer this question."
            )

        if data.get("status") == "error":

            return (
                "An error occurred while analyzing "
                "the requested data."
            )

        return (
            f"PharmaLens AI analyzed the question using "
            f"{tool}.\n\n"
            f"Key result:\n"
            f"{json.dumps(data, indent=2, default=str)}"
        )


    # ========================================================
    # MAIN ASK METHOD
    # ========================================================

    def ask(
        self,
        question: str,
        parameters: Optional[Dict[str, Any]] = None
    ):

        result = self.route_question(
            question,
            parameters
        )

        return self.basic_response(
            question,
            result
        )


# ============================================================
# CREATE DEFAULT AGENT
# ============================================================

pharmalens_agent = PharmaLensAgent()


# ============================================================
# CLI TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 60)

    print("PharmaLens AI Agent")

    print("=" * 60)

    print("\nAvailable tools:")

    for tool in pharmalens_agent.tools:

        print("-", tool)

    print("\nAgent is ready.")