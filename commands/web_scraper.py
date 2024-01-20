import requests
import re
import lxml.html

from scrapeghost import SchemaScraper

try:
	from googlesearch import search
except ImportError:
		print("No module named 'google' found")

# Scraper schema that specifies the format in which to return the site data
scrape_site = SchemaScraper(
  schema={
      "page_title": "string",
			"authors": "string",
			"date": "string",
			"page_keywords": "string",
			"page_all_text": "string",
  }
)

def scrape_site_formatted(url: str):
	"""
	Given a url, scrape the site using GPT3.5 using the scrapeghost helper library
	"""
	resp = scrape_site(url)
	return resp.data

def parse_url_or_html(url_or_html: str) -> lxml.html.Element:
    """
    Given URL or HTML, return lxml.html.Element
    """
    # coerce to HTML
    orig_url = None
    if url_or_html.startswith("http"):
        orig_url = url_or_html
        url_or_html = requests.get(url_or_html).text
    # collapse whitespace
    url_or_html = re.sub("[ \t]+", " ", url_or_html)
    doc = lxml.html.fromstring(url_or_html)
    if orig_url:
        doc.make_links_absolute(orig_url)
    return doc


def get_google_search_results(query: str):
	"""
	Given a query, return the top 5 google search results
	"""
	results = search(query, tld="co.in", num=5, stop=5, pause=2)
	return results

