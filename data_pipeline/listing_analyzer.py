# -*- coding: utf-8 -*-

"""A quick and dirty way to analyze on listings hiden in the log"""

import ast
import json

# # 1. extract listings from log file
count = 0
with open("listing_fetcher.log", "rb") as f:
    with open("listings.log", "wb") as out:
        for line in f.readlines():
            if line:
                idx = line.rfind("cloudamqp    INFO      [x] Sent ")
                if idx != -1:
                    idx += len("cloudamqp    INFO      [x] Sent ")
                    # print line[idx: -35]
                    listing = ast.literal_eval(line[idx: -35])
                    out.write(json.dumps(listing) + "\n")
                    count += 1
print "written %s" % str(count)

# 2. analyze
same_titles, same_prices, same_sizes, same_ids, same_urls, same_img_urls, same_geos, same_streets = {}, {}, {}, {}, {}, {}, {}, {}
collections = (same_titles, same_prices, same_sizes, same_ids, same_urls, same_img_urls, same_geos, same_streets)
keys = ("title", "price", "size", "craigslist_id", "url", "img_url", "geo", "street")
with open("listings.log", "rb") as f:
    for line in f.readlines():
        if line:
            listing = json.loads(line)
            for i in range(8):
                collection = collections[i]
                key = listing[keys[i]]
                if isinstance(key, dict):
                    key = str(key).encode("utf-8")
                else:
                    key = key.encode("utf-8")
                if collection.get(key) is not None:
                    collection.get(key)["count"] += 1
                    collection.get(key)["listings"].append(listing)
                else:
                    collection[key] = {"count": 1, "listings": [listing]}

for i in range(8):
    with open("same_" + keys[i] + ".log", "wb") as out:
        collection = collections[i]
        for key in collection:
            out.write("key=" + key + ", value=" + json.dumps(collection[key]) + "\n")


# 3. empty geo problem
same_geo = None
with open("same_geo.log", "rb") as f:
    for line in f.readlines():
        if line:
            if line.startswith("key={},"):
                idx = line.find("key={}, value=") + len("key={}, value=")
                same_geo = json.loads(line[idx:])
no_streets = 0
if same_geo:
    for listing in same_geo["listings"]:
        if listing["street"] is None or listing["street"] == "":
            no_streets += 1
print "listings with no geo=%s, among them listings with no streets=%s" % (same_geo["count"], no_streets)


# 4. available_date problem
no_available_date_count = 0
with open("listings.log", "rb") as f:
    for line in f.readlines():
        if line:
            listing = json.loads(line)
            if listing["available_date"] is None or listing["available_date"] == "":
                no_available_date_count += 1
print "no_available_date_count=%s" % no_available_date_count