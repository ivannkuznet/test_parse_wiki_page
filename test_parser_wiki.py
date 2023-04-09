import requests
import pytest

from bs4 import BeautifulSoup
from dataclasses import dataclass

URL = "https://en.wikipedia.org/wiki/Programming_languages_used_in_most_popular_websites"
TABLE_LOCATOR = ".wikitable"


@dataclass
class WebsitesInfo:
    """Contains data from «Programming languages used in most popular websites» table
    """
    website_name: str
    popularity: int
    frontend_language: str
    backend_language: str
    database: str
    notes: str


@pytest.fixture(scope='session')
def parse_wiki_page():
    """A fixture that makes a GET request to the Wiki page and returns a list of Websites objects and their
    info from the first table.
    """
    response = requests.get(URL)
    all_elements_from_page = BeautifulSoup(response.text, "html.parser")
    table = all_elements_from_page.select(TABLE_LOCATOR)[0]
    rows = table.select('tr')[1:]
    websites_information = []
    for row in rows:
        cells = row.select('td')
        website_name = cells[0].a['title']
        cleanup_popularity = cells[1].text.replace(',', '').replace('.', '').split("[")[0].split("(")[0].strip()
        popularity = int(cleanup_popularity)
        frontend_language = ', '.join([a['title'] for a in cells[2].select('td a[title]')])
        backend_language = ', '.join([a['title'] for a in cells[3].select('td a[title]')])
        database = ', '.join([a['title'] for a in cells[4].select('td a[title]')])
        notes = cells[5].text.strip()

        websites_information.append(WebsitesInfo(
            website_name, popularity, frontend_language, backend_language, database, notes))

    return websites_information


@pytest.mark.parametrize('visitors',
                         [10 ** 7, 1.5 * 10 ** 7, 5 * 10 ** 7, 10 ** 8, 5 * 10 ** 8, 10 ** 9, 1.5 * 10 ** 9])
def test_visitors_per_month(parse_wiki_page, visitors):
    """The test checks that there are no rows in the «Programming languages used in most popular websites» table that
    have the value in the "Popularity(unique visitors per month)" column less than the value passed as a
    parameter to the test.
    """
    errors = []
    for website in parse_wiki_page:
        if website.popularity < visitors:
            error_message = f'{website.website_name} ' \
                            f'(Frontend: {website.frontend_language} | Backend: {website.backend_language}) has ' \
                            f'{visitors} unique visitors per month. (Expected more than {website.popularity})\n'
            errors.append(error_message)
    if errors:
        error_message = '\n'.join(errors)
        raise AssertionError(error_message)
