def main():
    import os
    import ssl
    import csv
    import smtplib
    from dotenv import load_dotenv
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
                          f'Hej, tu twój Boromeusz! Mam wieści!<br>Właśnie się ukazało: <br><br>')

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

        text_body_comp += (f'\n---\n'
                           f'\nBoromeusz Dzielnicowy to wyjątkowy służbista. To wysoce wykwalifikowany ' 
                           f'skrypt w języku Python, który podejmuje się *dokładnie* jednego zadania. '
                           f'Raz na dobę Boromeusz przegląda podstrony z aktualnościami wybranych przez Ciebie urzędów ' 
                           f'dzielnic i wysyła Ci powiadomienie, gdy pojawi się zapowiedź sesji rady w danej dzielnicy / dzielnicach.' 
                           f'\n\n\nBoromeusz Dzielnicowy to projekt twojego fellow razemka, Krzysztofa Matejaka (matejak.com). ' 
                           f'\n\nSpokojnie, zazwyczaj nie gryzie przy próbach kontaktu. Chętnie opowiada boromejskie przypowieści.\n\n')
        html_body_comp += (f'<br><hr><br>'
                           f'<br>Boromeusz Dzielnicowy to wyjątkowy służbista. To wysoce wykwalifikowany '
                           f'skrypt w języku Python, który podejmuje się *dokładnie* jednego zadania. '
                           f'Raz na dobę Boromeusz przegląda podstrony z aktualnościami wybranych przez Ciebie urzędów ' 
                           f'dzielnic i wysyła Ci powiadomienie, gdy pojawi się zapowiedź sesji rady w danej dzielnicy / dzielnicach.'
                           f'<br><br><br>Boromeusz Dzielnicowy to projekt twojego <i>fellow</i> razemka, '
                           f'<br>Krzysztofa Matejaka (<a href="https://matejak.com/">matejak.com</a>).'  
                           f'<br>Spokojnie, zazwyczaj nie gryzie przy próbach kontaktu ;) Chętnie opowiada boromejskie przypowieści.<br><br>')
        
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
    load_dotenv()
    EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')
    EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
    
    # set up email message
    msg = MIMEMultipart('alternative')
    msg['Subject'] = f'SESJA RADY DZIELNICY łe-ło łe-ło łe-ło!!!'
    msg['From'] = str(EMAIL_ADDRESS)
    msg.attach(MIMEText(text_body, 'plain'))
    msg.attach(MIMEText(html_body, 'html'))

    # send emails
    port = 465
    smtp_server = "smtp.wp.pl"
    sender_email = EMAIL_ADDRESS
    password = EMAIL_PASSWORD
    recipients = []

    with open("contacts.csv") as file:
        csv_reader = csv.reader(file, delimiter=',')
        next(csv_reader)  # Skip header row
        for row in csv_reader:
            recipients.append(str(row[0]))

    msg['To'] = ", ".join(recipients)
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(
        smtp_server,
        port,
        context=context,
        ) as server:
        server.login(sender_email, password) # type: ignore
        server.sendmail(sender_email, recipients, msg.as_string()) # type: ignore

    print("Nowe posty! Powiadomienie email zostało wysłane.")


if __name__ == '__main__':
    main()