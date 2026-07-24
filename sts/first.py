import mechanicalsoup
import selenium
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

URL = "https://www.scrapethissite.com/pages"

def simple(link):
    browser = mechanicalsoup.StatefulBrowser()
    browser.open(link)
    div = browser.page.select_one("section#countries").select_one("div.container")
    for row in div.find_all("div", "row"):
        sibling = row.next_sibling
        if sibling != ".row":
            continue
        for col in row.find_all("div", "col-md-4 country"):
            country = col.find("h3").text.strip()
            info = [j.text for j in col.find("div", "country-info").find_all("span")]
    browser.close()


def forms(link):
    browser = mechanicalsoup.StatefulBrowser()
    browser.open(link)
    page = browser.page
    for curr_page in page.find("ul", class_ = "pagination").find_all("a")[1:]:
        for row in page.find_all("tr", class_ = "team"):
            row_contents = [i.text.strip() for i in row.find_all("td")]
            print(row_contents)
        browser.open(f"{URL}{curr_page['href'][1:]}")
    browser.close()


def javascript(page):
    options = selenium.webdriver.FirefoxOptions()
    options.add_argument("-headless")

    driver = selenium.webdriver.Firefox(options = options)
    driver.get(page)
    years = driver.find_elements(by = By.CLASS_NAME, value = "year-link")
    for year in years:
        driver.execute_script("arguments[0].click()", year)
        WebDriverWait(driver, 10).until(
            lambda d: d.find_element(By.CLASS_NAME, "table").value_of_css_property("display") == "table"
        )
        rows = driver.find_elements(By.CLASS_NAME, "film")
        for row in rows:
            elements = row.find_elements(By.XPATH, "./*")
            t = []
            for element in elements:
                if element.get_attribute("class") == "film-best-picture":
                    t.append(1) if element.find_elements(By.XPATH, ".//*") else t.append(0)
                    continue
                t.append(element.text)
    driver.close()


def iframes(page):
    options = selenium.webdriver.FirefoxOptions()
    options.add_argument("-headless")

    driver = selenium.webdriver.Firefox(options = options)
    driver.get(page)
    driver.switch_to.frame(driver.find_element(By.ID, "iframe"))
    rows = driver.find_elements(By.CLASS_NAME, "row")
    for i in range(len(rows)):
        row = driver.find_elements(By.CLASS_NAME, "row")[i]
        cols = row.find_elements(By.CLASS_NAME, "col-md-4")
        for j in range(len(cols)):
            row = driver.find_elements(By.CLASS_NAME, "row")[i]
            col = row.find_elements(By.CLASS_NAME, "col-md-4")[j]

            click_btn = col.find_element(By.CLASS_NAME, "btn")
            click_btn.click()
            WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.CLASS_NAME, "family-name"))
            )
            text_chunk = driver.find_element(By.CLASS_NAME, "lead")
            title = driver.find_element(By.TAG_NAME, "h3").text.strip()
            nodes = driver.execute_script("""
                return Array.from(arguments[0].childNodes).map(n => ({
                    type:n.nodeType,
                    name:n.nodeName,
                    text:n.textContent})
                )
            """, text_chunk)
            text = []
            for n in nodes:
                text.append(n['text'].strip())
            text = " ".join(text)
            out = {"title": title, "text": text}
            print(out)

            driver.find_element(By.CLASS_NAME, "btn").click()

            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "btn"))
            )

    driver.close()

def header_spoof(page):
    options = selenium.webdriver.FirefoxOptions()
    options.add_argument("-headless")
    driver = selenium.webdriver.Firefox(options = options)
    driver.get(page)
    orig = driver.current_window_handle

    driver.find_element(By.CSS_SELECTOR, "h4 a").click()
    WebDriverWait(driver, 10).until(
        lambda d: len(d.window_handles) > 1
    )

    new_window = [w for w in driver.window_handles if w != orig][0]
    driver.switch_to.window(new_window)
    
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CLASS_NAME, "col-md-4"))
    )
    good_text = driver.find_element(By.CLASS_NAME, "col-md-4").text
    print(good_text)

    driver.close()


def page_selector(link):
    page = f"{URL}/{link}"
    if "simple" in page: return # simple(page)
    elif "forms" in page: return # forms(page)
    elif "ajax-javascript" in page: return # javascript(page)
    elif "frames" in page: return # iframes(page)
    elif "advanced" in page: header_spoof(page)


def main():
    N = len("/pages/")
    browser = mechanicalsoup.StatefulBrowser()
    browser.open(URL)
    links = [l["href"] for l in browser.page.find("section").find("div", class_ = "container").find_all("a")]
    browser.close()

    for link in links:
        page_selector(link[N:])
        

main()