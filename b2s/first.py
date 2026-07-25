import requests
from bs4 import BeautifulSoup

URL = "https://books.toscrape.com/catalogue/"
stars_dict = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}

def get_links():
    all_links = []
    for page_num in range(1, 51):
        url = f"{URL}page-{page_num}.html"
        page = requests.get(url)
        soup = BeautifulSoup(page.text, "html.parser")

        links = soup.find_all("h3")
        for link in links:
            all_links.append(f"{URL}{link.find('a')['href']}")
        page.close()

    return all_links

def scrape_content(book_url):
    page = requests.get(book_url)
    soup = BeautifulSoup(page.text, "html.parser")

    category = soup.select("ul.breadcrumb a")[-1].text.strip()
    title = soup.find("h1").text.strip()
    t = soup.select("p.price_color")
    price = float(soup.select_one("p.price_color").text[2:].strip())
    stock_amount = int(soup.select_one("p.availability").text.strip().split(" ")[2][1:])
    stock_bool = stock_amount > 0
    title = soup.find("h1").text.strip()
    stars = stars_dict[soup.select_one("p.star-rating")["class"][-1].strip()]
    desc = soup.select_one("div#product_description").find_next_sibling().text


def main():
    links = get_links()
    scrape_content(links[0])

main()