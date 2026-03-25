import os
import asyncio
from wttj import parse_published_to_hours, retrieve_job_details, daily_search
from cover_letter import tailor_letter, write_docx
from report_summary import generate_report, send_email
from tqdm import tqdm
from openai import OpenAI
from sendgrid import SendGridAPIClient


def main(query_url:str, cover_letters_path:str, cover_template:str, system_prompt:str, llm_client:OpenAI, sg_client:SendGridAPIClient):
    #retrieving fresh job offers
    jobs = asyncio.run(daily_search(query_url))
    
    try :
        os.mkdir(cover_letters_path)
    except :
        print(f"{cover_letters_path} already exists")

    #mail report 
    print("Starting mail reporting")
    send_email(generate_report(jobs, llm_client), sg_client)
    
    #writing cover letters
    print("Starting cover letters writing")
    try:
        for job in tqdm(jobs):
            job_text = "\n".join([job[section] for section in ["Descriptif du poste", "Profil recherché"] if section in job])
            cover_letter = tailor_letter(cover_template, job_text, SYSTEM_PROMPT, llm_client)
            write_docx(cover_letter, f"{cover_letters_path}{"_".join(job["url"].split("/")[5:])+ ".docx"}")
    except:
        print("error in cover letters writing")

    return

if __name__ == "__main__":

    from datetime import datetime
    from dotenv import load_dotenv
    import sendgrid

    query_url_list=[
    "https://www.welcometothejungle.com/fr/jobs?refinementList%5Boffices.country_code%5D%5B%5D=FR&refinementList%5Bcontract_type%5D%5B%5D=full_time&query=%22data%20scientist%22&sortBy=mostRecent&page=1",
    "https://www.welcometothejungle.com/fr/jobs?refinementList%5Boffices.country_code%5D%5B%5D=FR&refinementList%5Bcontract_type%5D%5B%5D=full_time&query=%22ai%20engineer%22&page=1&sortBy=mostRecent",
    ]
    date_str = datetime.today().strftime("%Y-%m-%d")
    cover_letters_path = f"data/cover_letters/cover_letters_{date_str}/"
    
    load_dotenv()

    llm_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    sg_client = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))

    with open("data/resources/cover_template.txt") as f:
      cover_template = f.read()
    
    with open("data/resources/SYSTEM_PROMPT.txt") as f:
      SYSTEM_PROMPT = f.read()

    main(query_url_list, cover_letters_path, cover_template, SYSTEM_PROMPT, llm_client, sg_client)

    





