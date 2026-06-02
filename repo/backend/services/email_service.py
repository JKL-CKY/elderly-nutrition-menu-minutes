import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from dotenv import load_dotenv
from typing import List, Dict
import markdown

load_dotenv()

class EmailService:
    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", 587))
        self.smtp_user = os.getenv("SMTP_USER")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.from_email = os.getenv("FROM_EMAIL", self.smtp_user)

    def send_email(self, to_email: str, subject: str, body: str, cc: List[str] = None, attachments: List[Dict] = None) -> bool:
        try:
            msg = MIMEMultipart("alternative")
            msg["From"] = self.from_email
            msg["To"] = to_email
            msg["Subject"] = subject
            
            if cc:
                msg["Cc"] = ", ".join(cc)
            
            html_body = markdown.markdown(body)
            msg.attach(MIMEText(body, "plain", "utf-8"))
            msg.attach(MIMEText(html_body, "html", "utf-8"))
            
            if attachments:
                for att in attachments:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(att["content"])
                    encoders.encode_base64(part)
                    part.add_header(
                        "Content-Disposition",
                        f"attachment; filename= {att['filename']}",
                    )
                    msg.attach(part)
            
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                recipients = [to_email] + (cc if cc else [])
                server.sendmail(self.from_email, recipients, msg.as_string())
            
            return True
        except Exception as e:
            print(f"发送邮件失败: {str(e)}")
            return False

    def send_menu_to_family(self, family_email: str, elderly_name: str, menu_data: Dict, email_content: str) -> bool:
        week_start = menu_data["week_start"].strftime("%Y年%m月%d日")
        week_end = menu_data["week_end"].strftime("%Y年%m月%d日")
        
        subject = f"【养老院膳食通知】{elderly_name} 本周营养菜单 ({week_start} - {week_end})"
        
        full_body = f"{email_content}\n\n---\n\n## 本周菜单详情\n\n{menu_data['markdown_content']}"
        
        attachment = [{
            "filename": f"每周菜单_{week_start}_{week_end}.md",
            "content": menu_data['markdown_content'].encode("utf-8")
        }]
        
        return self.send_email(
            to_email=family_email,
            subject=subject,
            body=full_body,
            attachments=attachment
        )

    def send_meeting_minutes(self, recipients: List[str], meeting_title: str, minutes_content: str) -> bool:
        subject = f"【会议纪要】{meeting_title}"
        
        return self.send_email(
            to_email=recipients[0] if recipients else "",
            subject=subject,
            body=minutes_content,
            cc=recipients[1:] if len(recipients) > 1 else None
        )
