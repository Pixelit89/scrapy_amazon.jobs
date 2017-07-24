# -*- coding: utf-8 -*-

from scrapy.spiders import CrawlSpider, Rule
from scrapy import Request
from scrapy.linkextractors import LinkExtractor
from scrapy_splash import SplashRequest
from ..items import ScrapeAmazonJobsItem, ScrapeAmazonJobsList
from urllib.parse import urljoin
import requests, json
import re


class AmazonJobsSpider(CrawlSpider):
    name = 'amazon_jobs'
    allowed_domains = ['amazon.jobs']
    start_urls = ['https://www.amazon.jobs/en/job_categories/']

    rules = [
        Rule(LinkExtractor(allow=('/en/job_categories/')), callback='job_list', follow=True)
    ]

    def parse(self, response):
        raw_str = response.xpath('//div[@id="job-categories"]/div[2]/div/div/@data-react-props').extract_first()
        extracted_links = re.findall('/en/job_categories/\S+\"}', raw_str)
        fixed_links = map(lambda x: x[:-2], extracted_links)
        for link in fixed_links:
            yield Request(urljoin(response.url, link), callback=self.job_list)
        # yield Request(urljoin(response.url, list(fixed_links)[0]), callback=self.job_list)

    def job_list(self, response):
        count = int(response.xpath('//div[@id="job-category"]/div/div/div/div[2]/text()').extract_first())
        print(response.url)
        base, cat = response.url.split('job_categories/')
        params = 'search?result_limit={0}&category%5B%5D={1}'.format(count, cat)
        html = requests.get('{0}{1}'.format(base, params), headers={
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
            })
        response_dict = html.json()
        for job in response_dict['jobs']:
            item = ScrapeAmazonJobsItem()
            item['job_description'] = job['description'].replace('<br/>·', '')
            item['job_link'] = job['job_path']
            item['job_title'] = job['title']
            yield item