# Design Document

## Overview

This document will discuss the high-level design, modularization, interactions between modules, and reasonings on design choices of the Housing Market Monitoring System.

The core of the Housing Market Monitoring System are:

1. Web scrapers which continuously collect housing listings from Craigslist, where each scraper focus on one subsite (e.g. orangecounty.craigslist.org).

1. Duplicates elimination services

1. Geotagging services

1. Analytical services

1. A database that stores all the listings and the analytical results for each subsite

1. A map based visuliazation application

## Main use cases

* Visualize (mediam, average...) housing prices of different regions

* Display newest listings in a particular region

* (Future) Display pricing history

* (Future) Notify users about new listings

* (Future) Predict price changes

## High level design diagram

![High Level Design Diagram](high-level-design-diagram.png "High Level Design Diagram")

## Detailed design

### Modules Design Web Servers

![modules-design-web-servers](modules-design-web-servers.png "modules-design-web-servers")

Stack | Reason
--- | ---
Leaflet | 1. Open source, plenty of plugins, good documentation 2. Offering the same performance and functionality compared to its main competitor, Google Maps JavaScript API ([see comparisons here](https://www.codementor.io/victorgerardtemprano/google-maps-api-or-leaflet--what-s-best-for-your-project-faaev60vm)).
Angular | 1. Angular is a complete frontend MVC framework, which is better than React at handling complex logic. 2. Frontend's logic can become very complex when the size of the dataset grows larger and larger.
Node.js | 1. The web server is heavy at I/O operations (reading database) rather than computation 2. Node excels at contructing a non-blocking server with little resources using its single thread event loop structure 3. JavaScript, same as the language used in the client side app

* UI example 1: average prices of all the markets (Regions are shaded in propotion to the measurement of the statistical variables)

![ui-design-choropleth-map](ui-design-choropleth-map.png "ui-design-choropleth-map")

* UI example 2: new listings in one selected region

![ui-design-markers](ui-design-markers.png "ui-design-markers")

### Modules Design Backend Servers

![modules-design-backend-servers](modules-design-backend-servers.png "modules-design-backend-servers")


## Future work

