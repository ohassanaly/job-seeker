This repo aims at daily scrapping the job offers matching given defined criteria</br>

# Project Description
So far, we focused on [Welcome to the Jungle](https://www.welcometothejungle.com/fr)</br>
- wttj.py allows scrapping all the job offers in the latest 2 days appearing in the first result page following the filters in the provided URL
- report_summary.py generates a quick report of each offer found and sends an email
- cover_letter.py generates dedicated cover letters based on a template to fit with the job offer
- all those recipes are combined into main.py 
</br>

# Usage
clone this repo
uv sync
add your .env file with openai and sendgrid API keys
add a src/secrets.py file with your email adress informations
cd src
uv run main.py

# Later goals : 
- automate the daily script running (src/main.py using cron/GHActions/Airflow)
- add other platforms : [Linkedin](https://www.linkedin.com/) ; [Choisir le Service Public](https://choisirleservicepublic.gouv.fr/)
- extend the routine : based on job description, improve the cover letter generation ; add also a dedicated CV generation
- Improve the daily report generation