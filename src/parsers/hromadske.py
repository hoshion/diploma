from datetime import datetime

import pandas as pd
from bs4 import BeautifulSoup
import requests

from src.news.models import NewsWebsite, News, NewsCategory
from src.news.serializers import NewsSerializer


class HromadskeParser:
    website = 'Hromadske'

    def __init__(self, start_year, end_year, start_month, end_month, days=None):
        self.start_year = start_year
        self.end_year = end_year
        self.start_month = start_month
        self.end_month = end_month
        self.days = days  # list of int or None
        obj, created = NewsWebsite.objects.get_or_create(name='Hromadske')
        if created:
            obj.save()
        self.newsWebsite = obj

    def get_hromadske_archive_years_links(self):
        archive_link = 'https://hromadske.ua/ssr/archive'
        return list(map(lambda x: x['url'], [a for a in requests.get(archive_link).json()['state']['data']['years'] if
                                             self.start_year <= int(a['label']) <= self.end_year]))

    def get_hromadske_archive_months_links(self, link: str):
        response = requests.get(link).text
        soup = BeautifulSoup(response, 'html.parser')
        months = soup.find('div', class_='is-month').find_all('a')
        months = list(map(lambda x: x['href'], months))
        return [m for m in months if self.start_month <= int(m.split('/')[5]) <= self.end_month]

    def get_hromadske_archive_days_links(self, link: str):
        response = requests.get(link).text
        soup = BeautifulSoup(response, 'html.parser')
        return list(map(lambda x: x['href'], soup.find('div', class_='is-day').find_all('a')))

    def get_hromadske_news_pages_links(self, link):
        response = requests.get(link).text
        soup = BeautifulSoup(response, 'html.parser')
        return list(map(lambda x: x['href'], soup.find_all('a', class_='c-sitemap-content__link')))

    def get_hromadske_news_page(self, link: str):
        response = requests.get(link, allow_redirects=False).text
        soup = BeautifulSoup(response, 'html.parser')
        if soup.find('title').text.startswith('Redirecting'):
            return None, None, None
        if response is not None:
            section = self.get_section(soup)
            text = self.get_news_body(soup)
            date = self.get_news_date(soup)
            return section, text, date

    def get_news_body(self, soup: BeautifulSoup):
        title = soup.find('h1', class_='c-heading__title')
        title_text = '' if title is None else title.text + '. '
        content = soup.find('div', class_='c-content') 
        if content is None:
            content = soup.find('div', class_='s-content')
        content_text = '' if content is None else ''.join(map(lambda x: x.text, soup.find('div', class_='s-content').find_all('p')))
        return title_text + content_text

    def get_section(self, soup: BeautifulSoup):
        breadcrumbs_parts = soup.find_all(class_='c-breadcrumbs__segment')
        if len(breadcrumbs_parts) != 3:
            return 'Без теми'
        return breadcrumbs_parts[1].get_text()
    
    def get_news_date(self, soup: BeautifulSoup):
        date = soup.find('time', class_='c-post-header__date').get('datetime')
        print(date)
        return datetime.fromisoformat(date)

    def parse(self):
        years = self.get_hromadske_archive_years_links()
        for year in years:
            months = self.get_hromadske_archive_months_links(year)
            for month in months:
                days = self.get_hromadske_archive_days_links(month)
                for day_link in days:
                    strings = day_link.split('/')
                    year = strings[4]
                    month = strings[5]
                    day = strings[6]
                    # Only process if day is in self.days (if provided)
                    if self.days is not None and int(day) not in self.days:
                        continue
                    links = self.get_hromadske_news_pages_links(day_link)
                    for link in links:
                        section, text, date = self.get_hromadske_news_page(link)
                        if section is None:
                            continue
                        category, created = NewsCategory.objects.get_or_create(name=section)
                        if created:
                            category.save()
                        newsDb = NewsSerializer(News.objects.filter(published_at__exact=date), many=True).data
                        if len(newsDb) == 0:
                            news = News(content=text, category=category, website=self.newsWebsite, published_at=date)
                            news.save() 