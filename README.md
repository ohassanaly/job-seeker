This repo aims at daily scrapping the job offers matching given defined criteria</br>

# Project Description
So far, we focused on [Welcome to the Jungle](https://www.welcometothejungle.com/fr)</br>
- wttj.py allows scrapping all the job offers in the latest x hours appearing in the first result page following the filters provided in the URL
- linkedin.py allows scrapping all the job offers in the latest 24 hours appearing in the first result page following the filters provided in the URL
- report_summary.py generates a quick report of each offer found and sends an email
- cover_letter.py generates dedicated cover letters based on a template to fit with the job offer
- wttj, report_summary and cover_letter are combined into main.py 
</br>

# Usage
- clone this repo
- uv sync
- for cover_letter and generate_report usage : add your .env file with openai and sendgrid API keys
- for generate_report usage : add a src/secrets.py file with your email adress informations
- cd src
- uv run main.py

# Notes :
- currently, we are mainly running wttj.py and linkedin.py independently ; this allows
a first level of selection so I do not generate cover letters for irrelevant offers
- the routine can be automatically triggered using a cron job : </br>
''' crontab -e '''
''' 00 18 * * * cd /home/ohassanaly/work/job-reports/src && /home/ohassanaly/.local/bin/uv run main.py >> ../logs/scraper.log 2>&1 '''

# Later goals : 
- Update the src/main.py to include all functionnalities and situations
- add other platforms : [HelloWork](https://www.hellowork.com/fr-fr/) ; [Choisir le Service Public](https://choisirleservicepublic.gouv.fr/)
- Improve the cover letter generation ; add an LLMs as a judge to validate the generated results
- Structure the data extracted from the different platforms
- Add a dedicated CV generation
- Improve the daily report generation (context length considerations)