def goodjobs_eu():
    # import libraries
    import os
    import pickle
    import requests
    from bs4 import BeautifulSoup

    company_name = "goodjobs_eu"
    FILE_PATH = os.path.abspath(os.path.dirname(__file__))


    """
    PARSE AND SCRAPE WEBPAGES FOR CURRENT JOB POSTINGS
    """
    # get and parse webpage
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"}
    base_url = "https://goodjobs.eu/jobs?places=Berlin&distance=10&places_type=city&countrycode=DE&latlng=52.510885%2C13.3989367&job_search=1&sort_by_newest=true&num=100"
    r = requests.get(base_url, headers=headers)
    soup = BeautifulSoup(r.text, 'html.parser')
    
    n_pages = 2 # hard-coded for now, see if number of jobs passes 200 in the future...
    
    # loop through pages, extract all job postings, and store in dict
    current_jobs_dict = {}
    n_jobs_found = 0

    for page in range(1, n_pages+1):
        url = f"{base_url}&page={page}"
        r = requests.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        
        jobcards = soup.find_all("a", class_="jobcard")
        n_jobs_found += len(jobcards)

        for jobcard in jobcards:
            job_url = jobcard["href"]
            title = jobcard.find("h2").text.strip()
            company = jobcard \
                .find("div") \
                .find("div") \
                .find_all("div", recursive=False)[1] \
                .find("span") \
                .text.strip()

            is_powered_by_academics = False
            if jobcard.find("p"):
                is_powered_by_academics = jobcard.find("p").text.strip() == "Powered by academics"

            if not is_powered_by_academics:
                job_details = jobcard \
                .find("div") \
                .find("div") \
                .find_all("div", recursive=False)[2] \
                .find_all("div", recursive=False)

                location_remote_raw = job_details[0].find_all("div", recursive=False)[0].text.strip()
                location_remote_parts = [part.strip() for part in location_remote_raw.split("|")]
                if len(location_remote_parts) == 2:
                    location, remote = location_remote_parts
                else:
                    location = location_remote_parts[0]
                    remote = None
                date_posted = job_details[-1].find("span").text.strip()
                job_dict_id = job_url

            if is_powered_by_academics:
                job_details = jobcard \
                .find("div") \
                .find("div") \
                .find_all("div", recursive=False)[2] \
                .find_all("span")

                location = job_details[0].text.strip()
                remote = None
                date_posted = "N/A"
                job_dict_id = company + ' | ' + title
                
            current_jobs_dict.update(
                {job_dict_id: {
                    "title": title,
                    "company": company,
                    "location": location,
                    "date_posted": date_posted,
                    "details": remote,
                    "link": job_url
                    }
                }
            )

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
    summary = f"{n_jobs_found} jobs found, {len(current_jobs_dict)} scraped, {len(new_jobs)} new jobs."

    # return touple of summary and dict with new job postings if any, otherwise return None
    return (summary, new_jobs)