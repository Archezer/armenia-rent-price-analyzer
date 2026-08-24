from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class PredictionRequest(BaseModel):

    model_config = ConfigDict(
        extra='forbid',
        str_strip_whitespace=True,
    )

    city: Literal['Yerevan', 'Gyumri']
    district: str = Field(
        min_length=1,
        max_length=100
    )
    rooms: int = Field(
        gt=0,
        le=20,
    )
    area_sqm: float = Field(
        gt=0,
        le=1_000,
    )
    floor: int = Field(
        ge=0,
        le=200,
    )
    total_floors: int = Field(
        gt=0,
        le=200,
    )

    @model_validator(mode='after')
    def validate_floor_relation(self) -> 'PredictionRequest':
        """Reject apartments above the declared building height."""
        if self.floor > self.total_floors:
            raise ValueError('Floor must be less than or equal to total floors.')
        return self

class PredictionResponse(BaseModel):
    predicted_monthly_rent_amd: int
    currency: Literal['AMD']
    model_version: str

class HealthResponse(BaseModel):
    status: Literal['OK']
    model_version: str

class RecommendationRequest(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    city: Literal["Yerevan", "Gyumri"]
    district: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )
    rooms: int | None = Field(
        default=None,
        gt=0,
        le=20,
    )
    min_area_sqm: float | None = Field(
        default=None,
        gt=0,
        le=1_000,
    )
    max_area_sqm: float | None = Field(
        default=None,
        gt=0,
        le=1_000,
    )
    max_budget_amd: float | None = Field(
        default=None,
        gt=0,
    )
    limit: int = Field(
        default=5,
        ge=1,
        le=20,
    )

    @model_validator(mode="after")
    def validate_area_range(
        self,
    ) -> "RecommendationRequest":
        if (
            self.min_area_sqm is not None
            and self.max_area_sqm is not None
            and self.min_area_sqm
            > self.max_area_sqm
        ):
            raise ValueError(
                "min_area_sqm cannot exceed "
                "max_area_sqm"
            )

        return self


class RecommendationItem(BaseModel):
    city: str
    district: str
    rooms: int
    area_sqm: float
    floor: int
    total_floors: int
    estimated_monthly_rent_amd: int
    currency: Literal["AMD"]


class RecommendationResponse(BaseModel):
    model_version: str
    recommendations: list[RecommendationItem]