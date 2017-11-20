# -*- coding: utf-8 -*-

"""Scrape all regions"""

from bs4 import BeautifulSoup
import requests

REGIONS_URL = 'http://www.craigslist.org/about/sites'


def get_all_regions():
    """scrape all regions"""
    response = requests.get(REGIONS_URL)
    response.raise_for_status()  # Something failed?
    soup = BeautifulSoup(response.content, 'html.parser')
    regions = set()

    for box in soup.findAll('div', {'class': 'box'}):
        for a in box.findAll('a'):
            # Remove protocol and get subdomain
            region = a.attrs['href'].rsplit('//', 1)[1].split('.')[0]
            regions.add(region)

    return regions
