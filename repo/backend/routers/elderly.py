from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from .. import models, schemas
from ..services.nutrition_calculator import NutritionCalculator

router = APIRouter(prefix="/api/elderly", tags=["老人档案"])

@router.get("/", response_model=List[schemas.ElderlyResponse])
def get_elderly_list(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    elderly = db.query(models.Elderly).offset(skip).limit(limit).all()
    return elderly

@router.get("/{elderly_id}", response_model=schemas.ElderlyResponse)
def get_elderly(elderly_id: int, db: Session = Depends(get_db)):
    elderly = db.query(models.Elderly).filter(models.Elderly.id == elderly_id).first()
    if not elderly:
        raise HTTPException(status_code=404, detail="老人信息不存在")
    return elderly

@router.post("/", response_model=schemas.ElderlyResponse)
def create_elderly(elderly: schemas.ElderlyCreate, db: Session = Depends(get_db)):
    bmi = None
    if elderly.weight and elderly.height:
        bmi = NutritionCalculator.calculate_bmi(elderly.weight, elderly.height / 100)
    
    db_elderly = models.Elderly(
        **elderly.dict(exclude={"bmi"}),
        bmi=bmi
    )
    db.add(db_elderly)
    db.commit()
    db.refresh(db_elderly)
    return db_elderly

@router.put("/{elderly_id}", response_model=schemas.ElderlyResponse)
def update_elderly(elderly_id: int, elderly_update: schemas.ElderlyUpdate, db: Session = Depends(get_db)):
    db_elderly = db.query(models.Elderly).filter(models.Elderly.id == elderly_id).first()
    if not db_elderly:
        raise HTTPException(status_code=404, detail="老人信息不存在")
    
    update_data = elderly_update.dict(exclude_unset=True)
    
    if "weight" in update_data or "height" in update_data:
        weight = update_data.get("weight", db_elderly.weight)
        height = update_data.get("height", db_elderly.height)
        if weight and height:
            update_data["bmi"] = NutritionCalculator.calculate_bmi(weight, height / 100)
    
    for key, value in update_data.items():
        setattr(db_elderly, key, value)
    
    db.commit()
    db.refresh(db_elderly)
    return db_elderly

@router.delete("/{elderly_id}")
def delete_elderly(elderly_id: int, db: Session = Depends(get_db)):
    db_elderly = db.query(models.Elderly).filter(models.Elderly.id == elderly_id).first()
    if not db_elderly:
        raise HTTPException(status_code=404, detail="老人信息不存在")
    
    db.delete(db_elderly)
    db.commit()
    return {"message": "删除成功"}

@router.get("/{elderly_id}/health-records", response_model=List[schemas.HealthRecordResponse])
def get_health_records(elderly_id: int, db: Session = Depends(get_db)):
    records = db.query(models.HealthRecord).filter(models.HealthRecord.elderly_id == elderly_id).all()
    return records

@router.post("/{elderly_id}/health-records", response_model=schemas.HealthRecordResponse)
def create_health_record(elderly_id: int, record: schemas.HealthRecordCreate, db: Session = Depends(get_db)):
    db_record = models.HealthRecord(**record.dict())
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record

@router.get("/{elderly_id}/family-members", response_model=List[schemas.FamilyMemberResponse])
def get_family_members(elderly_id: int, db: Session = Depends(get_db)):
    members = db.query(models.FamilyMember).filter(models.FamilyMember.elderly_id == elderly_id).all()
    return members

@router.post("/{elderly_id}/family-members", response_model=schemas.FamilyMemberResponse)
def create_family_member(elderly_id: int, member: schemas.FamilyMemberCreate, db: Session = Depends(get_db)):
    db_member = models.FamilyMember(**member.dict())
    db.add(db_member)
    db.commit()
    db.refresh(db_member)
    return db_member
