# This is a template for a Python scraper on morph.io (https://morph.io)
# including some code snippets below that you should find helpful

# import scraperwiki
import lxml.html
import requests
import scraperwiki
import sqlite3
import json
from datetime import datetime

#
# # Read in a page
# html = scraperwiki.scrape("http://foo.com")
#
# # Find something on the page using css selectors
# root = lxml.html.fromstring(html)
# root.cssselect("div[align='left']")
#
# # Write out to the sqlite database using scraperwiki library
# scraperwiki.sqlite.save(unique_keys=['name'], data={"name": "susan", "occupation": "software developer"})
#
# # An arbitrary query against the database
# scraperwiki.sql.select("* from data where 'name'='peter'")

# You don't have to do things with the ScraperWiki and lxml libraries.
# You can use whatever libraries you want: https://morph.io/documentation/python
# All that matters is that your final data is written to an SQLite database
# called "data.sqlite" in the current working directory which has at least a table
# called "data".

products = [x['label'] for x in json.load(open('products.json'))['products']]

print products

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.71 Safari/537.36',
}

urls = {
    'recent': 'http://www.microsoft.com/en-us/server-cloud/roadmap/recently-available.aspx',
    'preview': 'http://www.microsoft.com/en-us/server-cloud/roadmap/public-preview.aspx',
    'development': 'http://www.microsoft.com/en-us/server-cloud/roadmap/Indevelopment.aspx',
    'cancelled': 'http://www.microsoft.com/en-us/server-cloud/roadmap/cancelled.aspx',
}

for state, url in urls.items():
    print
    print url

    resp = requests.get(url, headers=headers)

    tree = lxml.html.fromstring(resp.text)

    titles = [x for x in tree.xpath('//section//h5[contains(@class, "accordionHeader")]')]
    texts = [x for x in tree.xpath('//section//div[contains(@class, "accordionLeftSection")]')]

    for title_e, text_e in zip(titles, texts):
        section = title_e.getparent().getparent().getparent().attrib['id'].split('-')[1]

        title = title_e.text.strip()
        text = text_e.text_content().strip()

        thing_products = []
        for product in products:
            if product in title_e.attrib['class']:
                thing_products.append(product)

        print thing_products

        if title == 'No items available':
            continue

        print title
        
        now = datetime.now()
        
        try:
            exists = scraperwiki.sqlite.select("* from data where title=?", [title])
        except sqlite3.OperationalError:
            exists = []

        if len(exists) > 0:
            doc = exists[0]
        else:
            doc = {
                'title': title,
            }

            for section2 in urls.keys():
                doc[state] = None

        doc['section'] = section
        doc['products'] = ", ".join(thing_products)
        
        scraperwiki.sqlite.save(unique_keys=['title'], data=doc)

        if state not in doc or doc[state] is None:
            print "Updating" 
            doc[state] = now

            scraperwiki.sqlite.save(unique_keys=['title'], data=doc)
        else:
            print "Not updating"
 
