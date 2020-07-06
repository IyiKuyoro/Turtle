"""
This module contains a list of functions for searching data on google

Returns:
    Module: Relevant google search functions
"""
import os
import requests


def get_search_result_by_term(key, term, num_of_results, start_at, excluded_sites, country=''):
    """Searches for a term on the web

    Args:
        key (string): The google search api key
        term (string): The term to be searched
        num_of_results (int): The number of results to pull from the search
        start_at (int): The page number to start from
        excluded_sites (list): List of sites not to include in results

    Returns:
        dic: A dictionary containing the google search response
    """
    excluded_sites = '+'.join(excluded_sites)
    technical_term = term.split(' ')
    google_search_engine_id = os.environ["GOOGLE_SEARCH_ENGINE_ID"]
    url = 'https://www.googleapis.com/customsearch/v1' \
            '?key={key}&cx={cx}&q={q}&lr=lang_en&num={num}&start={start}' \
            '&exactTerms={exact_terms}&safe={safe}&siteSearch={site_search}' \
            '&siteSearchFilter={site_search_filter}' \
            '&dateRestrict={date_restricted}'.format(
                key=key, cx=google_search_engine_id,
                q=term, num=num_of_results, start=start_at,
                exact_terms=technical_term[0], safe='ACTIVE',
                site_search=excluded_sites, site_search_filter='e',
                date_restricted='m6'
            )
    if country == '':
        url += '&cr={country}'.format(country=country)

    google_search_response = requests.get(url)

    if google_search_response.status_code != 200:
        raise Exception('Error on google search', google_search_response.json())

    return google_search_response.json()
