from pydantic import BaseModel, Field, field_validator


VALID_GOALS = {
    "weight loss",
    "muscle gain",
    "general wellness",
    "flexibility",
    "endurance",
}


VALID_INTENSITIES = {
    "low",
    "medium",
    "high",
}


class UserInput(BaseModel):

    user_id: str = Field(
        min_length=2,
        max_length=50
    )

    name: str = Field(
        min_length=2,
        max_length=100
    )

    age: int = Field(
        ge=13,
        le=100
    )

    weight: float = Field(
        gt=20,
        le=300
    )

    goal: str

    intensity: str


    @field_validator(
        "user_id",
        "name"
    )
    @classmethod
    def validate_text(cls, value):

        value = value.strip()

        if not value:

            raise ValueError(
                "This field cannot be empty."
            )

        return value


    @field_validator("goal")
    @classmethod
    def validate_goal(cls, value):

        value = value.strip().lower()

        if value not in VALID_GOALS:

            raise ValueError(
                "Invalid fitness goal."
            )

        return value


    @field_validator("intensity")
    @classmethod
    def validate_intensity(cls, value):

        value = value.strip().lower()

        if value not in VALID_INTENSITIES:

            raise ValueError(
                "Intensity must be low, medium, or high."
            )

        return value


class FeedbackInput(BaseModel):

    user_id: str = Field(
        min_length=2,
        max_length=50
    )

    feedback: str = Field(
        min_length=5,
        max_length=1000
    )


    @field_validator("feedback")
    @classmethod
    def validate_feedback(cls, value):

        value = value.strip()

        if not value:

            raise ValueError(
                "Feedback cannot be empty."
            )

        return value