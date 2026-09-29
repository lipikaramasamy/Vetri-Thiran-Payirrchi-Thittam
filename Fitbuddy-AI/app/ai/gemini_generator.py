import os
import time

from dotenv import load_dotenv
from google import genai

load_dotenv()


# ============================================================
# GEMINI SETUP
# ============================================================

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY is missing in your .env file."
    )

client = genai.Client(api_key=API_KEY)

MODELS = [
    "gemini-3.8-flash",
    "gemini-3.7-flash",
    "gemini-3.5-flash-lite",
]


# ============================================================
# GEMINI REQUEST
# ============================================================

def ask_gemini(prompt: str) -> str:

    last_error = None

    for model in MODELS:

        print(f"\nTrying Gemini model: {model}")

        for attempt in range(3):

            try:

                response = client.models.generate_content(
                    model=model,
                    contents=prompt,
                )

                text = getattr(response, "text", None)

                if text:
                    print(f"Gemini success: {model}")
                    return text

                raise RuntimeError(
                    "Gemini returned an empty response."
                )

            except Exception as error:

                last_error = error
                error_text = str(error)

                print(
                    f"Gemini error | "
                    f"model={model} | "
                    f"attempt={attempt + 1}/3"
                )
                print(error_text)

                if (
                    "503" in error_text
                    or "UNAVAILABLE" in error_text
                    or "429" in error_text
                ):

                    wait_time = 2 ** attempt

                    print(
                        f"Retrying in {wait_time} seconds..."
                    )

                    time.sleep(wait_time)
                    continue

                break

    raise RuntimeError(
        f"Gemini API error: {last_error}"
    )


# ============================================================
# WORKOUT PLAN
# ============================================================

def generate_workout_plan(
    name=None,
    age=None,
    gender=None,
    weight=None,
    height=None,
    goal=None,
    fitness_goal=None,
    activity_level=None,
    workout_days=None,
    workout_location=None,
    **kwargs
):

    # --------------------------------------------------------
    # Accept either "goal" or "fitness_goal"
    # --------------------------------------------------------

    if not goal:
        goal = fitness_goal

    # --------------------------------------------------------
    # Accept possible alternative field names
    # --------------------------------------------------------

    if not workout_days:
        workout_days = kwargs.get("days_per_week")

    if not workout_location:
        workout_location = kwargs.get("location")

    # --------------------------------------------------------
    # Prompt
    # --------------------------------------------------------

    prompt = f"""
You are FitBuddy, a friendly fitness planning assistant.

Create a safe and realistic 7-day fitness plan.

USER INFORMATION
----------------

Name: {name}
Age: {age}
Gender: {gender}
Weight: {weight}
Height: {height}
Fitness Goal: {goal}
Activity Level: {activity_level}
Workout Days: {workout_days}
Workout Location: {workout_location}

PLAN REQUIREMENTS
-----------------

1. Create a simple 7-day schedule.

2. Include appropriate rest and recovery days.

3. Keep activities appropriate for the user's
   age and experience.

4. Focus on healthy movement, general fitness,
   strength, mobility and recovery.

5. Do not recommend extreme exercise.

6. Do not recommend restrictive eating.

7. Give general healthy nutrition and hydration
   guidance.

8. Include sleep and recovery advice.

9. If the user has pain, injury or another health
   concern, recommend speaking with a parent/guardian
   and an appropriate healthcare professional.

10. Keep the response easy to understand.

RESPONSE FORMAT
---------------

DAY 1
Workout:

DAY 2
Workout:

DAY 3
Workout:

DAY 4
Workout:

DAY 5
Workout:

DAY 6
Workout:

DAY 7
Workout:

GENERAL NUTRITION GUIDANCE

RECOVERY TIPS

SAFETY NOTE
"""

    return ask_gemini(prompt)