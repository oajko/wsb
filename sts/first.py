import mechanicalsoup
from bs4 import Comment
import time

url = "https://www.scrapethissite.com/"
browser = mechanicalsoup.StatefulBrowser()

def simple(p):
    div = p.select_one("section#countries").select_one("div.container")

    for row in div.find_all("div", "row"):
        sibling = row.next_sibling
        if sibling != ".row":
            continue
        for col in row.find_all("div", "col-md-4 country"):
            country = col.find("h3").text.strip()
            info = [j.text for j in col.find("div", "country-info").find_all("span")]


def forms(page):
    links = page.page.find("ul", class_ = "pagination")
    for curr_page in links.find_all("a")[1:]:
        for row in page.page.find_all("tr", class_ = "team"):
            row_contents = [i.text.strip() for i in row.find_all("td")]
        page.open(f"{url}{curr_page['href'][1:]}")


def javascript(page):
    """
    Need Selenium for AJAX-JS
    """
    page_url = page.url
    prev = None
    links = page.page.find("section").find("div", class_ = "container")
    for l in links:
        if isinstance(l, Comment):
            break
        prev = l
    for a in prev.find_all("a"):
        page.open(f'{page_url}#{a.text}')
        time.sleep(2)
        print(page.page.find("tr", class_ = "film"))
        # pg = page.page.find_all("tbody", id_ = "table-body")
        # print(pg)



def page_selector(link):
    page = link.url
    if "simple" in page:
        return
        simple(link.page)
    elif "forms" in page:
        return
        forms(link)
    elif "ajax-javascript" in page:
        javascript(link)
    elif "frames" in page:
        pass
    elif "advanced" in page:
        pass

def init_sandbox():
    browser.open(url)
    browser.follow_link("pages")

def main():
    init_sandbox()
    links_url = browser.get_url()
    links = browser.page.find_all("a")

    for link in links:
        href_link = link.get("href")
        if "/pages/" not in href_link or "/pages/" == href_link:
            continue
        browser.follow_link(link)
        page_selector(browser)
        browser.open(links_url)
        

main()