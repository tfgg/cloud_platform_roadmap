# This is a template for a Python scraper on morph.io (https://morph.io)
# including some code snippets below that you should find helpful

# import scraperwiki
import lxml.html
import requests
import scraperwiki
import sqlite3
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

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.71 Safari/537.36',
}

urls = {
    'recent': 'http://www.microsoft.com/en-us/server-cloud/roadmap/recently-available.aspx',
    'preview': 'http://www.microsoft.com/en-us/server-cloud/roadmap/public-preview.aspx',
    'development': 'http://www.microsoft.com/en-us/server-cloud/roadmap/Indevelopment.aspx',
    'cancelled': 'http://www.microsoft.com/en-us/server-cloud/roadmap/cancelled.aspx',
}

for section, url in urls.items():
    print
    print url

    resp = requests.get(url, headers=headers)

    tree = lxml.html.fromstring(resp.text)

    titles = [x.text.strip() for x in tree.xpath('//section[@id="stbTabPanel-Cloudinfrastructure"]//h5[contains(@class, "accordionHeader")]')]
    texts = [x.text_content().strip() for x in tree.xpath('//section[@id="stbTabPanel-Cloudinfrastructure"]//div[contains(@class, "accordionLeftSection")]')]

    for title, text in zip(titles, texts):
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
                doc[section2] = None

        if section not in doc or doc[section] is None:
            print "Updating" 
            doc[section] = now

            scraperwiki.sqlite.save(unique_keys=['title'], data=doc)
        else:
            print "Not updating"
 
