import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed

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


def scrape_content(book_url):
    """
    Scrape the content of one url.

    Args:
        url (str): Url of product page
    
    Return:
        dict{
            genre (str): book genre
            title (str): book title
            price (float): price of book
            stock_qty (int): qty of stock available
            stock_bool (bool): book has available stock
            stars (int): product rating
            desc (str): book desc
        }
    """
    try:
        page = requests.get(book_url)
        soup = BeautifulSoup(page.text, "html.parser")

        genre = safe(lambda: soup.select("ul.breadcrumb a")[-1].get_text(strip = True))
        title = safe(lambda: soup.find("h1").get_text(strip = True))
        price = safe(lambda: float(soup.select_one("p.price_color").get_text(strip = True)[2:]))
        stock_qty = safe(lambda: int(soup.select_one("p.availability").get_text(strip = True).split(" ")[2][1:]))
        stock_bool = stock_qty > 0 if stock_qty else None
        stars = safe(lambda: stars_dict[soup.select_one("p.star-rating")["class"][-1].strip()])
        desc = safe(lambda: soup.select_one("div#product_description").find_next_sibling().get_text(strip = True))
        page.close()
        return {
            "genre": genre,
            "title": title,
            "price": price,
            "stock_qty": stock_qty,
            "stock_bool": stock_bool,
            "stars": stars,
            "desc": desc
        }
    except:
        return

def thread_pool_scrape(all_urls):
    """
    Scrape book urls with threading

    Args:
        all_urls(list[str]): A list of book urls to scrape
    
    Returns:
        list[dict]: A list of scraped books
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
    page_urls = [f"{URL}page-{i}.html" for i in range(1, 51)]
    with ThreadPoolExecutor(max_workers = 16) as executor:
        futures = list(map(lambda x: executor.submit(get_links, x), page_urls))
        for f in as_completed(futures):
            all_links.extend(f.result())
    return all_links


def main():
    links = thread_get_links()
    contents = thread_pool_scrape(links)
    # print(contents)


if __name__ == "__main__":
    main()