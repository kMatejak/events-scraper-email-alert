def ochota():
    # import libraries
    import os
    import pickle
    import requests
    from bs4 import BeautifulSoup

    district_name = "ochota"
    FILE_PATH = os.path.abspath(os.path.dirname(__file__))


    """
    PARSE AND SCRAPE WEBPAGES FOR CURRENT POSTS
    """
    # get and parse webpage
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"}
    urls = [
        "https://ochota.um.warszawa.pl/wiecej-aktualnosci",
    ]

    # loop through pages, extract all posts, and store in dict
    current_posts_dict = {}
    n_posts_found = 0

    for url in urls:
        r = requests.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")

        post_listings = soup.find_all("div", class_="articles-list__item-content")
        n_posts_found += len(post_listings)

        for post in post_listings:
            link = post.find("a")["href"] # type: ignore
            title = post.find("span", class_="cut-text").text.strip() # type: ignore
            date_posted = post.find("time").text.strip() # type: ignore
            post_details = post.find("div", class_="articles-list__item-text").text.strip() \
                if post.find("div", class_="articles-list__item-text") else None 

            current_posts_dict.update({link: {"title": title, # type: ignore
                                            "date_posted": date_posted,
                                            "details": post_details,
                                            "link": link }
                                            })


    """
    LOAD RESULTS OF LAST EXECUTION - STORE CURRENT RESULTS
    """
    # open last saved post (create empty dict if nonexistent)
    try:
        with open(f'{FILE_PATH}/{district_name}_current_posts_dict.pkl', 'rb') as f:
            saved_posts_dict = pickle.load(f)
    except FileNotFoundError:
        saved_posts_dict = {} 

    # store current state of posts for next execution
    with open(f'{FILE_PATH}/{district_name}_current_posts_dict.pkl', 'wb') as f:
        pickle.dump(current_posts_dict, f)


    """
    FILTER POSTS AND RETURN RESULTS AS DICTIONARY
    """
    # create list containing only ids of new posts
    new_posts = {post: current_posts_dict[post] for post in current_posts_dict if post not in saved_posts_dict}
    # create written summary
    summary = f"Ogółem znalazłem {n_posts_found} postów. W tym {len(current_posts_dict)} z nich jest unikalna (nie powtarza się). " 
    summary += f"A {len(new_posts)} z nich jest nowe."

    # return touple of summary and dict with new posts if any, otherwise return None
    return (summary, new_posts)
