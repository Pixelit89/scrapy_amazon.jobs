# -*- coding: utf-8 -*-

from scrapy.spiders import CrawlSpider, Rule
from scrapy import Request
from scrapy_splash import SplashRequest
from ..items import ScrapeAmazonJobsItem, ScrapeAmazonJobsList
from urllib.parse import urljoin


class AmazonJobsSpider(CrawlSpider):
    name = 'amazon_jobs'
    allowed_domains = ['amazon.jobs']
    start_urls = ['https://www.amazon.jobs/en/job_categories/']

    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url, self.parse, args={'wait': 0.5})

    def parse(self, response):
        item = ScrapeAmazonJobsList()
        item['list_of_cat'] = response.xpath('//div[@class="tiles"]/div/a/div/div[1]/h2/text()').extract()
        cat_links = response.xpath('//div[@class="tiles"]/div/a/@href').extract()
        for link in cat_links:
            yield Request(urljoin(response.url, link), callback=self.get_full_list, )

    def get_full_list(self, response):
        count = int(response.xpath('//div[@id="job-category"]/div/div/div/div[2]/text()').extract_first())
        url = response.url.split('?')[0]
        params = '?job_count={0}'.format(count+2)
        wait = 50 if (count/10 > 60) else count/10
        yield SplashRequest('{}{}'.format(url, params), self.parse_jobs, args={'wait': wait, 'timeout': 60})

    def parse_jobs(self, response):
        job_links = response.xpath('//a[contains(@href, "/en/jobs/")]/@href').extract()
        for job_link in job_links:
            job_link = job_link
            yield Request(urljoin(response.url, job_link), callback=self.parse_job_text)

    def parse_job_text(self, response):
        item = ScrapeAmazonJobsItem()
        item['job_link'] = response.url
        item['job_title'] = response.xpath('//div[@id="job-detail"]/div[@class="header"]/div/div/div[1]/div/h1/text()').extract_first()
        item['job_description'] = response.xpath('//div[@id="job-detail"]/div[@class="container"]/div[@class="row"]/div[1]/div/div[1]/p/text()').extract_first()
        yield item


