#!/usr/bin/env python3
"""
Test crawler
"""

__author__ = "Jason Beach"
__version__ = "0.1.0"
__license__ = "AGPL-3.0"

from src.modules.enterodoc.url import UrlFactory, UniformResourceLocator
from src.web.crawler import Crawler, scenario

urls = ['https://www.jpmorgan.com']
URL = UrlFactory()
Url_list = [URL.build(url) for url in urls]
#scenario.url = Url_list[0]
scenario.base_url = None
scenario.urls = Url_list
scenario.depth = 0
crawler = Crawler(
                scenario=scenario,
                logger=None,
                exporter=''
                )


def test_crawler_check_urls_are_valid():
    valid_urls = crawler.check_urls_are_valid()
    assert valid_urls.__len__() == 1

def test_crawler_generate_href_chain_without_base_url():
    valid_urls = crawler.check_urls_are_valid()
    result_urls = crawler.generate_href_chain()
    assert len(result_urls.keys()) == 1
    key = list(result_urls.keys())[0]
    assert len(result_urls[key]) == 60

def test_crawler_generate_href_chain_with_base_url():
    scenario.base_url = URL.build('https://www.jpmorgan.com')
    url_list = ['https://www.chase.com']
    scenario.urls = [URL.build(url) for url in url_list]
    scenario.depth = 0
    crawler.add_scenario(scenario)

    valid_urls = crawler.check_urls_are_valid()
    result_urls = crawler.generate_href_chain()
    assert True == False