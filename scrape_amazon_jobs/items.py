# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ScrapeAmazonJobsItem(scrapy.Item):
    # define the fields for your item here like:
    job_link = scrapy.Field()
    job_title = scrapy.Field()
    job_description = scrapy.Field()
    pass

class ScrapeAmazonJobsList(scrapy.Item):
    list_of_cat = scrapy.Field()
