# Arvottaja

This repository aims to provide a method for estimating the value of a given apartment. Currently, only houses in Finland are supported.

## Data scrapers
These live in the `/scrapers` folder. The folders are arranged by scraped website.

### oikotie-webscraper
This uses webscraper.io. Included are:
 - a config file that should work for oikotie.fi, but requires you to pass the correct number of pages for the query you want to execute
 - data from a run of Espoo and Kauniainen on 2021-04-15. The query had two additional parameters:
  - consider only apartments which own the lot they are on
  - consider only apartments which are of full-ownership type

### asuntojen-hintatiedot
This is a Python request / BeautifulSoup scraper. Usage:

#### Installation

```
pip install -r requirements.txt
```

#### Usage

##### Environment variables
`ENV`
 - if `DEBUG`, use `scrapers/asuntojen-hintatiedot/static_pages/debug.html` instead of requesting a page from the internet
  - you can replace this with your own page you want to debug
 - if `DEV`, use `scrapers/asuntojen-hintatiedot/static_pages/test.html` instead of requesting a page from the internet
 - basically both of these are implemented to reduce the load at asuntojen-hintatiedot servers. We're polite people!

Running the scraper:
```
scraper.py [-h] [--page PAGE] city

positional arguments:
  city         Which city should be parsed, capitalized. E.g. "Espoo"

optional arguments:
  -h, --help   show this help message and exit
  --page PAGE  Scrape and print data for a single page, useful for debugging
```

## Data exploration
There is a jupyter notebook in `explorations`. It currently uses the provided example data from `asuntojen-hintatiedot`. Feel free to duplicate the notebook and change in your data!

### Visualizations

#### Installation

To enable interactive plots you need to follow plotly [installation guide](https://plotly.com/python/getting-started/). Namely run 

`jupyter labextension install @jupyter-widgets/jupyterlab-manager plotlywidget@4.14.3`

after installing the requirements with pip.

