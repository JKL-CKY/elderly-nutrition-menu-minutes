from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class Elderly(Base):
    __tablename__ = "elderly"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    age = Column(Integer)
    gender = Column(String(10))
    room_number = Column(String(20))
    medical_history = Column(Text)
    dietary_restrictions = Column(Text)
    allergies = Column(Text)
    food_texture = Column(String(50))
    weight = Column(Float)
    height = Column(Float)
    bmi = Column(Float)
    activity_level = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    health_records = relationship("HealthRecord", back_populates="elderly")
    family_members = relationship("FamilyMember", back_populates="elderly")

class HealthRecord(Base):
    __tablename__ = "health_records"

    id = Column(Integer, primary_key=True, index=True)
    elderly_id = Column(Integer, ForeignKey("elderly.id"))
    blood_pressure = Column(String(20))
    blood_sugar = Column(Float)
    cholesterol = Column(Float)
    heart_disease = Column(Boolean, default=False)
    diabetes = Column(Boolean, default=False)
    kidney_disease = Column(Boolean, default=False)
    notes = Column(Text)
    record_date = Column(DateTime, default=datetime.utcnow)

    elderly = relationship("Elderly", back_populates="health_records")

class FamilyMember(Base):
    __tablename__ = "family_members"

    id = Column(Integer, primary_key=True, index=True)
    elderly_id = Column(Integer, ForeignKey("elderly.id"))
    name = Column(String(100))
    relationship = Column(String(50))
    email = Column(String(100))
    phone = Column(String(20))
    is_representative = Column(Boolean, default=False)

    elderly = relationship("Elderly", back_populates="family_members")

class MeetingRecording(Base):
    __tablename__ = "meeting_recordings"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200))
    audio_file_path = Column(String(500))
    meeting_date = Column(DateTime, default=datetime.utcnow)
    transcription = Column(Text)
    diarization_result = Column(Text)
    processed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class MenuPlan(Base):
    __tablename__ = "menu_plans"

    id = Column(Integer, primary_key=True, index=True)
    week_start = Column(DateTime)
    week_end = Column(DateTime)
    markdown_content = Column(Text)
    assessment_form = Column(Text)
    sent_to_families = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    meeting_id = Column(Integer, ForeignKey("meeting_recordings.id"))

class NutritionRequirement(Base):
    __tablename__ = "nutrition_requirements"

    id = Column(Integer, primary_key=True, index=True)
    elderly_id = Column(Integer, ForeignKey("elderly.id"))
    calories = Column(Float)
    protein = Column(Float)
    carbohydrates = Column(Float)
    fat = Column(Float)
    fiber = Column(Float)
    sodium = Column(Float)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
