import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os

load_dotenv()

EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

def send_reminder_email(to_email, task_title, due_date):
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"⏰ Task Reminder: {task_title}"
        msg["From"] = EMAIL_SENDER
        msg["To"] = to_email

        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; background: #f4f4f4; padding: 20px;">
            <div style="max-width: 500px; margin: auto; background: white; border-radius: 12px; padding: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <div style="text-align: center; margin-bottom: 20px;">
                    <h1 style="color: #16a34a;">📝 Task Tracker</h1>
                    <p style="color: #666;">Student Productivity Dashboard</p>
                </div>
                <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
                <h2 style="color: #333;">⏰ Task Due Tomorrow!</h2>
                <div style="background: #f0fdf4; border-left: 4px solid #16a34a; padding: 15px; border-radius: 8px; margin: 20px 0;">
                    <p style="margin: 0; color: #333;"><strong>Task:</strong> {task_title}</p>
                    <p style="margin: 8px 0 0 0; color: #666;"><strong>Due Date:</strong> {due_date}</p>
                </div>
                <p style="color: #666;">Please make sure to complete your task on time!</p>
                <div style="text-align: center; margin-top: 25px;">
                    <a href="http://localhost:3000" 
                       style="background: #16a34a; color: white; padding: 12px 25px; border-radius: 8px; text-decoration: none; font-weight: bold;">
                        Open Task Tracker
                    </a>
                </div>
                <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
                <p style="color: #999; font-size: 12px; text-align: center;">© 2026 Task Tracker • Student Edition</p>
            </div>
        </body>
        </html>
        """

        msg.attach(MIMEText(html, "html"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, to_email, msg.as_string())

        print(f"✅ Reminder sent to {to_email} for task: {task_title}")
        return True

    except Exception as e:
        print(f"❌ Email error: {e}")
        return False