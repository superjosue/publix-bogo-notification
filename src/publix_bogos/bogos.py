from dataclasses import dataclass
from enum import Enum

import requests
from bs4 import BeautifulSoup, ResultSet

from publix_bogos.utils import is_any_in_text


class BogoType(Enum):
    NOBOGO = ''
    BOGO = 'BOGO'
    B2G1 = 'B2G1'


@dataclass(slots=True)
class BogoItem:
    """Container for a single BOGO item."""

    name: str
    effective_dates: str
    type: BogoType


bogo_compare_text = [
    'buy 1 get 1 free',
    'buy one get one free',
    'buy one get 1 free',
    'buy 1 get one free',
]

b2g1_compare_text = [
    'buy 2 get 1 free',
    'buy two get one free',
    'buy 2 get one free',
    'buy two get 1 free',
]


def retrieve_sales_webpage(url: str) -> BeautifulSoup:
    """Retrieve sales webpage context as an BeautifulSoup object.

    Args:
        url (str): URL for retrieving the sales content

    Raises:
        Exception: Unsuccessful status code returned
        Exception: No content was retrieved for the given URL

    Returns:
        BeautifulSoup: BeautifulSoup object containing the webpage content
    """
    response = requests.get(url, timeout=5)
    response.raise_for_status()

    if not response.content:
        raise ValueError("No content returned")

    return BeautifulSoup(response.content, "html.parser")


def parse_webpage_bogos(webpage_content: BeautifulSoup) -> list[BogoItem]:
    """Parse webpage content (BeautifulSoup) to find and return bogo items.

    Returns:
        list[BogoItem]]: List of bogo items
    """
    bogo_items: list[BogoItem] = []

    for item in webpage_content.find_all("div", class_="theTileContainer"):
        deal_div = item.find("div", class_="deal")
        if not deal_div:
            continue

        sale_text = deal_div.find("span", class_="ellipsis_text").text
        bogo_type = get_bogo_type(sale_text)
        if bogo_type == BogoType.NOBOGO:
            continue

        item_name = item.find("div", class_="title").find(
            "h2", class_="ellipsis_text"
        ).text
        effective_dates = item.find("div", class_="validDates").find("span").text
        bogo_items.append(BogoItem(item_name, effective_dates, bogo_type))

    return bogo_items


def get_bogo_type(item_sale_text: str) -> BogoType:
    """Determine if sales text is a BOGO type sale or not.

    Args:
        item_sale_text (str): text to parse for BOGO type

    Returns:
        BogoType: BOGO type
    """
    if is_bogo(item_sale_text):
        return BogoType.BOGO
    if is_b2g1(item_sale_text):
        return BogoType.B2G1
    return BogoType.NOBOGO


def is_bogo(item_sale_text: str) -> bool:
    """Determine if the sales text is for a BOGO sale.

    Args:
        item_sale_text (str): text to parse for BOGO

    Returns:
        bool: True if text is considered BOGO otherwise False
    """
    return is_any_in_text(item_sale_text, bogo_compare_text)


def is_b2g1(item_sale_text: str) -> bool:
    """Determine if the sales text is for a B2G1 sale.

    Args:
        item_sale_text (str): text to parse for B2G1

    Returns:
        bool: True if text is considered B2G1 otherwise False
    """
    return is_any_in_text(item_sale_text, b2g1_compare_text)
