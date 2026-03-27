import asyncio
import random
import json
from playwright.async_api import async_playwright
from playwright_stealth import Stealth
from datetime import datetime

async def linkedin_daily_search(query_url, output_path):
    # Use a persistent directory to store "Guest" session data
    user_data_dir = "./user_data"
    
    async with Stealth().use_async(async_playwright()) as p:
        
        context = await p.chromium.launch_persistent_context(
            user_data_dir,
            headless=False,  # Headless=True is a major signal for the login wall
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={'width': 1920, 'height': 1080},
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                ]
        )
        
        page = context.pages[0] if context.pages else await context.new_page()
        
        # Step 1: Mimic a human landing from Google
        await page.goto("https://www.google.com", wait_until="domcontentloaded")
        await asyncio.sleep(random.uniform(2, 4))
    
        
        # Step 2: Go to LinkedIn homepage first
        await page.goto("https://www.linkedin.com/", wait_until="domcontentloaded", referer="https://www.google.com/")
        await asyncio.sleep(random.uniform(3, 5))
    
        # Step 3: Then go to the filtered jobs URL
        # NOTE: Add '&trk=guest_homepage-basic_guest_nav_menu_jobs' to your URL 
        # to trick LinkedIn into thinking you clicked the Nav bar.
        final_url = query_url + "&trk=guest_homepage-basic_guest_nav_menu_jobs"
    
        await page.goto(final_url, wait_until="domcontentloaded")
        await asyncio.sleep(random.uniform(2, 4))
    
        # Step 4: Try to close the login panel
        try:
            close_btn = await page.wait_for_selector(
            'button[aria-label="Ignorer"], '
            'button[aria-label="Dismiss"], '
            'button[aria-label="Fermer"], '
            'button.modal__dismiss, '
            'button.contextual-sign-in-modal__modal-dismiss-icon',
            timeout=3000
            )
            await close_btn.click()
            await asyncio.sleep(1)
        except:
            print("No need / unable to close the login panel")
    
        # Step 5: Scroll the job list pane specifically
        print("scrolling")
        for i in range(5):  # Scroll 5 times
            await page.mouse.wheel(0, 1000)
            await asyncio.sleep(random.uniform(1, 5))
    
        
        # Step6: Extract job cards
        print("starting retrieving the job content")
        jobs = await page.evaluate(r'''() => {
            const cards = document.querySelectorAll('ul.jobs-search__results-list li');
            return Array.from(cards).map(card => {
                const rawLink = card.querySelector('a.base-card__full-link')?.href ?? '';
                const match = rawLink.match(/(\d{8,})/);
                const jobId = match ? match[1] : null;
                return {
                    title: card.querySelector('.base-search-card__title')?.innerText?.trim(),
                    company: card.querySelector('.base-search-card__subtitle')?.innerText?.trim(),
                    location: card.querySelector('.job-search-card__location')?.innerText?.trim(),
                    date: card.querySelector('time')?.getAttribute('datetime'),
                    job_id: jobId,
                    url: jobId ? `https://www.linkedin.com/jobs/view/${jobId}/` : rawLink,
                };
            }).filter(j => j.job_id);
        }''')
    
        print(f"{len(jobs)} jobs found")
    
        # Step7: Click each card and grab description from side panel
        for job in jobs:
            try:
                await page.click(f'a[href*="{job["job_id"]}"]')
                await asyncio.sleep(random.uniform(3, 6))
    
                description = await page.evaluate('''() => {
                    const el = document.querySelector('.description__text')
                            ?? document.querySelector('.show-more-less-html__markup');
                    return el ? el.innerText.trim() : null;
                }''')
    
                job['description'] = description
                print(f"✓ {job['title']} @ {job['company']}")
    
            except Exception as e:
                job['description'] = None
                print(f"✗ Failed for {job['job_id']}: {e}")
    
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(jobs, f, ensure_ascii=False, indent=2)
    
        print(f"Saved {len(jobs)} jobs to {output_path}")
    
        await context.close()
        return(jobs)

if __name__ == "__main__":

    date_str = datetime.today().strftime("%Y-%m-%d")

    query_url_dict = {"data_scientist":"https://www.linkedin.com/jobs/search/?f_E=3%2C4%2C5%2C6&f_TPR=r86400&keywords=%22data%20scientist%22&location=France&origin=JOB_SEARCH_PAGE_JOB_FILTER&sortBy=DD&spellCorrectionEnabled=true",
    "ai_engineer":"https://www.linkedin.com/jobs/search/?f_E=3%2C4%2C5%2C6&f_TPR=r86400&keywords=%22ai%20engineer%22&location=France&origin=JOB_SEARCH_PAGE_JOB_FILTER&sortBy=DD&spellCorrectionEnabled=true"}
    
    for job_title, url in query_url_dict.items():
        
        output_path = f"data/daily_scrap/linkedin_{job_title}_{date_str}.json"
        asyncio.run(linkedin_daily_search(url, output_path))