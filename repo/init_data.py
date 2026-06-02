from backend.database import SessionLocal
from backend import models
from datetime import datetime, timedelta

def init_sample_data():
    db = SessionLocal()
    
    try:
        elderly_list = [
            {
                "name": "张爷爷",
                "age": 78,
                "gender": "男",
                "room_number": "101",
                "medical_history": "高血压、糖尿病",
                "dietary_restrictions": "低糖、低盐",
                "allergies": "无",
                "food_texture": "软食",
                "weight": 65,
                "height": 170,
                "bmi": 22.5,
                "activity_level": "轻度活动"
            },
            {
                "name": "李奶奶",
                "age": 82,
                "gender": "女",
                "room_number": "102",
                "medical_history": "心脏病、高血脂",
                "dietary_restrictions": "低脂肪、低胆固醇",
                "allergies": "海鲜过敏",
                "food_texture": "普食",
                "weight": 55,
                "height": 158,
                "bmi": 22.0,
                "activity_level": "中度活动"
            },
            {
                "name": "王爷爷",
                "age": 75,
                "gender": "男",
                "room_number": "103",
                "medical_history": "无",
                "dietary_restrictions": "无",
                "allergies": "花生过敏",
                "food_texture": "普食",
                "weight": 72,
                "height": 175,
                "bmi": 23.5,
                "activity_level": "中度活动"
            },
            {
                "name": "赵奶奶",
                "age": 85,
                "gender": "女",
                "room_number": "104",
                "medical_history": "老年痴呆、吞咽困难",
                "dietary_restrictions": "无",
                "allergies": "无",
                "food_texture": "半流食",
                "weight": 48,
                "height": 152,
                "bmi": 20.8,
                "activity_level": "卧床"
            }
        ]
        
        for e_data in elderly_list:
            elderly = models.Elderly(**e_data)
            db.add(elderly)
            db.flush()
            
            health_record = models.HealthRecord(
                elderly_id=elderly.id,
                blood_pressure="130/85" if "高血压" not in e_data["medical_history"] else "150/95",
                blood_sugar=5.5 if "糖尿病" not in e_data["medical_history"] else 8.2,
                cholesterol=4.8 if "高血脂" not in e_data["medical_history"] else 6.5,
                heart_disease="心脏病" in e_data["medical_history"],
                diabetes="糖尿病" in e_data["medical_history"],
                kidney_disease=False,
                notes="例行检查"
            )
            db.add(health_record)
            
            family = models.FamilyMember(
                elderly_id=elderly.id,
                name=f"{e_data['name'][0]}先生/女士",
                relationship="子女",
                email=f"family_{elderly.id}@example.com",
                phone=f"1380000000{elderly.id}",
                is_representative=True
            )
            db.add(family)
        
        meeting = models.MeetingRecording(
            title="5月第三周膳食营养讨论会",
            meeting_date=datetime.now(),
            processed=False
        )
        db.add(meeting)
        
        db.commit()
        print("示例数据初始化完成！")
        
    except Exception as e:
        db.rollback()
        print(f"初始化失败: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    init_sample_data()
