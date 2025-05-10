import urllib
from typing import List, Tuple

import requests
from bs4 import BeautifulSoup as bs

from parser import fetch_urls

COOKIES = {
    "NID": "523=qPTn_OFiHfzOZjm9RtjrYLveWz-_W00Vz8G-DMbB2Yd8cetFyKuts-4g4HKH6iyF2L2zSCVf9Vsg43cvBZx-aAf8_y2mMgKdaP7YmKQ8joUpFdhgenVLcA-P0B6D124cXyvDqDYQEnCcyHXTwmHMaDU5e67YMgyySGwGd3FL08c8rfStv3EbELTOLRkuEQ7FsLAu3S9w6BdqDu19pJGHvpXnO9i6yt4kyhA271jbgejZQnfAu9WzobiLTo5hBLTY",
    "DV": "4wHnNwE6J60fQIaWaSHSPtADSJ2iYhk",
    "AEC": "AVcja2cOnzWiImAaGBh3sPOVdmrEdMU9j7E7zBS6XWyF9lGl4PLlrhh2XQ",
}


def get_google_html(request: str) -> str:
    request_text = request.replace(" ", ' ').replace('\n', ' ').replace('\t', ' ')
    request_text = request_text.lower()
    response = requests.get('https://www.google.ru/search?q={}'.format(request_text),
                            cookies=COOKIES)
    return response.text


def get_urls_on_google_page(html: str) -> List[str]:
    parser = bs(html, "html.parser")
    main = parser.find('div', attrs={"id": "main"}).extract()
    urls = list()
    for div in main.find_all('div', recursive=False):
        url = div.find('a')
        if url and url.get('href', ''):
            url = url.get('href', '')
            if url.startswith('/url') and all(
                    x not in url for x in ['google.com', 'youtube.com', 'rutube.ru', 'yandex.ru/video']):
                url = url.replace('/url?q=', '')
                url = url.split("&")[0]
                urls.append(url)
    urls = list(set(urls))
    return urls


def clean_html_and_extract_text(html: str) -> str:
    soup = bs(html, "html.parser")
    for tag in soup(['script', 'style', 'footer', 'nav', 'header', 'iframe']):
        tag.decompose()
    return soup.get_text(separator='\n', strip=True)


def get_texts_and_urls_from_google_search(user_request: str) -> Tuple[List[str], List[str]]:
    google_html = get_google_html(user_request)
    urls = get_urls_on_google_page(google_html)
    urls = list(map(urllib.parse.unquote, urls))
    htmls = fetch_urls(urls)
    texts = list(map(clean_html_and_extract_text, htmls))
    return texts, urls
