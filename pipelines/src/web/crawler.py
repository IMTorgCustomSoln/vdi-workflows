#!/usr/bin/env python3
"""
URL to PDF Workflow
"""

__author__ = "Jason Beach"
__version__ = "0.1.0"
__license__ = "MIT"


from ..structures.url import UniformResourceLocator
from ..services._constants import logger

import googlesearch

from pathlib import Path
import itertools



#argument templates
class BaseLogger:
    """Base class for the Crawler's logger."""
    def __init__(self):
        pass

    def info(self, msg):
        print('INFO: {msg}')

    def error(self, msg):
        print('ERROR: {msg}')


class BaseSearchScenario:
    """Base class for the Crawler's search scenario conditions."""
    def __init__(self, url, list_of_search_terms):
        self.url = url
        self.list_of_search_terms = list_of_search_terms


class BaseExporter:
    """Base class for the Crawler's exporter."""
    def __init__(self):
        pass

    def export(self, url_list):
        return url_list




scenario = BaseSearchScenario(url='',
                              list_of_search_terms=['creditcard`, `fees', 'terms conditions', 'overdraft', 'non insufficient funds']
                                )




#primary class
class Crawler:
    """Crawl sites specific to a url and search terms to
    produce a list of urls which can be exported.

    This is an 'opportunistic' crawler in that it only 
    accepts an initial domain and search scenario, then
    leverages google search to find target pages.
    
    Usage::
    UrlCrawl = Crawler(logger, exporter, scenario)
    """

    def __init__(self, scenario, logger, exporter):
        self.scenario = scenario
        self.scenario.url = self._ensure_url_class(scenario.url)
        self.logger = logger
        self.exporter = exporter

    def __repr__(self):
        return self.scenario.url
    
    def _ensure_url_class(self, url):
        """Provide url of class UniformResourceLocator if not one already."""
        result = url if type(url) == UniformResourceLocator else UniformResourceLocator(url)
        return result
    
    def check_urls_are_valid(self, url_list, base_url=''):
        """Basic checks of urls in a list
        * ensure proper url formatting
        * consistent domain owner (if base_domain provided)
        """
        validated_urls = []
        BaseUrl = self._ensure_url_class(base_url)
        if base_url:
            BaseUrl.check_valid_format()
        url_list = list(set(url_list))
        for url in url_list:  
            Url = self._ensure_url_class(url)
            check_scheme = Url.check_scheme()
            check_owner = Url.has_same_url_owner_(BaseUrl) if base_url else True
            if check_scheme and check_owner:
                validated_urls.append(Url)
            else:
                pass
        logger.info(f'validated urls: {validated_urls}')
        return validated_urls

    def generate_href_chain(self):
        """Given a domain name, collects the appropriate
        href links."""
        result_urls = {}
        
        initial_list = self.get_initial_url_list(self.scenario.url, self.list_of_search_terms)
        hrefs = self.get_hrefs_within_depth(base_url = self.scenario.url, 
                                           depth = 0, 
                                           initial_url_list = initial_list
                                           )
        result_urls[self.scenario.url] = hrefs
        self.logger.info(f"result_urls: {result_urls}")
        return result_urls

    def get_initial_url_list(self, url, list_of_search_terms=[]):
        """Get initial list of urls from google given search terms."""
        NumberOfSearchResults = 5
        BaseUrl = UniformResourceLocator('https://www.jpmorgan.com')
        domain = url.get_domain()

        term_permutations = list(itertools.permutations(list_of_search_terms, r=2))
        search_terms_list = []
        for tup in term_permutations:
            tmp = list(tup)
            tmp.append(domain)
            search_terms_list.append(tmp)
        stringified_lists = [' '.join(terms) for terms in search_terms_list]

        result_url_list = []
        for terms in stringified_lists:
            try:
                search_results = googlesearch.search(query = terms, 
                                                     stop =  NumberOfSearchResults,
                                                     pause = 1 
                                                     )
                unique_urls = [url for url in search_results if url not in result_url_list]
                SearchUrls = [UniformResourceLocator(result) for result in unique_urls]
                ValidUrls = self.check_urls_are_valid(url_list = SearchUrls, 
                                                 base_url = BaseUrl
                                                 )
                result_url_list.extend(ValidUrls)
            except:
                self.logger.error('ERROR: there was a problem making the request to google.com.')
        return result_url_list


    def get_hrefs_within_depth(self, base_url, depth=1, initial_url_list=[]):
        """Get all hrefs from a page, within a depth, and certain criteria.

        This is similar to `wget --recursive http://site.com`, but it removes 
        links that are out of scope.
        """
        BaseUrl_JPM = UniformResourceLocator('https://www.jpmorgan.com')
        searched_hrefs = set()
        BaseUrl = self._ensure_url_class(base_url)
        #if len(initial_url_list) == 0:
        #    hrefs = BaseUrl.get_hrefs_within_hostname_(searched_hrefs = searched_hrefs)
        #    #searched_hrefs = add_list_to_set(searched_hrefs, hrefs)
        #else:
        #    hrefs = initial_url_list
        hrefs = initial_url_list
        while depth > -1:
            level_hrefs = []
            for url in hrefs:
                Url = self._ensure_url_class(url)
                check_owner = Url.has_same_url_owner_(BaseUrl)
                if not (Url in searched_hrefs) and not check_owner:
                    new_hrefs = Url.get_hrefs_within_hostname_(searched_hrefs = searched_hrefs)
                    valid_hrefs = self.check_urls_are_valid(url_list = new_hrefs, 
                                                       base_url = BaseUrl_JPM
                                                       )
                    searched_hrefs.add(Url)
                    level_hrefs.extend(valid_hrefs)
            hrefs = list(set(level_hrefs))
            depth = depth - 1

        return searched_hrefs
    

    def export(self, urls):
        """Export urls through customization of BaseExporter class.

        The result is typically one of the following:
        * bool - result of process
        * [bool] - list of bools for result of multiple processes
        * [f(url)] - transformation of the urls
        
        """
        result_urls = self.exporter.export(urls)
        return result_urls