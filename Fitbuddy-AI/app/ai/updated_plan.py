from .gemini_client import generate_content


def generate_updated_plan(
    name: str,
    age: int,
    weight: float,
    goal: str,
    intensity: str,
    current_plan: str,
    feedback: str,
) -> str:


    prompt = f"""
You are FitBuddy.

A user has provided feedback about their
AI-generated workout plan.

USER INFORMATION

Name: {name}
Age: {age}
Weight: {weight} kg
Goal: {goal}
Intensity: {intensity}


CURRENT WORKOUT PLAN

{current_plan}


USER FEEDBACK

{feedback}


TASK

Create a complete revised 7-day workout plan.

Do not only explain the changes.

Return:

Day 1
Day 2
Day 3
Day 4
Day 5
Day 6
Day 7

For every day include:

Focus:
Warm-up:
Main Workout:
Rest Guidance:
Cool-down:

Respect reasonable user feedback.

Maintain appropriate recovery.

Do not recommend:
- dangerous challenges
- extreme exercise
- extreme dieting
- medical treatment
- unsafe activities

If the requested change is unsafe,
provide a safer general-wellness alternative.

Return ONLY the revised workout plan.
"""


    return generate_content(prompt)