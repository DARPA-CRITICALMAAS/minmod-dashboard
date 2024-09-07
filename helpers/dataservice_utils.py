import requests
from constants import API_ENDPOINT


def fetch_api_data(path, ssl_flag):
    """
    Fetches and returns data from the API

    :param url: str - URL to the API
    :param ssl_flag: bool - boolean to enable SSL auth
    :return: dict - Parsed JSON data from the API
    """
    try:
        response = requests.get(API_ENDPOINT + path, verify=ssl_flag)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx and 5xx)
        return response.json()  # Parse and return JSON response
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"An error occurred: {err}")


if __name__ == "__main__":
    swagger_url = API_ENDPOINT + "/mineral_site_grade_and_tonnage/zinc"
    swagger_data = fetch_api_data(swagger_url, False)
    print(swagger_data)
