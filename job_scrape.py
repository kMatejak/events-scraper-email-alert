def main():
    # import libraries
    import os
    import smtplib
    from dotenv import load_dotenv
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from utils import add_sorting_keys
    # import scraping modules
    from websites.goodjobs_eu.goodjobs_eu_scrape import goodjobs_eu
    from websites.talents4good.talents4good_scrape import talents4good
    # from websites.waw-districts.ochota.ochota_scrape import ochota


    # Specify which sites to scrape and the corresponding company/platform name
    company_funcs = {
        'Goodjobs EU': goodjobs_eu,
        'Talents4Good': talents4good,
        # 'Ochota': ochota
        }

    # Define key words for relevant (pos) and irrelevant (neg) flagging
    pos_search_terms = ["data", "analyst", "analysis", "analytics", "machine learning",
                        "daten", "analyse", "auswertung", "analytiker", "statistik",
                        "marktforschung", "markt", "forschung", "market", "research", 
                        " ki ", " ai ", " ml "]
    neg_search_terms = ["trainee", "student", "studium", "studierend", "praktikum", 
                        "praktikant", "ausbildung"]

    # initialize empty objects to store scraping results and email text in
    ls_text_body = []
    ls_html_body = []
    n_new_jobs_total = 0
    error_messages = ''


    # ---------------------------------------------------------------- #
    # POPULATE EMAIL BODY TEXTS WITH RESULTS OF SCRAPER MODULES ------ #
    # ---------------------------------------------------------------- #

    # Call scraping function of each website (return dictionary)
    for website_name, website_func in company_funcs.items():
        # Make scraping function call
        try:
            summary, new_company_jobs = website_func()
            print(f'{website_name}: {summary}')
        except Exception as e:
            error_messages += f'Error while scraping {website_name}:\n{e}\n\n'
            print(f'{website_name}: ERROR ({e})')
            continue

        # skip if there are no new jobs
        n_new_company_jobs = len(new_company_jobs)
        if n_new_company_jobs == 0:
            continue

        # add sorting and color coding by relevance (acc. to search terms defined above)
        new_company_jobs = add_sorting_keys(new_company_jobs, pos_search_terms, neg_search_terms)
        # sort dictionairy based on relevance (desc) and job title
        new_company_jobs_sorted = dict(sorted(new_company_jobs.items(),
                                              key=lambda x: (-x[1]['relevance'], x[1]['title'])))

        # initialize email text sections per company scraped
        text_body_comp = f'{n_new_company_jobs} new jobs at {website_name}:\n{summary}\n\n'
        html_body_comp = (f'<big><b>{n_new_company_jobs} new jobs at {website_name}:</b></big> <br>'
                          f'<small><i>{summary}</i></small> <br><br>')

        # add information for each job to company text section
        for job_details in new_company_jobs_sorted.values():
            link = job_details['link']
            title = job_details['title']
            company = job_details['company']
            location = job_details['location']
            date = job_details['date_posted']
            details = job_details['details'] if 'details' in job_details else None
            font_style = job_details['font_style']

            # Add job info to mail bodies
            text_body_comp += (f'Title: {title}:\nLink: {link}\nLocation: {location}')
            html_body_comp += (f'<a href="{link}" {font_style}><b>{title}</b></a>'
                               f'<br>Company: {company}'
                               f'<br>Location(s): {location}'
                               f'<br>Posted/Deadline: {date}')
            
            # Add element "details" to bodies if existent
            text_body_comp += f'\nDetails: {details}\n\n' if details else '\n\n'
            html_body_comp += f'<br>Details: {details}<br><br>' if details else '<br><br>'
        
        ls_text_body.append(text_body_comp)
        ls_html_body.append(html_body_comp)
        
        n_new_jobs_total += n_new_company_jobs
        
    # Create final body messages by joining individual company body texts
    text_body = '<br><hr><br>'.join(ls_text_body)
    html_body = '<br><hr><br>'.join(ls_html_body)

    # Add captured error messages to end of texts
    if error_messages:
        text_body += f'<br><hr><br>{error_messages}'
        html_body += f'<br><hr><br>{error_messages}'


    # ---------------------------------------------------------------- #
    # SET UP CONNECTION AND SEND EMAIL ------------------------------- #
    # ---------------------------------------------------------------- #

    # Send job alert per mail if new jobs were found (i.e. if bodies are not empty)
    if n_new_jobs_total == 0:
        print("No new jobs.")
        return
    
    # include mail account credentials from environment variables
    load_dotenv()
    EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')
    EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
    EMAIL_TO = os.getenv('EMAIL_TO')
    
    # set up email message
    msg = MIMEMultipart('alternative')
    msg['Subject'] = f'JOB ALERT ({n_new_jobs_total} new)'
    msg['From'] = EMAIL_ADDRESS # type: ignore
    msg['To'] = EMAIL_TO # type: ignore
    msg.attach(MIMEText(text_body, 'plain'))
    msg.attach(MIMEText(html_body, 'html'))

    # send email
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD) # type: ignore
        server.sendmail(EMAIL_ADDRESS, EMAIL_TO, msg.as_string()) # type: ignore

    print("New posts, email notification sent!")


if __name__ == '__main__':
    main()