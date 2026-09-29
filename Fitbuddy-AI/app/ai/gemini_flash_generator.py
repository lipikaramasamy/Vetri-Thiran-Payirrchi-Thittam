from .gemini_client import generate_content


def generate_nutrition_tip(
    age: int,
    goal: str,
) -> str:

    if age < 18:

        safety_instruction = """
The user is under 18.

Do not recommend calorie restriction,
fasting, weight-loss dieting, or supplements.

Focus on balanced meals, hydration,
sleep, and normal nutritious foods.
"""

    else:

        safety_instruction = """
Provide general nutrition and recovery
information only.
"""


    prompt = f"""
You are FitBuddy, an AI fitness assistant.

Generate one short and practical
nutrition or recovery tip.

USER AGE:
{age}

FITNESS GOAL:
{goal}

{safety_instruction}

The tip can discuss:

- balanced meals
- hydration
- sleep
- recovery
- nutritious everyday foods

Keep the answer between 3 and 5 sentences.

Do not provide medical treatment.

Return ONLY the tip.
"""


    return generate_content(prompt)