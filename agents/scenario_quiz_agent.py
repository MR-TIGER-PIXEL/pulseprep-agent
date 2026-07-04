from tools.quiz_tools import get_scenario, score_response


class ScenarioQuizAgent:
    """Generates CPR/AED practice scenarios and evaluates responses."""

    def create_question(self, setting: str = "basketball") -> str:
        scenario = get_scenario(setting)
        return f"""
## Practice Scenario: {scenario.setting.title()}

{scenario.scenario}

**Question:** {scenario.question}

Reply with what you would do first and what you would ask others to do.
""".strip()

    def evaluate_answer(self, answer: str, setting: str = "basketball") -> str:
        scenario = get_scenario(setting)
        result = score_response(answer, scenario.expected_steps)
        matched = "\n".join([f"- {step}" for step in result["matched_steps"]]) or "- None detected"
        missing = "\n".join([f"- {step}" for step in result["missing_steps"]]) or "- No major expected steps missing"

        return f"""
## Quiz Feedback

Score: **{result['score']} / {result['possible']} key steps detected**

### You included
{matched}

### Consider adding
{missing}

### Model response
A strong response would be: **Call 911 or local emergency services immediately, send someone to get the AED, begin CPR if trained and safe, and follow the AED voice prompts when it arrives.**
""".strip()
