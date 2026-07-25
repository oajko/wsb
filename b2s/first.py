import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import TypedDict
import sqlite3
import time
import random

URL = "https://books.toscrape.com/catalogue/"
stars_dict = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}

def get_links(url):
    """
    Get all book url links

    Args:
        url (str): Page url to get book urls

    Return:
        List: All book links on the site
    """
    time.sleep(random.random() * 6)
    all_links = []
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")

    links = soup.find_all("h3")
    for link in links:
        all_links.append(f"{URL}{link.find('a')['href']}")
    page.close()
    return all_links


def safe(func):
    """
    Error handling page scraping with fallback None

    Args:
        func (callable): Zero arugment callable to execute

    Return:
        Any | None: Callable's value or None if exception
    """
    try:
        return func()
    except:
        return None


class ScrapeFields(TypedDict):
    """
    Book data extracted
    """
    genre: str | None
    title: str | None
    price: float | None
    stock_qty: int | None
    stock_bool: bool | None
    stars: int | None
    desc: str | None


def scrape_content(book_url):
    """
    Scrape the content of one url.

    Args:
        url (str): Url of product page
    
    Return:
        ScrapeFields
    """
    time.sleep(random.random() * 6)
    try:
        page = requests.get(book_url)
        soup = BeautifulSoup(page.text, "html.parser")

        storage: ScrapeFields = {
            "genre": safe(lambda: soup.select("ul.breadcrumb a")[-1].get_text(strip = True)),
            "title": safe(lambda: soup.find("h1").get_text(strip = True)),
            "price": safe(lambda: float(soup.select_one("p.price_color").get_text(strip = True)[2:])),
            "stock_qty": safe(lambda: int(soup.select_one("p.availability").get_text(strip = True).split(" ")[2][1:])),
            "stars": safe(lambda: stars_dict[soup.select_one("p.star-rating")["class"][-1].strip()]),
            "desc": safe(lambda: soup.select_one("div#product_description").find_next_sibling().get_text(strip = True))
        }
        storage["stock_bool"] = storage["stock_qty"] > 0 if storage["stock_qty"] else None

        page.close()
        return storage
    except:
        return

def thread_pool_scrape(all_urls):
    """
    Scrape book urls with threading

    Args:
        all_urls(list[str]): A list of book urls to scrape
    
    Returns:
        list[ScrapeFields]: A list of scraped books
    """
    all_content = []
    with ThreadPoolExecutor(max_workers = 16) as executor:
        future = list(map(lambda x: executor.submit(scrape_content, x), all_urls))
        for f in as_completed(future):
            if f.result() is not None:
                all_content.append(f.result())
    return all_content


def thread_get_links():
    """
    Scrape links to books

    Returns:
        list[str]: A list of book urls
    """
    all_links = []
    page_urls = [f"{URL}page-{i}.html" for i in range(1, 3)]
    with ThreadPoolExecutor(max_workers = 16) as executor:
        futures = list(map(lambda x: executor.submit(get_links, x), page_urls))
        for f in as_completed(futures):
            all_links.extend(f.result())
    return all_links


def main():
    links = thread_get_links()
    contents = thread_pool_scrape(links)

    connection = sqlite3.connect("books.db")
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            genre TEXT,
            title TEXT,
            price REAL,
            stock_qty INTEGER,
            stars INTEGER,
            desc TEXT,
            stock_bool BOOLEAN
        )
    """)

    cursor.executemany("""
        INSERT INTO books (genre, title, price, stock_qty, stars, desc, stock_bool) VALUES (?, ?, ?, ?, ?, ?, ?)""",
        [(c['genre'], c['title'], c['price'], c['stock_qty'], c['stars'], c['desc'], c['stock_bool']) for c in contents]
    )
    connection.commit()

if __name__ == "__main__":
    main()