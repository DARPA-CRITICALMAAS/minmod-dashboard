import requests
from constants import API_ENDPOINT
import aiohttp
import asyncio
import time
from logger_config import logger


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


# Decorator to log runtime using Python's logging
def log_async_runtime(func):
    """
    A decorator to log the runtime of a function using Python logging.
    """

    async def wrapper(*args, **kwargs):
        start_time = time.time()  # Start timer
        result = await func(*args, **kwargs)  # Execute the asynchronous function
        elapsed_time = time.time() - start_time  # Calculate elapsed time
        logger.info(
            f"Function '{func.__name__}' args : {args[1]} executed in {elapsed_time:.2f} seconds"
        )
        return result

    return wrapper


# Async function to fetch JSON data with timing
@log_async_runtime
async def fetch_json(session, url):
    async with session.get(url) as response:
        response.raise_for_status()
        return await response.json()


# Async function to fetch data from all URLs
async def fetch_all(urls):
    urls = [API_ENDPOINT + url_path for url_path in urls]
    connector = aiohttp.TCPConnector(ssl=False)  # Disable SSL verification
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [fetch_json(session, url) for url in urls]
        return await asyncio.gather(*tasks)


if __name__ == "__main__":
    swagger_url = API_ENDPOINT + "/mineral_site_grade_and_tonnage/zinc"
    swagger_data = fetch_api_data(swagger_url, False)
    print(swagger_data)
