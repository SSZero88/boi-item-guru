import re
from pprint import pprint

from bs4 import BeautifulSoup, NavigableString
import requests
import json


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


def perform_common_replacements(desc_text):
    newline_removal_regex = re.compile(r"\n+")
    multiplier_replacement_regex = re.compile(r"x(?P<first_digit>[0-9])")
    approximiation_replacement_regex = re.compile(r"~(?P<first_digit>[0-9])")
    desc_text = re.sub(newline_removal_regex, " ", desc_text)
    desc_text = multiplier_replacement_regex.sub(r"times \g<first_digit>", desc_text)
    desc_text = approximiation_replacement_regex.sub(r"around \g<first_digit>", desc_text)
    return desc_text


def get_items_from_wiki(collection_page="https://bindingofisaacrebirth.fandom.com/wiki/Items",
                        item_class="row-collectible"):
    base_url = "https://bindingofisaacrebirth.fandom.com"


    item_dict = {}
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0",
               "Accept-Encoding": "gzip, deflate",
               "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "DNT": "1",
               "Connection": "close", "Upgrade-Insecure-Requests": "1"}

    r = requests.get(
        collection_page,
        headers=headers)  # , proxies=proxies)
    soup = BeautifulSoup(r.content, features="html.parser")

    for item_row in soup.findAll("tr", attrs={"class": item_class}):
        link = item_row.find("a", href=True)
        if link and link.get("href"):
            try:
                item_page = requests.get(
                    "{}{}".format(base_url, link.get("href")),
                    headers=headers)
                item_soup = BeautifulSoup(item_page.content, features="html.parser")

                header = item_soup.find("h1", id=["firstHeading", "section_0"])
                item_name = header.text.lower()

                effect_title = item_soup.find("span", id=["Effects", "Effect"])

                effect_title_parent = effect_title.parent
                while effect_title_parent.name not in {"h2", "h3"}:
                    effect_title_parent = effect_title_parent.parent

                description_section = effect_title.parent.nextSibling

                while isinstance(description_section, NavigableString):
                    description_section = description_section.nextSibling

                # some descriptions are wrapped in divs
                if description_section.name == "div":
                    children = description_section.children
                    description_section = next(children)
                    while isinstance(description_section, NavigableString):
                        description_section = next(children)

                description_tags = []
                while description_section is not None and description_section.name in ("p", "ul"):
                    description_tags.append(description_section)
                    description_section = description_section.nextSibling
                    while isinstance(description_section, NavigableString):
                        description_section = description_section.nextSibling

                description_lines = []
                for tag in description_tags:
                    if tag.name == "p":
                        desc_text = tag.text.encode("ascii", "ignore").decode()
                        desc_text = perform_common_replacements(desc_text)
                        description_lines.append(desc_text)
                    else:

                        # Remove any lines which describe effects that have been removed
                        old_descriptions = tag.find_all("img", alt=["Removed in Afterbirth †", "Removed in Afterbirth"])
                        [desc.parent.decompose() for desc in old_descriptions]

                        desc_lines = tag.findAll("li")

                        # Remove nested list items, which are already included in text
                        for line in desc_lines:
                            for nested_li in line.findAll("li"):
                                nested_li.extract()

                        desc_text = " ".join([line.text.encode("ascii", "ignore").decode() for line in desc_lines])
                        desc_text = perform_common_replacements(desc_text)
                        description_lines.append(desc_text)

                description = "".join(description_lines)
                item_dict[item_name] = description

                print("{}\n\t- {}".format(item_name, description))
            except Exception as e:
                print("Error occurred during item processing from {}: {}".format(link.get("href"), e))

    return item_dict


def get_trinkets_from_wiki():
    return get_items_from_wiki(collection_page="https://bindingofisaacrebirth.fandom.com/wiki/Trinkets",
                               item_class="row-trinket")


def get_pills_from_wiki():
    return {}


def post_process_entries(item_dict):
    item_dict["d4"] = "Upon use, re-rolls each of Isaac's passive items into new ones. " \
                      "The game attempts to match the new item to the pool where the item " \
                      "it replaces was acquired. If the item has no pool (gained as a starting " \
                      "item, fixed drops such as a Blood Bag from a Blood Donation Machine or " \
                      "The Virus from Lust, or gained via the debug console), the Treasure Room pool is used."
    item_dict["dead sea scrolls"] = "When used, a random activated item effect will be triggered."


if __name__ == '__main__':
    item_dict = get_data_from_wiki()
    post_process_entries(item_dict)
    pprint(item_dict)
    print(json.dumps(item_dict))
