# Python script for events alerts and email notification

I redesigned this Python script (based on **[Nick Marcus’s project](https://github.com/nick-peter-marcus/job-scraper-email-alert)**) to receive email notifications whenever a new post appears on the website of the Ochota district office in Warsaw. I wanted to stay up to date on the meetings of the district council where I live.

---

There is one central, modular script, <b>job_scrape.py</b>, calling individual functions in <i>/websites/</i> each scraping a different career site.

Each scraper module works as follows:
1. Parse\* webpages containing current job listings.
2. Process and store job details in a dictionary.
3. Compare current postings with those from last execution.
4. Extract new postings and, if applicable, filter on relevant criteria (e.g. location).
5. Return a dictionary containing details of the filtered postings, or None when there are no new jobs.

These results are then joined as formatted email texts (MIMEMultipart class) in job_scrape.py. A secured SMTP connection will be started and the email will be send.

This script is executed every 24h as a scheduled task on <a href="https://www.pythonanywhere.com/">PythonAnywhere</a>.

_\*Note:
For static webpages, the **BeautifulSoup** package is used to scrape and parse HTML-documents.
For dynamic webpages, **Selenium**'s WebDriver is utilized, initiating a headless browser to capture rendered data._