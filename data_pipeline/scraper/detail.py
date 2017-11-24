# -*- coding: utf-8 -*-

"""A class for scraping details from the details page"""

import logging
import re
import pprint

from bs4.element import Tag
from six.moves import range

from base import BaseScraper


class DetailScraper(BaseScraper):
    """A class for scraping details from the details page"""

    def __init__(self, url=None, region=None, category=None):
        self.logger = logging.getLogger(__name__)
        if url is None or region is None or category is None:
            msg = "Incomplete information: url=%s, region=%s, category=%s" % (
                url, region, category)
            self.logger.error(msg)
            raise ValueError(msg)

        self.url = url
        self.region = region
        self.category = category

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
        price = price_ele.text.strip() if price_ele and price_ele.text else ""

        title_ele = soup.find("span", {"id": "titletextonly"})
        title = title_ele.text.strip() if title_ele and title_ele.text else ""

        geo_ele = soup.find("div", {"id": "map"})
        geo = {}
        if geo_ele and geo_ele.attrs.get("data-latitude") and geo_ele.attrs.get("data-longitude"):
            lat = geo_ele.attrs.get("data-latitude").strip()
            lon = geo_ele.attrs.get("data-longitude").strip()
            if lat != "" and lon != "":
                geo = {"latitude": lat, "longitude": lon}

        info_eles = soup.find("div", {"class": "postinginfos"})
        craigslist_id = ""
        post_datetime = ""
        update_datetime = ""
        if info_eles:
            craigslist_id = self.__parse_id(
                unicode(info_eles.find(string=re.compile(".*post id:.*"))))
            for info_ele in info_eles:
                if isinstance(info_ele, Tag):
                    time_ele = info_ele.find("time", {"class": "date"})
                    if time_ele:
                        for text in info_ele.stripped_strings:
                            if text.find("posted") != -1:
                                if time_ele.attrs.get("datetime"):
                                    post_datetime = time_ele.attrs.get(
                                        "datetime").strip()
                                break
                            elif text.find("updated") != -1:
                                if time_ele.attrs.get("datetime"):
                                    update_datetime = time_ele.attrs.get(
                                        "datetime").strip()
                                break
        else:
            self.logger.debug("Unable to find postinginfos url=%s. Returning None... Skipping...", self.url)
            return None

        city_ele = soup.find("span", {"class": "postingtitletext"})
        city = ""
        if city_ele:
            small_ele = city_ele.find("small")
            if small_ele and small_ele.text:
                city = small_ele.text.strip()

        street_ele = soup.find("div", {"class": "mapbox"})
        street = ""
        if street_ele:
            addr_ele = street_ele.find("div", {"class": "mapaddress"})
            if addr_ele and addr_ele.text:
                street = addr_ele.text.strip()

        gallery_ele = soup.find("div", {"class": "gallery"})
        img_url = ""
        if gallery_ele:
            img_ele = gallery_ele.find("img")
            if img_ele and img_ele.attrs.get("src"):
                img_url = img_ele.attrs.get("src").strip()

        bubble_eles = soup.find_all("span", {"class": "shared-line-bubble"})
        bed = ""
        bath = ""
        size = ""
        available_date = ""
        if bubble_eles:
            for bubble_ele in bubble_eles:
                if isinstance(bubble_ele, Tag):
                    if bubble_ele.attrs.get("data-date"):
                        available_date = bubble_ele.attrs.get("data-date").strip()
                    else:
                        for text in bubble_ele.stripped_strings:
                            if text == "/":
                                try:
                                    bed = bubble_ele.contents[0].string.strip()
                                    bath = bubble_ele.contents[2].string.strip()
                                    break
                                except (IndexError, AttributeError):
                                    self.logger.warning(
                                        "Unable to parse bed & bath, bubble_ele=%s", bubble_ele)
                            elif text == "ft":
                                try:
                                    size = bubble_ele.contents[0].string.strip(
                                    ) + "ft2"
                                    break
                                except (IndexError, AttributeError):
                                    self.logger.warning(
                                        "Unable to parse size, bubble_ele=%s", bubble_ele)

        attrgroup_eles = soup.find_all("p", {"class": "attrgroup"})
        open_house_dates = []
        features = []
        if attrgroup_eles:
            for attrgroup_ele in attrgroup_eles:
                if isinstance(attrgroup_ele, Tag) and attrgroup_ele.find("span", {"class": "shared-line-bubble"}) is None:
                    for text in attrgroup_ele.stripped_strings:
                        if text == "open house dates":
                            open_house_dates = [
                                date for date in attrgroup_ele.stripped_strings][1:]
                            break
                    features = [
                        feature for feature in attrgroup_ele.stripped_strings]

        body_ele = soup.find("section", {"id": "postingbody"})
        body = []
        if body_ele:
            body = [line for line in body_ele.stripped_strings]

        result = {"region": self.region,
                  "category": self.category,
                  "url": self.url,
                  "price": price,
                  "title": title,
                  "geo": geo,
                  "craigslist_id": craigslist_id,
                  "post_datetime": post_datetime,
                  "update_datetime": update_datetime,
                  "city": city,
                  "street": street,
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
