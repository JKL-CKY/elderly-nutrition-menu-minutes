import os
from openai import OpenAI
from dotenv import load_dotenv
from typing import Dict, List
import json
from datetime import datetime, timedelta

load_dotenv()

class OpenAIService:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def generate_meeting_summary(self, transcription_with_roles: List[Dict], nutrition_requirements: Dict) -> str:
        conversation_text = "\n".join([
            f"[{item['role']}] {item['text']}"
            for item in transcription_with_roles
        ])
        
        prompt = f"""请作为养老院膳食营养师，总结以下膳食营养会议内容，并提取关键信息：

会议对话记录：
{conversation_text}

已提取的营养需求信息：
{json.dumps(nutrition_requirements, ensure_ascii=False, indent=2)}

请提供：
1. 会议要点总结（300字以内）
2. 老人饮食禁忌汇总
3. 食物质地要求
4. 营养师特别建议
5. 厨师长反馈与调整意见"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "你是一位专业的养老院营养师，擅长制定健康膳食方案。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=1500
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"生成摘要时出错: {str(e)}"

    def generate_weekly_menu(self, elderly_profiles: List[Dict], meeting_summary: str, week_start: datetime = None) -> Dict:
        if week_start is None:
            week_start = datetime.now()
            week_start = week_start - timedelta(days=week_start.weekday())
        
        week_end = week_start + timedelta(days=6)
        
        elderly_summary = "\n".join([
            f"- {e['name']}({e['age']}岁): {e.get('dietary_restrictions', '无特殊禁忌')}, "
            f"质地要求: {e.get('food_texture', '普食')}, "
            f"病史: {e.get('medical_history', '无')}"
            for e in elderly_profiles
        ])
        
        prompt = f"""请为养老院制定下周（{week_start.strftime('%Y年%m月%d日')} 至 {week_end.strftime('%Y年%m月%d日')}）的营养菜单。

在院老人基本情况：
{elderly_summary}

本次会议讨论要点：
{meeting_summary}

请生成包含以下内容的每周菜单：
1. 每日三餐（早餐、午餐、晚餐）+ 加餐
2. 每餐包含：主菜、副菜、主食、汤品
3. 考虑以下因素：
   - 低盐（每日盐摄入≤5g）
   - 低油（每日油脂摄入≤25g）
   - 高蛋白（每日蛋白质1.0-1.2g/kg体重）
   - 高纤维（每日膳食纤维≥25g）
   - 充足的钙和维生素D
   - 考虑不同质地需求（普食、软食、半流食、流食）
4. 每周轮换菜品，避免重复
5. 提供营养评定表（热量、蛋白质、脂肪、碳水、钠、钙、膳食纤维）

请以Markdown格式输出，包含评定表。"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "你是一位资深养老院营养师，擅长制定科学、美味、适合老年人的营养菜单。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6,
                max_tokens=4000
            )
            
            markdown_content = response.choices[0].message.content
            assessment_form = self._extract_assessment_form(markdown_content)
            
            return {
                "week_start": week_start,
                "week_end": week_end,
                "markdown_content": markdown_content,
                "assessment_form": assessment_form
            }
        except Exception as e:
            return {
                "error": str(e),
                "week_start": week_start,
                "week_end": week_end,
                "markdown_content": f"生成菜单时出错: {str(e)}",
                "assessment_form": ""
            }

    def _extract_assessment_form(self, markdown_content: str) -> str:
        lines = markdown_content.split("\n")
        in_table = False
        table_content = []
        
        for line in lines:
            if "评定" in line or "评估" in line or "营养" in line and "表" in line:
                in_table = True
            if in_table:
                table_content.append(line)
                if line.strip() == "" and len(table_content) > 3:
                    break
        
        return "\n".join(table_content) if table_content else ""

    def generate_family_email_content(self, menu_data: Dict, elderly_name: str = "各位老人") -> str:
        prompt = f"""请基于以下每周菜单内容，为家属代表撰写一封温馨的邮件：

菜单信息：
周次: {menu_data['week_start'].strftime('%Y年%m月%d日')} - {menu_data['week_end'].strftime('%Y年%m月%d日')}

菜单详情：
{menu_data['markdown_content'][:2000]}

请撰写：
1. 亲切的问候
2. 说明本周膳食安排的营养考量
3. 提及特别关注的老人饮食需求
4. 邀请家属反馈
5. 结尾祝福

请保持温暖、专业的语气，字数控制在300-500字。"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "你是养老院的营养师，善于与家属沟通，让家属放心。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=800
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"生成邮件内容时出错: {str(e)}"
