import os
import json
from openai import OpenAI
from datetime import datetime

import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content
from sendgrid import SendGridAPIClient
from secrets import send_email, target_email

def generate_report(jobs: list[dict], client) -> str:
    
    jobs_text = json.dumps(jobs, ensure_ascii=False, indent=2)
    
    response = client.chat.completions.create(
        model="gpt-4.1-mini", #1M tokens context window
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a concise job report writer. "
                    "For each job, write: the job title, company name, "
                    "a 2-sentence summary of the role, and the URL. "
                    "Separate each job with a blank line. Plain text only, no markdown."
                )
            },
            {
                "role": "user",
                "content": f"Generate a brief report for these job offers:\n{jobs_text}"
            }
        ],
        temperature=0.3,
    )
    
    return response.choices[0].message.content.strip()

def send_email(summary:str, sg_client:SendGridAPIClient , sender:str=send_email, target:str=target_email):

    date_str = datetime.today().strftime("%Y-%m-%d")
    subject = f"Job updates : {date_str}"
    
    from_email = Email(sender)
    to_email = To(target)
    mail = Mail(from_email, to_email, subject, summary)
    response = sg_client.send(mail)
    print(f"Email sent — status {response.status_code}")
    return

if __name__ == "__main__":
    
    from dotenv import load_dotenv
    load_dotenv()
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    with open("data/test/jobs_2026-03-24.json", "r") as f:
        jobs = json.load(f)
        
    summary = generate_report(jobs, client)
    
    sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
    
    send_email(summary, sg)