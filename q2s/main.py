import mechanicalsoup
import requests
from bs4 import BeautifulSoup
from typing import TypedDict
from dotenv import load_dotenv
import os

load_dotenv()

URL = "https://quotes.toscrape.com"
PROXY = "dc.oxylabs.io:8000"

seen_authors = set()

def login():
    """
    Login as user to view user locked hierarchy content

    Return:
        browser (StatefulBrowser): http user request with login setting
    """
    browser = mechanicalsoup.StatefulBrowser()
    browser.open(f"{URL}/login")
    browser.select_form()

    browser["username"] = "test"
    browser["password"] = "test"

    browser.submit_selected()
    return browser.session


def create_auth_sess(session):
    """
    Passes login session and header settings into new url

    Args:
        session
    """
    s = requests.Session()

    s.cookies.update(session.cookies)
    s.headers.update(session.headers)

    proxies = 'https://user-%s:%s@%s' % (os.getenv('PROXY_USERNAME'), os.getenv('PROXY_PASSWORD'), PROXY)
    s.proxies.update({"http": proxies, "https": proxies})

    return s


class Data(TypedDict):
    quote: str | None
    author: str | None
    person_page: str | None
    goodreads: str | None
    tags: list | None

    born_date: str | None
    born_location: str | None
    author_desc: str | None


def safe(func):
    try:
        return func()
    except:
        return None


def scrape(session, html):
    soup = BeautifulSoup(html, "html.parser")
    all_data = []

    for row in soup.find_all("div", class_ = "quote"):
        data: Data = {
            "quote": safe(lambda: row.find(class_ = "text").get_text(strip = True)),
            "author": safe(lambda: row.find(class_ = "author").get_text(strip = True))
        }
        links_ = row.find_all("span")[1].find_all("a")
        data["person_page"] = safe(lambda: links_[0]['href'])
        data["goodreads"] = safe(lambda: links_[1]['href'])
        data["tags"] = safe(lambda: [i.get_text(strip = True) for i in row.find(class_ = "tags").find_all("a")])
        if data["author"] not in seen_authors:
            s = BeautifulSoup(session.get(f"{URL}{data['person_page']}").text, "html.parser")
            data["born_date"] = safe(lambda: s.find(class_ = "author-born-date").get_text(strip = True))
            data["born_location"] = safe(lambda: s.find(class_ = "author-born-location").get_text(strip = True))
            data["author_desc"] = safe(lambda: s.find(class_ = "author-description").get_text(strip = True))
            seen_authors.add(data["author"])
        all_data.append(data)
    return all_data


def get_content(login_session):
    next_page = ""
    all_data = []

    while next_page is not None:
        session = create_auth_sess(login_session)
        html = session.get(f"{URL}{next_page}" if next_page else URL).text
        all_data.extend(scrape(login_session, html))

        n = BeautifulSoup(html, "html.parser").find(class_ = "next")
        next_page = n.find("a")["href"] if n else None
    return all_data


def main():
    login_session = login()
    c = get_content(login_session)


if __name__ == "__main__":
    main()