def main():
    import os
    import smtplib
    # from dotenv import load_dotenv
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from utils import add_sorting_keys

    from websites.waw_districts.ochota.ochota_scrape import ochota


    # Specify which sites to scrape and the corresponding company/platform name
    district_funcs = {
        'Ochota': ochota
        }

    # Define key words for relevant (pos) and irrelevant (neg) flagging
    pos_search_terms = ["sesja", "rady", "dzielnicy"]
    neg_search_terms = []

    # initialize empty objects to store scraping results and email text in
    ls_text_body = []
    ls_html_body = []
    n_new_posts_total = 0
    error_messages = ''


    # ---------------------------------------------------------------- #
    # POPULATE EMAIL BODY TEXTS WITH RESULTS OF SCRAPER MODULES ------ #
    # ---------------------------------------------------------------- #

    # Call scraping function of each website (return dictionary)
    for website_name, website_func in district_funcs.items():
        # Make scraping function call
        try:
            summary, new_district_posts = website_func()
            # print(f'{website_name}: {summary}')
        except Exception as e:
            error_messages += f'Błąd podczas scrapingu {website_name}:\n{e}\n\n'
            print(f'{website_name}: ERROR ({e})')
            continue

        # skip if there are no new jobs
        n_new_district_posts = len(new_district_posts)
        if n_new_district_posts == 0:
            continue

        # add sorting and color coding by relevance (acc. to search terms defined above)
        new_district_posts = add_sorting_keys(new_district_posts, pos_search_terms, neg_search_terms)
        
        # sort dictionairy based on relevance (desc) and post title
        # new_district_post_sorted = dict(sorted(new_district_posts.items(),
        #                                       key=lambda x: (-x[1]['relevance'], x[1]['title'])))

        # filter dictionary based on relevance (only if contains pos_search_terms)
        new_district_post_filtered = dict(filter(lambda x: x[1]['relevance'] == 1, new_district_posts.items()))

        # initialize email text sections per company scraped
        text_body_comp = (f'**NADCIĄGA Sesja Rady Dzielnicy {website_name}**\nHej, tu twój Boromeusz! Mam wieści!\n'
                          f'Właśnie się ukazało:\n\n')
        html_body_comp = (f'<big><b>NADCIĄGA Sesja Rady Dzielnicy {website_name}</b></big> <br>'
                          f'<small>Hej, tu twój Boromeusz! Mam wieści!<br>Właśnie się ukazało:</small> <br><br>')

        # add information for each job to company text section
        for post_details in new_district_post_filtered.values():
            link = post_details['link']
            title = post_details['title']
            date_posted = post_details['date_posted']
            details = post_details['details'] if 'details' in post_details else None
            font_style = post_details['font_style']

            # Add job info to mail bodies
            text_body_comp += (f'{title}\n'
                               f'{date_posted} (data publ.)\n'
                               f'{link}')
            html_body_comp += (f'<a href="{link}" {font_style}><b>{title}</b></a>'
                               f'<br>{date_posted} (data publ.)')
            
            # Add element "details" to bodies if existent
            text_body_comp += f'\nOpis: {details}\n\n' if details else '\n\n'
            html_body_comp += f'<br>Opis: {details}<br><br>' if details else '<br><br>'
        
        ls_text_body.append(text_body_comp)
        ls_html_body.append(html_body_comp)
        
        n_new_posts_total += n_new_district_posts
        
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
    if n_new_posts_total == 0:
        print("Nie ma żadnych nowych postów.")
        return
    
    # include mail account credentials from environment variables
    # load_dotenv()
    # EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')
    # EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
    # EMAIL_TO = os.getenv('EMAIL_TO')
    
    # set up email message
    msg = MIMEMultipart('alternative')
    msg['Subject'] = f'SESJA RADY DZIELNICY ALERT łe-ło łe-ło łe-ło!!!'
    # msg['From'] = EMAIL_ADDRESS # type: ignore
    # msg['To'] = EMAIL_TO # type: ignore

    msg['From'] = 'bok@kowalsky.com' # type: ignore
    msg['To'] = 'krystyna@polska.pl' # type: ignore
    msg.attach(MIMEText(text_body, 'plain'))
    msg.attach(MIMEText(html_body, 'html'))

    # send email
    # with smtplib.SMTP('smtp.gmail.com', 587) as server:
        # server.starttls()
        # server.login(EMAIL_ADDRESS, EMAIL_PASSWORD) # type: ignore
        # server.sendmail(EMAIL_ADDRESS, EMAIL_TO, msg.as_string()) # type: ignore

    # print(text_body)
    # print()
    # print(html_body)
    # print()
    print("Nowe posty! Powiadomienie email zostało wysłane.")


if __name__ == '__main__':
    main()