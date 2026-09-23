from __future__ import annotations
import json

class DeterministicSynthesizer:
    def synthesize(self, question, plan, results):
        if not results:
            return (
                "No supported analytical task was generated for this question."
            )
        sections = [f"Question: {question}", "", "Analytical results:"]
        for result in results:
            sections.append(f"\n[{result.tool_name}]")
            if result.error:
                sections.append(f"ERROR: {result.error}")
            else:
                payload = result.result
                if hasattr(payload, "to_dict"):
                    payload = payload.to_dict()
                sections.append(json.dumps(payload, indent=2, default=str))
        return "\n".join(sections)
