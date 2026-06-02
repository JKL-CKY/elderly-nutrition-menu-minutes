from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from .. import models, schemas
from ..services import OpenAIService, EmailService

router = APIRouter(prefix="/api/menu", tags=["菜单管理"])

openai_service = None
email_service = None

def get_services():
    global openai_service, email_service
    if openai_service is None:
        openai_service = OpenAIService()
    if email_service is None:
        email_service = EmailService()
    return openai_service, email_service

@router.get("/plans", response_model=List[schemas.MenuPlanResponse])
def get_menu_plans(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    plans = db.query(models.MenuPlan).order_by(models.MenuPlan.week_start.desc()).offset(skip).limit(limit).all()
    return plans

@router.get("/plans/{plan_id}", response_model=schemas.MenuPlanResponse)
def get_menu_plan(plan_id: int, db: Session = Depends(get_db)):
    plan = db.query(models.MenuPlan).filter(models.MenuPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="菜单计划不存在")
    return plan

@router.get("/plans/{plan_id}/markdown")
def get_menu_plan_markdown(plan_id: int, db: Session = Depends(get_db)):
    plan = db.query(models.MenuPlan).filter(models.MenuPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="菜单计划不存在")
    return {
        "markdown_content": plan.markdown_content,
        "assessment_form": plan.assessment_form
    }

@router.post("/plans/{plan_id}/send-to-families", response_model=schemas.SendMenuResponse)
def send_menu_to_families(plan_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    plan = db.query(models.MenuPlan).filter(models.MenuPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="菜单计划不存在")
    
    if plan.sent_to_families:
        return schemas.SendMenuResponse(
            success=True,
            sent_count=0,
            message="该菜单已经发送过给家属"
        )
    
    background_tasks.add_task(send_menu_to_families_task, plan_id, db)
    
    return schemas.SendMenuResponse(
        success=True,
        sent_count=0,
        message="正在发送菜单给家属，请稍后查看发送状态"
    )

def send_menu_to_families_task(plan_id: int, db: Session):
    plan = db.query(models.MenuPlan).filter(models.MenuPlan.id == plan_id).first()
    if not plan:
        return
    
    openai_svc, email_svc = get_services()
    
    elderly_list = db.query(models.Elderly).all()
    sent_count = 0
    
    menu_data = {
        "week_start": plan.week_start,
        "week_end": plan.week_end,
        "markdown_content": plan.markdown_content
    }
    
    for elderly in elderly_list:
        family_members = db.query(models.FamilyMember).filter(
            models.FamilyMember.elderly_id == elderly.id,
            models.FamilyMember.is_representative == True
        ).all()
        
        for member in family_members:
            if member.email:
                try:
                    email_content = openai_svc.generate_family_email_content(
                        menu_data, elderly.name
                    )
                    email_svc.send_menu_to_family(
                        member.email,
                        elderly.name,
                        menu_data,
                        email_content
                    )
                    sent_count += 1
                except Exception as e:
                    print(f"发送邮件给 {member.email} 失败: {str(e)}")
    
    plan.sent_to_families = True
    db.commit()
    
    print(f"菜单发送完成，共发送 {sent_count} 封邮件")

@router.post("/plans/{plan_id}/resend")
def resend_menu_to_family(plan_id: int, elderly_id: int, db: Session = Depends(get_db)):
    plan = db.query(models.MenuPlan).filter(models.MenuPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="菜单计划不存在")
    
    elderly = db.query(models.Elderly).filter(models.Elderly.id == elderly_id).first()
    if not elderly:
        raise HTTPException(status_code=404, detail="老人信息不存在")
    
    family_members = db.query(models.FamilyMember).filter(
        models.FamilyMember.elderly_id == elderly_id,
        models.FamilyMember.is_representative == True
    ).all()
    
    if not family_members:
        raise HTTPException(status_code=400, detail="该老人没有指定家属代表")
    
    openai_svc, email_svc = get_services()
    
    menu_data = {
        "week_start": plan.week_start,
        "week_end": plan.week_end,
        "markdown_content": plan.markdown_content
    }
    
    sent_count = 0
    for member in family_members:
        if member.email:
            try:
                email_content = openai_svc.generate_family_email_content(
                    menu_data, elderly.name
                )
                success = email_svc.send_menu_to_family(
                    member.email,
                    elderly.name,
                    menu_data,
                    email_content
                )
                if success:
                    sent_count += 1
            except Exception as e:
                print(f"发送邮件给 {member.email} 失败: {str(e)}")
    
    return {
        "success": sent_count > 0,
        "sent_count": sent_count,
        "message": f"已重新发送给 {sent_count} 位家属"
    }
