# -*- coding: utf-8 -*-

from scrapy.spiders import CrawlSpider, Rule
from scrapy import Request
from scrapy_splash import SplashRequest
from ..items import ScrapeAmazonJobsItem, ScrapeAmazonJobsList
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urljoin
from time import sleep


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
        # yield Request(urljoin(response.url, cat_links[0]), callback=self.get_full_list)

    def get_full_list(self, response):
        count = response.xpath('//div[@id="job-category"]/div/div/div/div[2]/text()').extract_first()
        url = response.url.split('?')[0]
        params = '?job_count={0}'.format(int(count)+2)
        yield Request('{}{}'.format(url, params), callback=self.parse_jobs)

    def parse_jobs(self, response):
        item = ScrapeAmazonJobsItem()
        driver = webdriver.Firefox()
        driver.get(response.url)
        WebDriverWait(driver, 300).until(
            EC.presence_of_element_located((By.XPATH, '//div[@id="search-results"]/div/div[2]')))
        job_links = driver.find_elements_by_xpath('//a[contains(@href, "/en/jobs/")]')
        print(len(job_links))
        for job_link in job_links:
            job_link = job_link.get_attribute('href')
            yield Request(job_link, callback=self.parse_job_text)

    def parse_job_text(self, response):
        item = ScrapeAmazonJobsItem()
        item['job_link'] = response.url
        item['job_title'] = response.xpath('//div[@id="job-detail"]/div[@class="header"]/div/div/div[1]/div/h1/text()').extract_first()
        item['job_description'] = response.xpath('//div[@id="job-detail"]/div[@class="container"]/div[@class="row"]/div[1]/div/div[1]/p/text()').extract_first()
        yield item


