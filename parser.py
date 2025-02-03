import pandas as pd
from bs4 import BeautifulSoup
import requests
import time


def get_hromadske_archive_years_links(start_year, end_year):
    archive_link = 'https://hromadske.ua/ssr/archive'
    return list(map(lambda x: x['url'], [a for a in requests.get(archive_link).json()['state']['data']['years'] if
                                         start_year <= int(a['label']) <= end_year]))


def get_hromadske_archive_months_links(link: str, start_month, end_month):
    response = requests.get(link).text
    soup = BeautifulSoup(response, 'html.parser')
    months = soup.find('div', class_='is-month').find_all('a')
    months = list(map(lambda x: x['href'], months))
    return [m for m in months if start_month <= int(m.split('/')[5]) <= end_month]


def get_hromadske_archive_days_links(link: str):
    response = requests.get(link).text
    soup = BeautifulSoup(response, 'html.parser')
    return list(map(lambda x: x['href'], soup.find('div', class_='is-day').find_all('a')))


def get_hromadske_news_pages_links(link):
    response = requests.get(link).text
    soup = BeautifulSoup(response, 'html.parser')
    return list(map(lambda x: x['href'], soup.find_all('a', class_='c-sitemap-content__link')))


def get_hromadske_news_page(link: str):
    response = requests.get(link, allow_redirects=False).text
    soup = BeautifulSoup(response, 'html.parser')
    if soup.find('title').text.startswith('Redirecting'):
        return None, None
    if response is not None:
        section = get_section(soup)
        text = get_news_body(soup)
        return section, text


def get_news_body(soup: BeautifulSoup):
    return soup.find('h1', class_='c-heading__title').text + '. ' + ''.join(map(lambda x: x.text, soup.find('div', class_='s-content').find_all('p')))


def get_section(soup: BeautifulSoup):
    breadcrumbs_parts = soup.find_all(class_='c-breadcrumbs__segment')
    if len(breadcrumbs_parts) != 3:
        return 'Без теми'
    return breadcrumbs_parts[1].get_text()


def get_hromadske_news():
    result = {'year': [], 'month': [], 'day': [], 'section': [], 'text': []}
    years = get_hromadske_archive_years_links(2019, 2019)
    for year in years:
        months = get_hromadske_archive_months_links(year, 7, 7)
        for month in months:
            days = get_hromadske_archive_days_links(month)
            for day_link in days:
                strings = day_link.split('/')
                year = strings[4]
                month = strings[5]
                day = strings[6]
                links = get_hromadske_news_pages_links(day_link)
                for link in links:
                    section, text = get_hromadske_news_page(link)
                    if section is None:
                        continue
                    result['year'].append(year)
                    result['month'].append(month)
                    result['day'].append(day)
                    result['section'].append(section)
                    result['text'].append(text)
                    print(year, month, day, section, text)
    pd.DataFrame(data=result).to_excel('hromadske.xlsx')


if __name__ == '__main__':
    get_hromadske_news()
