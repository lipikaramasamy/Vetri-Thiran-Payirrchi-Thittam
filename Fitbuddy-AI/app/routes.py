from datetime import datetime

from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from sqlalchemy.orm import Session

from .config import settings
from .database import SessionLocal, User, FitnessPlan
from .schemas import UserInput, FeedbackInput

from .ai.gemini_generator import generate_workout_plan
from .ai.gemini_flash_generator import generate_nutrition_tip
from .ai.updated_plan import generate_updated_plan


router = APIRouter()

templates = Jinja2Templates(directory="templates")


# ---------------------------------------------------------
# DATABASE HELPER
# ---------------------------------------------------------

def get_database():
    db = SessionLocal()

    try:
        return db

    except Exception:
        db.close()
        raise


# ---------------------------------------------------------
# HOME PAGE
# ---------------------------------------------------------

@router.get("/")
def home(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={}
    )


# ---------------------------------------------------------
# GENERATE FITNESS PLAN
# ---------------------------------------------------------

@router.post("/generate")
def generate_plan(
    request: Request,

    user_id: str = Form(...),
    name: str = Form(...),
    age: int = Form(...),
    weight: float = Form(...),
    goal: str = Form(...),
    intensity: str = Form(...),
):

    db: Session = get_database()

    try:

        # Validate input using Pydantic
        user_input = UserInput(
            user_id=user_id,
            name=name,
            age=age,
            weight=weight,
            goal=goal,
            intensity=intensity,
        )

        # Check whether user already exists
        user = (
            db.query(User)
            .filter(User.user_id == user_input.user_id)
            .first()
        )

        # -------------------------------------------------
        # CREATE USER
        # -------------------------------------------------

        if user is None:

            user = User(
                user_id=user_input.user_id,
                name=user_input.name,
                age=user_input.age,
                weight=user_input.weight,
                goal=user_input.goal,
                intensity=user_input.intensity,
            )

            db.add(user)
            db.commit()
            db.refresh(user)

        # -------------------------------------------------
        # UPDATE EXISTING USER
        # -------------------------------------------------

        else:

            user.name = user_input.name
            user.age = user_input.age
            user.weight = user_input.weight
            user.goal = user_input.goal
            user.intensity = user_input.intensity

            db.commit()
            db.refresh(user)

        # -------------------------------------------------
        # GENERATE WORKOUT PLAN USING GEMINI
        # -------------------------------------------------

        workout_plan = generate_workout_plan(
            name=user.name,
            age=user.age,
            weight=user.weight,
            goal=user.goal,
            intensity=user.intensity,
        )

        # -------------------------------------------------
        # GENERATE NUTRITION TIP
        # -------------------------------------------------

        nutrition_tip = generate_nutrition_tip(
            age=user.age,
            goal=user.goal,
        )

        # -------------------------------------------------
        # SAVE FITNESS PLAN
        # -------------------------------------------------

        fitness_plan = FitnessPlan(
            user_id=user.id,
            workout_plan=workout_plan,
            nutrition_tip=nutrition_tip,
        )

        db.add(fitness_plan)
        db.commit()
        db.refresh(fitness_plan)

        # -------------------------------------------------
        # RESULT PAGE
        # -------------------------------------------------

        return templates.TemplateResponse(
            request=request,
            name="result.html",
            context={
                "user": user,
                "plan": fitness_plan,
                "error": None,
            }
        )

    except Exception as error:

        db.rollback()

        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "error": str(error)
            }
        )

    finally:

        db.close()


# ---------------------------------------------------------
# UPDATE PLAN USING USER FEEDBACK
# ---------------------------------------------------------

@router.post("/update-plan")
def update_plan(
    request: Request,

    user_id: str = Form(...),
    feedback: str = Form(...),
):

    db: Session = get_database()

    try:

        # -------------------------------------------------
        # VALIDATE FEEDBACK
        # -------------------------------------------------

        feedback_input = FeedbackInput(
            user_id=user_id,
            feedback=feedback,
        )

        # -------------------------------------------------
        # FIND USER
        # -------------------------------------------------

        user = (
            db.query(User)
            .filter(User.user_id == feedback_input.user_id)
            .first()
        )

        if user is None:

            return templates.TemplateResponse(
                request=request,
                name="index.html",
                context={
                    "error": "User not found."
                }
            )

        # -------------------------------------------------
        # GET LATEST PLAN
        # -------------------------------------------------

        current_plan = (
            db.query(FitnessPlan)
            .filter(FitnessPlan.user_id == user.id)
            .order_by(FitnessPlan.id.desc())
            .first()
        )

        if current_plan is None:

            return templates.TemplateResponse(
                request=request,
                name="index.html",
                context={
                    "error": "No fitness plan found for this user."
                }
            )

        # -------------------------------------------------
        # GENERATE UPDATED PLAN
        # -------------------------------------------------

        updated_plan = generate_updated_plan(
            name=user.name,
            age=user.age,
            weight=user.weight,
            goal=user.goal,
            intensity=user.intensity,
            current_plan=current_plan.workout_plan,
            feedback=feedback_input.feedback,
        )

        # -------------------------------------------------
        # SAVE FEEDBACK + UPDATED PLAN
        # -------------------------------------------------

        current_plan.feedback = feedback_input.feedback
        current_plan.updated_plan = updated_plan
        current_plan.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(current_plan)

        # -------------------------------------------------
        # SHOW RESULT
        # -------------------------------------------------

        return templates.TemplateResponse(
            request=request,
            name="result.html",
            context={
                "user": user,
                "plan": current_plan,
                "error": None,
            }
        )

    except Exception as error:

        db.rollback()

        # Try to find user again for displaying result page
        user = (
            db.query(User)
            .filter(User.user_id == user_id)
            .first()
        )

        if user is not None:

            latest_plan = (
                db.query(FitnessPlan)
                .filter(FitnessPlan.user_id == user.id)
                .order_by(FitnessPlan.id.desc())
                .first()
            )

            return templates.TemplateResponse(
                request=request,
                name="result.html",
                context={
                    "user": user,
                    "plan": latest_plan,
                    "error": str(error),
                }
            )

        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "error": str(error)
            }
        )

    finally:

        db.close()


# ---------------------------------------------------------
# ADMIN - ALL USERS
# ---------------------------------------------------------

@router.get("/all-users")
def all_users(
    request: Request,
    key: str = "",
):

    # -----------------------------------------------------
    # ADMIN KEY CHECK
    # -----------------------------------------------------

    if key != settings.ADMIN_KEY:

        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "error": "Invalid admin key."
            }
        )

    db: Session = get_database()

    try:

        users = (
            db.query(User)
            .order_by(User.id.desc())
            .all()
        )

        # -------------------------------------------------
        # LOAD PLANS FOR EACH USER
        # -------------------------------------------------

        user_data = []

        for user in users:

            plans = (
                db.query(FitnessPlan)
                .filter(FitnessPlan.user_id == user.id)
                .order_by(FitnessPlan.id.desc())
                .all()
            )

            user_data.append(
                {
                    "user": user,
                    "plans": plans,
                }
            )

        return templates.TemplateResponse(
            request=request,
            name="all_users.html",
            context={
                "users": user_data,
                "admin_key": key,
            }
        )

    finally:

        db.close()


# ---------------------------------------------------------
# API INFORMATION
# ---------------------------------------------------------

@router.get("/health")
def health_check():

    return {
        "status": "healthy",
        "application": "FitBuddy",
    }