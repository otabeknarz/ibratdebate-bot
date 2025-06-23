import requests


def get_request(url: str, params: dict = None) -> requests.Response:
    return requests.get(url, params=params)


def post_request(
    url: str, data: dict, params: dict = None
) -> requests.Response:
    return requests.post(url, json=data, params=params)


def patch_request(
    url: str, data: dict, params: dict = None
) -> requests.Response:
    return requests.patch(url, json=data, params=params)
