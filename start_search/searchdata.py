"""
This module contains a list of functions for searching data on google

Returns:
    Module: Relevant google search functions
"""
import os
import requests

def get_search_result_by_term_and_country(key, term, country, num_of_results, start_at):
    """
    Searches for a term on google against a country

    Args:
        key (string): The google search api key
        term (string): The term to be searched
        country (string): The country code
        num_of_results (int): The number of result to pull in this search
        start_at (int): The page number to start from

    Returns:
        dic: A dictionary containing the google search response
    """
    try:
        google_search_engine_id = os.environ["GOOGLE_SEARCH_ENGINE_ID"]
        url = 'https://www.googleapis.com/customsearch/v1' \
              '?key={}&cx={}&q={}&cr={}&lr=lang_en&num={}&start={}'.format(
                  key, google_search_engine_id, term, country, num_of_results, start_at
              )
        google_search_response = requests.get(url)

        return google_search_response.json()
    except Exception:
        # ToDo Raise server error
        raise


def get_search_result_by_term(key, term, num_of_results, start_at):
    """Searches for a term on the web

    Args:
        key (string): The google search api key
        term (string): The term to be searched
        num_of_results (int): The number of results to pull from the search
        start_at (int): The page number to start from

    Returns:
        dic: A dictionary containing the google search response
    """
    try:
        google_search_engine_id = os.environ["GOOGLE_SEARCH_ENGINE_ID"]
        url = 'https://www.googleapis.com/customsearch/v1' \
              '?key={}&cx={}&q={}&lr=lang_en&num={}&start={}'.format(
                  key, google_search_engine_id, term, num_of_results, start_at
              )
        google_search_response = requests.get(url)

        return google_search_response.json()
    except Exception:
        # ToDo Raise server error
        raise
