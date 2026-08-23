def talents4good():
    # import libraries
    import os
    import pickle
    import requests
    from bs4 import BeautifulSoup

    company_name = "talents4good"
    FILE_PATH = os.path.abspath(os.path.dirname(__file__))


    """
    PARSE AND SCRAPE WEBPAGES FOR CURRENT JOB POSTINGS
    """
    # get and parse webpage
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"}
    urls = [
        "https://jobs.talents4good.org/jobs?location=Berlin", 
        "https://jobs.talents4good.org/jobs?remote=1",
    ]

    # loop through pages, extract all job postings, and store in dict
    current_jobs_dict = {}
    n_jobs_found = 0

    for url in urls:
        r = requests.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")

        job_listings = soup.find_all("div", class_="job-details")
        n_jobs_found += len(job_listings)

        for job_listing in job_listings:
            link = "https://jobs.talents4good.org" + job_listing.find("a")["href"]
            title = job_listing.find("a").text.strip()
            details_all = job_listing.find_all("div")[1].text.split("\n\n")[1:]
            details_all = [t.strip().split("\n")[0] for t in details_all]
            company = details_all[0]
            location = details_all[2]
            date_posted = details_all[3]
            job_details = details_all[1]

            current_jobs_dict.update({link: {"title": title,
                                            "company": company,
                                            "location": location,
                                            "date_posted": date_posted,
                                            "details": job_details,
                                            "link": link}})


    """
    LOAD RESULTS OF LAST EXECUTION - STORE CURRENT RESULTS
    """
    # open last saved job postings (create empty dict if nonexistent)
    try:
        with open(f'{FILE_PATH}/{company_name}_current_jobs_dict.pkl', 'rb') as f:
            saved_jobs_dict = pickle.load(f)
    except FileNotFoundError:
        saved_jobs_dict = {} 

    # store current state of job postings for next execution
    with open(f'{FILE_PATH}/{company_name}_current_jobs_dict.pkl', 'wb') as f:
        pickle.dump(current_jobs_dict, f)


    """
    FILTER JOBS AND RETURN RESULTS AS DICTIONARY
    """
    # create list containing only ids of new jobs
    new_jobs = {job: current_jobs_dict[job] for job in current_jobs_dict if job not in saved_jobs_dict}
    # create written summary
    summary = f"{n_jobs_found} jobs found, {len(current_jobs_dict)} unique scraped, {len(new_jobs)} new jobs."

    # return touple of summary and dict with new job postings if any, otherwise return None
    return (summary, new_jobs)
