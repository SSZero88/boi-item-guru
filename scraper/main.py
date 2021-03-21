import re
from pprint import pprint

from bs4 import BeautifulSoup
import requests


def get_data_from_platinum_god():
    item_dict = {}
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0",
               "Accept-Encoding": "gzip, deflate",
               "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "DNT": "1",
               "Connection": "close", "Upgrade-Insecure-Requests": "1"}

    r = requests.get(
        'https://platinumgod.co.uk/',
        headers=headers)  # , proxies=proxies)
    soup = BeautifulSoup(r.content, features="html.parser")

    for d in soup.findAll('li', attrs={"class": "textbox", "data-tid": True}):
        item_name = d.find('p', attrs={"class": "item-title"}).text
        desc_lines = d.findAll('p', attrs={"class": None})
        description = " ".join([line.text.encode("ascii", "ignore").decode() for line in desc_lines])

        item_dict[item_name] = description
        # print("{}: {}".format(item_name, description))
    return item_dict


def get_data_from_wiki():
    item_dict = get_items_from_wiki()
    trinket_dict = get_trinkets_from_wiki()
    pill_dict = get_pills_from_wiki()

    all_items = {**item_dict, **trinket_dict, **pill_dict}

    return all_items


def get_items_from_wiki():
    base_url = "https://bindingofisaacrebirth.fandom.com"

    newline_removal_regex = re.compile(r"\n+")

    item_dict = {}
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0",
               "Accept-Encoding": "gzip, deflate",
               "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "DNT": "1",
               "Connection": "close", "Upgrade-Insecure-Requests": "1"}

    r = requests.get(
        'https://bindingofisaacrebirth.fandom.com/wiki/Items',
        headers=headers)  # , proxies=proxies)
    soup = BeautifulSoup(r.content, features="html.parser")

    for item_row in soup.findAll("tr", attrs={"class": "row-collectible"}):
        link = item_row.find("a", href=True)
        if link and link.get("href"):
            try:
                item_page = requests.get(
                    "{}{}".format(base_url, link.get("href")),
                    headers=headers)
                item_soup = BeautifulSoup(item_page.content, features="html.parser")

                header = item_soup.find("h1", id=["firstHeading", "section_0"])
                item_name = header.text

                effect_title = item_soup.find("span", id=["Effects", "Effect"])

                description_section = effect_title.parent.findNext("ul")

                old_descriptions = description_section.find_all("img", alt="Removed in Afterbirth †")
                [desc.parent.decompose() for desc in old_descriptions]

                desc_lines = description_section.findAll("li")

                description = " ".join([line.text.encode("ascii", "ignore").decode() for line in desc_lines])
                description = re.sub(newline_removal_regex, " ", description)

                item_dict[item_name] = description

                print(item_name)
            except Exception as e:
                print("Error occurred during item processing from {}: {}".format(link.get("href"), e))

    return item_dict


def get_trinkets_from_wiki():
    base_url = "https://bindingofisaacrebirth.fandom.com"

    newline_removal_regex = re.compile(r"\n+")

    item_dict = {}
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0",
               "Accept-Encoding": "gzip, deflate",
               "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "DNT": "1",
               "Connection": "close", "Upgrade-Insecure-Requests": "1"}

    r = requests.get(
        'https://bindingofisaacrebirth.fandom.com/wiki/Trinkets',
        headers=headers)  # , proxies=proxies)
    soup = BeautifulSoup(r.content, features="html.parser")

    for item_row in soup.findAll("tr", attrs={"class": "row-trinket"}):
        link = item_row.find("a", href=True)
        if link and link.get("href"):
            try:
                item_page = requests.get(
                    "{}{}".format(base_url, link.get("href")),
                    headers=headers)
                item_soup = BeautifulSoup(item_page.content, features="html.parser")

                header = item_soup.find("h1", id=["firstHeading", "section_0"])
                item_name = header.text

                effect_title = item_soup.find("span", id=["Effects", "Effect"])

                description_section = effect_title.parent.findNext("ul")

                old_descriptions = description_section.find_all("img", alt="Removed in Afterbirth †")
                [desc.parent.decompose() for desc in old_descriptions]

                desc_lines = description_section.findAll("li")

                description = " ".join([line.text.encode("ascii", "ignore").decode() for line in desc_lines])
                description = re.sub(newline_removal_regex, " ", description)

                item_dict[item_name] = description

                print(item_name)
            except Exception as e:
                print("Error occurred during item processing from {}: {}".format(link.get("href"), e))

    return item_dict


def get_pills_from_wiki():
    return {}


if __name__ == '__main__':
    item_dict = get_data_from_wiki()
    pprint(item_dict)
