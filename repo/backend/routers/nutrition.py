from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from .. import models, schemas
from ..services.nutrition_calculator import NutritionCalculator

router = APIRouter(prefix="/api/nutrition", tags=["营养计算"])

@router.post("/calculate", response_model=schemas.NutritionCalculateResponse)
def calculate_nutrition(request: schemas.NutritionCalculateRequest):
    bmi = NutritionCalculator.calculate_bmi(request.weight_kg, request.height_cm / 100)
    bmi_category = NutritionCalculator.get_bmi_category(bmi)
    bmr = NutritionCalculator.calculate_bmr(
        request.weight_kg, request.height_cm, request.age, request.gender
    )
    tdee = NutritionCalculator.calculate_tdee(bmr, request.activity_level)
    requirements = NutritionCalculator.calculate_nutrient_requirements(
        request.weight_kg, request.height_cm, request.age, request.gender,
        request.activity_level, request.health_conditions
    )
    advice = NutritionCalculator.generate_nutrition_advice(
        bmi, requirements, request.health_conditions
    )
    
    return schemas.NutritionCalculateResponse(
        bmi=bmi,
        bmi_category=bmi_category,
        bmr=bmr,
        tdee=tdee,
        requirements=requirements,
        advice=advice
    )

@router.get("/requirements", response_model=List[schemas.NutritionRequirementResponse])
def get_nutrition_requirements(elderly_id: int = None, db: Session = Depends(get_db)):
    query = db.query(models.NutritionRequirement)
    if elderly_id:
        query = query.filter(models.NutritionRequirement.elderly_id == elderly_id)
    return query.all()

@router.post("/requirements", response_model=schemas.NutritionRequirementResponse)
def create_nutrition_requirement(requirement: schemas.NutritionRequirementCreate, db: Session = Depends(get_db)):
    db_requirement = models.NutritionRequirement(**requirement.dict())
    db.add(db_requirement)
    db.commit()
    db.refresh(db_requirement)
    return db_requirement

@router.post("/calculate-meal")
def calculate_meal_nutrition(meal_items: List[dict]):
    result = NutritionCalculator.calculate_meal_nutrition(meal_items)
    return result
