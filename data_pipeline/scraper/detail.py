# -*- coding: utf-8 -*-

"""A class for scraping details from the details page"""

import logging
import re
import pprint

from bs4.element import Tag
from dateutil import parser
from six.moves import range

from base import BaseScraper

class DetailScraper(BaseScraper):
    """A class for scraping details from the details page"""

    def __init__(self, url=None, region=None, category=None):
        self.logger = logging.getLogger(__name__)
        if url is None or region is None or category is None:
            msg = "Incomplete information: url=%s, region=%s, category=%s" % (url, region, category)
            self.logger.error(msg)
            raise ValueError(msg)

        self.url = url
        self.region = region
        self.category = category

    def __parse_price(self, price_ele):
        """parse price element --> int"""

        if price_ele:
            inner_html = price_ele.text.strip()
            self.logger.debug("price_ele: inner_html=%s", inner_html)
            try:
                for i in range(len(inner_html)):
                    if inner_html[i].isdigit():
                        number = inner_html[i:]
                        return int(number) if number.isdigit() else int(float(number))
            except ValueError:
                pass
        msg = "Unable to parse a useful price"
        self.logger.warning(msg)
        raise ValueError(msg)

    def __parse_id(self, text):
        """remove strs other than ID"""

        for i in range(len(text)):
            if text[i].isdigit():
                return text[i:]
        return ""

    def get_details(self):
        """Get all details from the given details page"""

        soup = self._get_soup(url=self.url, logger=self.logger)

        price_ele = soup.find("span", {"class": "price"})
        try:
            price = self.__parse_price(price_ele)
        except ValueError:
            return None

        title_ele = soup.find("span", {"id": "titletextonly"})
        title = title_ele.text if title_ele else ""

        geo_ele = soup.find("div", {"id": "map"})
        geo = {"latitude": geo_ele.attrs.get("data-latitude"),
               "longitude": geo_ele.attrs.get("data-longitude")} if geo_ele else {}

        info_eles = soup.find("div", {"class": "postinginfos"})
        craigslist_id = self.__parse_id(unicode(info_eles.find(string=re.compile(".*post id:.*"))))
        post_datetime = None
        update_datetime = None
        for info_ele in info_eles:
            if isinstance(info_ele, Tag):
                for text in info_ele.stripped_strings:
                    if text.find("posted") != -1:
                        try:
                            post_datetime = parser.parse(info_ele.find("time", {"class": "date"}).attrs.get("datetime"))
                        except (ValueError, OverflowError):
                            self.logger.warning("Unable to parse post datetime=%s", info_ele.find("time", {"class": "date"}).attrs.get("datetime"))
                        break
                    elif text.find("updated") != -1:
                        try:
                            update_datetime = parser.parse(info_ele.find("time", {"class": "date"}).attrs.get("datetime"))
                        except (ValueError, OverflowError):
                            self.logger.warning("Unable to parse update datetime=%s", info_ele.find("time", {"class": "date"}).attrs.get("datetime"))
                        break

        city_ele = soup.find("span", {"class": "postingtitletext"})
        city = ""
        if city_ele:
            small_ele = city_ele.find("small")
            if small_ele:
                city = small_ele.text

        street_ele = soup.find("div", {"class": "mapbox"})
        street = ""
        if street_ele:
            addr_ele = street_ele.find("div", {"class": "mapaddress"})
            if addr_ele:
                street = addr_ele.text

        gallery_ele = soup.find("div", {"class": "gallery"})
        img_url = ""
        if gallery_ele:
            img_ele = gallery_ele.find("img")
            if img_ele:
                img_url = img_ele.attrs.get("src")

        bubble_eles = soup.find_all("span", {"class": "shared-line-bubble"})
        bed = ""
        bath = ""
        size = ""
        available_date = None
        for bubble_ele in bubble_eles:
            if isinstance(bubble_ele, Tag):
                if bubble_ele.attrs.get("data-date") is not None:
                    try:
                        available_date = parser.parse(bubble_ele.attrs.get("data-date"))
                    except (ValueError, OverflowError):
                        self.logger.warning("Unable to parse available date=%s", bubble_ele.attrs.get("data-date"))
                else:
                    for text in bubble_ele.stripped_strings:
                        if text == "/":
                            try:
                                bed = bubble_ele.contents[0].string.strip()
                                bath = bubble_ele.contents[2].string.strip()
                                break
                            except (IndexError, AttributeError):
                                self.logger.warning("Unable to parse bed & bath, bubble_ele=%s", bubble_ele)
                        elif text == "ft":
                            try:
                                size = bubble_ele.contents[0].string.strip() + "ft2"
                                break
                            except (IndexError, AttributeError):
                                self.logger.warning("Unable to parse size, bubble_ele=%s", bubble_ele)

        attrgroup_eles = soup.find_all("p", {"class": "attrgroup"})
        open_house_dates = []
        features = []
        for attrgroup_ele in attrgroup_eles:
            if isinstance(attrgroup_ele, Tag) and attrgroup_ele.find("span", {"class": "shared-line-bubble"}) is None:
                for text in attrgroup_ele.stripped_strings:
                    if text == "open house dates":
                        open_house_dates = [date for date in attrgroup_ele.stripped_strings][1:]
                        break
                features = [feature for feature in attrgroup_ele.stripped_strings]
        
        body_ele = soup.find("section", {"id": "postingbody"})
        body = [line for line in body_ele.stripped_strings]

        result = {"price": price,
                  "title": title,
                  "geo": geo,
                  "craigslist_id": craigslist_id,
                  "post_datetime": post_datetime,
                  "update_datetime": update_datetime,
                  "city": city,
                  "street": street,
                  "region": self.region,
                  "category": self.category,
                  "url": self.url,
                  "img_url": img_url,
                  "bed": bed,
                  "bath": bath,
                  "size": size,
                  "available_date": available_date,
                  "open_house_dates": open_house_dates,
                  "features": features,
                  "body": body}
        self.logger.debug("Returning detail=%s", pprint.pformat(result))
        return result
