from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from .. import models, schemas
from ..services import (
    WhisperService,
    PyannoteService,
    SpacyNutritionService,
    OpenAIService,
    EmailService
)
import os
import json
from datetime import datetime

router = APIRouter(prefix="/api/meetings", tags=["会议管理"])

UPLOAD_DIR = "uploads/meetings"
os.makedirs(UPLOAD_DIR, exist_ok=True)

whisper_service = None
pyannote_service = None
spacy_service = None
openai_service = None
email_service = None

def get_services():
    global whisper_service, pyannote_service, spacy_service, openai_service, email_service
    if whisper_service is None:
        whisper_service = WhisperService()
    if pyannote_service is None:
        pyannote_service = PyannoteService()
    if spacy_service is None:
        spacy_service = SpacyNutritionService()
    if openai_service is None:
        openai_service = OpenAIService()
    if email_service is None:
        email_service = EmailService()
    return whisper_service, pyannote_service, spacy_service, openai_service, email_service

@router.get("/", response_model=List[schemas.MeetingRecordingResponse])
def get_meetings(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    meetings = db.query(models.MeetingRecording).offset(skip).limit(limit).all()
    return meetings

@router.get("/{meeting_id}", response_model=schemas.MeetingRecordingResponse)
def get_meeting(meeting_id: int, db: Session = Depends(get_db)):
    meeting = db.query(models.MeetingRecording).filter(models.MeetingRecording.id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="会议记录不存在")
    return meeting

@router.post("/", response_model=schemas.MeetingRecordingResponse)
async def create_meeting(title: str, audio_file: Optional[UploadFile] = File(None), db: Session = Depends(get_db)):
    audio_path = None
    if audio_file:
        audio_path = os.path.join(UPLOAD_DIR, f"{datetime.now().timestamp()}_{audio_file.filename}")
        with open(audio_path, "wb") as f:
            content = await audio_file.read()
            f.write(content)
    
    meeting = models.MeetingRecording(
        title=title,
        audio_file_path=audio_path
    )
    db.add(meeting)
    db.commit()
    db.refresh(meeting)
    return meeting

@router.post("/{meeting_id}/upload-audio")
async def upload_meeting_audio(meeting_id: int, audio_file: UploadFile = File(...), db: Session = Depends(get_db)):
    meeting = db.query(models.MeetingRecording).filter(models.MeetingRecording.id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="会议记录不存在")
    
    audio_path = os.path.join(UPLOAD_DIR, f"{meeting_id}_{datetime.now().timestamp()}_{audio_file.filename}")
    with open(audio_path, "wb") as f:
        content = await audio_file.read()
        f.write(content)
    
    meeting.audio_file_path = audio_path
    meeting.processed = False
    db.commit()
    db.refresh(meeting)
    return {"message": "音频上传成功", "audio_path": audio_path}

@router.post("/{meeting_id}/process")
def process_meeting(meeting_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    meeting = db.query(models.MeetingRecording).filter(models.MeetingRecording.id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="会议记录不存在")
    
    if not meeting.audio_file_path or not os.path.exists(meeting.audio_file_path):
        raise HTTPException(status_code=400, detail="会议音频文件不存在")
    
    background_tasks.add_task(process_meeting_task, meeting_id, db)
    
    return {"message": "会议处理已启动，请稍后查看结果"}

def process_meeting_task(meeting_id: int, db: Session):
    meeting = db.query(models.MeetingRecording).filter(models.MeetingRecording.id == meeting_id).first()
    if not meeting:
        return
    
    whisper_svc, pyannote_svc, spacy_svc, openai_svc, _ = get_services()
    
    try:
        transcription_result = whisper_svc.transcribe_with_timestamps(meeting.audio_file_path)
        meeting.transcription = transcription_result.get("full_text", "")
        
        diarization_result = pyannote_svc.diarize_audio(meeting.audio_file_path)
        meeting.diarization_result = json.dumps(diarization_result, ensure_ascii=False)
        
        transcription_segments = transcription_result.get("segments", [])
        annotated_segments = pyannote_svc.map_speakers_to_roles(
            diarization_result, transcription_segments
        )
        
        all_text = " ".join([seg["text"] for seg in annotated_segments])
        nutrition_requirements = spacy_svc.extract_all_requirements(all_text)
        
        meeting_summary = openai_svc.generate_meeting_summary(
            annotated_segments, nutrition_requirements
        )
        
        elderly_list = db.query(models.Elderly).all()
        elderly_profiles = []
        for e in elderly_list:
            health_records = db.query(models.HealthRecord).filter(models.HealthRecord.elderly_id == e.id).all()
            conditions = []
            for hr in health_records:
                if hr.diabetes:
                    conditions.append("糖尿病")
                if hr.heart_disease:
                    conditions.append("心脏病")
                if hr.kidney_disease:
                    conditions.append("肾病")
            elderly_profiles.append({
                "name": e.name,
                "age": e.age,
                "dietary_restrictions": e.dietary_restrictions,
                "food_texture": e.food_texture,
                "medical_history": e.medical_history,
                "health_conditions": conditions
            })
        
        menu_result = openai_svc.generate_weekly_menu(elderly_profiles, meeting_summary)
        
        menu_plan = models.MenuPlan(
            week_start=menu_result["week_start"],
            week_end=menu_result["week_end"],
            markdown_content=menu_result["markdown_content"],
            assessment_form=menu_result["assessment_form"],
            meeting_id=meeting_id
        )
        db.add(menu_plan)
        
        meeting.processed = True
        db.commit()
        
    except Exception as e:
        print(f"处理会议时出错: {str(e)}")
        meeting.transcription = f"处理失败: {str(e)}"
        db.commit()

@router.get("/{meeting_id}/transcription")
def get_meeting_transcription(meeting_id: int, db: Session = Depends(get_db)):
    meeting = db.query(models.MeetingRecording).filter(models.MeetingRecording.id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="会议记录不存在")
    
    if meeting.diarization_result:
        try:
            diarization = json.loads(meeting.diarization_result)
        except:
            diarization = {}
    else:
        diarization = {}
    
    return {
        "transcription": meeting.transcription,
        "diarization": diarization,
        "processed": meeting.processed
    }

@router.get("/{meeting_id}/menu-plan")
def get_meeting_menu_plan(meeting_id: int, db: Session = Depends(get_db)):
    menu_plan = db.query(models.MenuPlan).filter(models.MenuPlan.meeting_id == meeting_id).first()
    if not menu_plan:
        raise HTTPException(status_code=404, detail="该会议的菜单计划不存在")
    return {
        "id": menu_plan.id,
        "week_start": menu_plan.week_start,
        "week_end": menu_plan.week_end,
        "markdown_content": menu_plan.markdown_content,
        "assessment_form": menu_plan.assessment_form,
        "sent_to_families": menu_plan.sent_to_families
    }
