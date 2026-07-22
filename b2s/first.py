import requests
from bs4 import BeautifulSoup
from urllib.request import urlopen
import mechanicalsoup

URL = "https://books.toscrape.com/"



b = mechanicalsoup.StatefulBrowser()