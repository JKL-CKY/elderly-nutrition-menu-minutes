from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime

class ElderlyBase(BaseModel):
    name: str
    age: Optional[int] = None
    gender: Optional[str] = None
    room_number: Optional[str] = None
    medical_history: Optional[str] = None
    dietary_restrictions: Optional[str] = None
    allergies: Optional[str] = None
    food_texture: Optional[str] = None
    weight: Optional[float] = None
    height: Optional[float] = None
    bmi: Optional[float] = None
    activity_level: Optional[str] = None

class ElderlyCreate(ElderlyBase):
    pass

class ElderlyUpdate(ElderlyBase):
    pass

class ElderlyResponse(ElderlyBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class HealthRecordBase(BaseModel):
    elderly_id: int
    blood_pressure: Optional[str] = None
    blood_sugar: Optional[float] = None
    cholesterol: Optional[float] = None
    heart_disease: Optional[bool] = False
    diabetes: Optional[bool] = False
    kidney_disease: Optional[bool] = False
    notes: Optional[str] = None

class HealthRecordCreate(HealthRecordBase):
    pass

class HealthRecordResponse(HealthRecordBase):
    id: int
    record_date: datetime

    class Config:
        from_attributes = True

class FamilyMemberBase(BaseModel):
    elderly_id: int
    name: Optional[str] = None
    relationship: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    is_representative: Optional[bool] = False

class FamilyMemberCreate(FamilyMemberBase):
    pass

class FamilyMemberResponse(FamilyMemberBase):
    id: int

    class Config:
        from_attributes = True

class MeetingRecordingBase(BaseModel):
    title: str
    audio_file_path: Optional[str] = None

class MeetingRecordingCreate(MeetingRecordingBase):
    pass

class MeetingRecordingResponse(MeetingRecordingBase):
    id: int
    meeting_date: datetime
    transcription: Optional[str] = None
    diarization_result: Optional[str] = None
    processed: bool
    created_at: datetime

    class Config:
        from_attributes = True

class TranscriptionSegment(BaseModel):
    start: float
    end: float
    text: str
    role: Optional[str] = None

class NutritionRequirementBase(BaseModel):
    elderly_id: int
    calories: Optional[float] = None
    protein: Optional[float] = None
    carbohydrates: Optional[float] = None
    fat: Optional[float] = None
    fiber: Optional[float] = None
    sodium: Optional[float] = None
    notes: Optional[str] = None

class NutritionRequirementCreate(NutritionRequirementBase):
    pass

class NutritionRequirementResponse(NutritionRequirementBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class MenuPlanBase(BaseModel):
    week_start: datetime
    week_end: datetime
    markdown_content: Optional[str] = None
    assessment_form: Optional[str] = None
    meeting_id: Optional[int] = None

class MenuPlanCreate(MenuPlanBase):
    pass

class MenuPlanResponse(MenuPlanBase):
    id: int
    sent_to_families: bool
    created_at: datetime

    class Config:
        from_attributes = True

class NutritionCalculateRequest(BaseModel):
    weight_kg: float
    height_cm: float
    age: int
    gender: str
    activity_level: str
    health_conditions: Optional[List[str]] = []

class NutritionCalculateResponse(BaseModel):
    bmi: float
    bmi_category: str
    bmr: float
    tdee: float
    requirements: Dict
    advice: str

class ProcessMeetingRequest(BaseModel):
    meeting_id: int

class ProcessMeetingResponse(BaseModel):
    meeting_id: int
    transcription: str
    diarization_result: Dict
    nutrition_requirements: Dict
    meeting_summary: str
    menu_plan: Optional[Dict] = None

class SendMenuRequest(BaseModel):
    menu_plan_id: int

class SendMenuResponse(BaseModel):
    success: bool
    sent_count: int
    message: str
