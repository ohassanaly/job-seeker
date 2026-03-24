import os
import asyncio
from wttj import parse_published_to_hours, retrieve_job_details, daily_search
from cover_letter import tailor_letter, write_docx
from tqdm import tqdm
from openai import OpenAI


def main(query_url:str, cover_letters_path:str, cover_template:str, system_prompt:str, client:OpenAI):
    #retrieving fresh job offers
    jobs = asyncio.run(daily_search(query_url))
    
    try :
        os.mkdir(cover_letters_path)
    except :
        print(f"{cover_letters_path} already exists")

    #writing cover letters
    for job in tqdm(jobs):
        job_text = "\n".join([job[section] for section in ["Descriptif du poste", "Profil recherché"] if section in job])
        cover_letter = tailor_letter(cover_template, job_text, SYSTEM_PROMPT, client)
        write_docx(cover_letter, f"{cover_letters_path}{"_".join(job["url"].split("/")[5:])+ ".docx"}")

if __name__ == "__main__":

    from datetime import datetime
    from dotenv import load_dotenv

    query_url="https://www.welcometothejungle.com/fr/jobs?refinementList%5Boffices.country_code%5D%5B%5D=FR&refinementList%5Bcontract_type%5D%5B%5D=full_time&query=%22data%20scientist%22&sortBy=mostRecent&page=1"
    date_str = datetime.today().strftime("%Y-%m-%d")
    cover_letters_path = f"data/cover_letters_{date_str}/"
    
    load_dotenv()

    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    with open("data/cover_template.txt") as f:
      cover_template = f.read()
    
    with open("data/SYSTEM_PROMPT.txt") as f:
      SYSTEM_PROMPT = f.read()

    main(query_url, cover_letters_path, cover_template, SYSTEM_PROMPT, client)

    





