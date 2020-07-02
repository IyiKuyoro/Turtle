import requests

GOOGLE_SEARCH_ENGINE_ID = '010789377440770036764:wrpyd9iz6d8&q'

def get_search_result_by_term_and_country(key, term, country):
    try:
        global GOOGLE_SEARCH_ENGINE_ID
        url = 'https://www.googleapis.com/customsearch/v1?key={}&cx={}&q={}&cr={}'.format(key, GOOGLE_SEARCH_ENGINE_ID, term, country)
        x = requests.get(url)

        return x.json()
    except Exception:
        # ToDo Raise server error
        raise


def get_search_result_by_term(key, term):
    try:
        global GOOGLE_SEARCH_ENGINE_ID
        url = 'https://www.googleapis.com/customsearch/v1?key={}&cx={}&q={}'.format(key, GOOGLE_SEARCH_ENGINE_ID, term)
        x = requests.get(url)

        return x.json()
    except Exception:
        # ToDo Raise server error
        raise
