
"""
Scrape Welcome to the Jungle 

for "data scientist" keyword
CDI jobs
posted in the last 2 days

criteria are editable in the query_url
"""

import re
import json
import httpx
import asyncio
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from datetime import datetime
from dict import exclude_keywords

def parse_published_to_hours(text: str) -> int | None:
    import re
    match = re.search(
        r"(il y a (\d+) (heures?|jours?|mois)|hier|aujourd'hui)",
        text,
        re.IGNORECASE
    )
    if not match:
        return None

    raw = match.group(0).lower()

    if "aujourd'hui" in raw:
        return 0
    if "hier" in raw:
        return 24

    number = int(match.group(2))
    unit = match.group(3)

    if "heure" in unit:
        return number
    if "jour" in unit:
        return number * 24
    if "mois" in unit:
        return number * 30 * 24

    return None
    
def retrieve_job_details(url:str)-> dict:
    r = httpx.get(url, headers={"Accept-Language": "fr-FR"})
    soup = BeautifulSoup(r.text, "html.parser")

    text = soup.get_text(" ", strip=True)

    published = parse_published_to_hours(text)

    sections = {}
    for h4 in soup.find_all("h4"):
        title = h4.get_text(strip=True)
        if title in ["Descriptif du poste", "Profil recherché"]:
            # Collect all sibling text until the next heading
            content_parts = []
            for sibling in h4.find_next_siblings():
                if sibling.name in ["h3", "h4"]:
                    break
                content_parts.append(sibling.get_text(" ", strip=True))
            sections[title] = "\n".join(content_parts)

    result = {"published": published, **sections}
    return(result)

def filter_consultancies(title: str, details: dict, exclude_keywords:list) -> bool:
    
    searchable = " ".join([
        title,
        details.get("Descriptif du poste", ""),
        details.get("Profil recherché", "")
    ]).lower()
    
    return not any(keyword in searchable for keyword in exclude_keywords)

async def daily_search(query_url_list:list[str]):
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        all_jobs = {}

        for query_url in query_url_list:
            print(f"Loading page: {query_url}")
            await page.goto(query_url, wait_until="networkidle", timeout=60_000)

            # Dismiss cookie banner if present
            try:
                await page.click("button[id*='accept'], button[id*='cookie'], button[data-testid*='cookie']", timeout=5_000)
                print("Cookie banner dismissed")
                await page.wait_for_timeout(2_000)  # let the page settle
            except:
                print("No cookie banner found")

            #Retrieve jobs and details
            await page.wait_for_selector("a[role='link'][href*='/jobs/']", timeout=30_000)
            job_links = await page.query_selector_all("a[role='link'][href*='/jobs/']")
        
            print("starting jobs scrapping")
        
            #will iterate on 62 job offers maximum (page size)
            for link in job_links:

                title = (await link.inner_text()).strip()
                href = await link.get_attribute("href")
                job_url = f"https://www.welcometothejungle.com{href}"
                #html scrapping based on the job offer URL
                details = retrieve_job_details(job_url)

                #only retrieve the fresh job offers and filter out consulting jobs
                if details["published"] <= 48 and filter_consultancies(title, details, exclude_keywords):
                    all_jobs[job_url] = {
                        "title": title,
                        "url": job_url,
                        **details
                    }
        await browser.close()
        
    date_str = datetime.today().strftime("%Y-%m-%d")
    write_path = f"data/daily_scrap/jobs_{date_str}.json"

    #remove duplicates (same job link rendered multiple times in the DOM)
    jobs = list(all_jobs.values())

    with open(write_path, "w", encoding="utf-8") as f:
        json.dump(jobs, f, ensure_ascii=False, indent=2)
    
    print(f"Saved {len(jobs)} jobs published in the latest 48 hours at {write_path}")
    return(jobs)


if __name__ == "__main__":
    query_url_list=[
    "https://www.welcometothejungle.com/fr/jobs?refinementList%5Boffices.country_code%5D%5B%5D=FR&refinementList%5Bcontract_type%5D%5B%5D=full_time&query=%22data%20scientist%22&sortBy=mostRecent&page=1",
    "https://www.welcometothejungle.com/fr/jobs?refinementList%5Boffices.country_code%5D%5B%5D=FR&refinementList%5Bcontract_type%5D%5B%5D=full_time&query=%22ai%20engineer%22&page=1&sortBy=mostRecent",
    ]
    asyncio.run(daily_search(query_url_list))
