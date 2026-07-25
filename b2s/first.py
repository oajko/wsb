import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed

URL = "https://books.toscrape.com/catalogue/"
stars_dict = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}

def get_links():
    """
    Get all book url links

    Return:
        List: All book links on the site
    """
    all_links = []
    for page_num in range(1, 2):
        url = f"{URL}page-{page_num}.html"
        page = requests.get(url)
        soup = BeautifulSoup(page.text, "html.parser")

        links = soup.find_all("h3")
        for link in links:
            all_links.append(f"{URL}{link.find('a')['href']}")
        page.close()

    return all_links

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
    page = requests.get(book_url)
    soup = BeautifulSoup(page.text, "html.parser")

    genre = soup.select("ul.breadcrumb a")[-1].text.strip()
    title = soup.find("h1").text.strip()
    price = float(soup.select_one("p.price_color").text[2:].strip())
    stock_qty = int(soup.select_one("p.availability").text.strip().split(" ")[2][1:])
    stock_bool = stock_qty > 0
    stars = stars_dict[soup.select_one("p.star-rating")["class"][-1].strip()]
    desc = soup.select_one("div#product_description").find_next_sibling().text
    return {
        "genre": genre,
        "title": title,
        "price": price,
        "stock_qty": stock_qty,
        "stock_bool": stock_bool,
        "stars": stars,
        "desc": desc
    }

def thread_pool_scrape(all_urls):
    all_content = []
    with ThreadPoolExecutor(max_workers = 16) as executor:
        future = list(map(lambda x: executor.submit(scrape_content, x), all_urls))
        for f in as_completed(future):
            all_content.append(f.result())

    print(all_content)


def main():
    links = get_links()
    thread_pool_scrape(links)

main()