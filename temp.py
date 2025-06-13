import requests
from bs4 import BeautifulSoup

def find_press_release_links(base_url):
    response = requests.get(base_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    links = []

    for a in soup.find_all('a', href=True):
        href = a['href']
        if 'quarter' in href.lower() or 'results' in href.lower():
            links.append(href)

    return links

base_url = "https://www.wipro.com/investors/"
press_links = find_press_release_links(base_url)
for link in press_links:
    print(link)
