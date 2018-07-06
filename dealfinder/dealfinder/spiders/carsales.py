# -*- coding: utf-8 -*-
import re
import scrapy
from scrapy.selector import Selector

from dealfinder.items import DealFinderItem

class CarsalesSpider(scrapy.Spider):
    name = 'carsales'
    allowed_domains = ['carsales.com.au']
    start_urls = [
        'https://www.carsales.com.au/cars/results?limit=24&offset=0&setype=pagination&q=%28And.State.New%20South%20Wales._.BodyStyle.SUV._.Service.Carsales._.Price.range%280..20000%29._.Year.range%282013..%29._.Odometer.range%280..60000%29._.EngineSize.range%281500..2000%29.%29&sortby=~Price&offset=0&area=Stock&vertical=car&WT.z_srchsrcx=makemodel',
        'https://www.carsales.com.au/cars/results?limit=24&offset=24&setype=pagination&q=%28And.State.New%20South%20Wales._.BodyStyle.SUV._.Service.Carsales._.Price.range%280..20000%29._.Year.range%282013..%29._.Odometer.range%280..60000%29._.EngineSize.range%281500..2000%29.%29&sortby=~Price&offset=0&area=Stock&vertical=car&WT.z_srchsrcx=makemodel',
        'https://www.carsales.com.au/cars/results?limit=24&offset=48&setype=pagination&q=%28And.State.New%20South%20Wales._.BodyStyle.SUV._.Service.Carsales._.Price.range%280..20000%29._.Year.range%282013..%29._.Odometer.range%280..60000%29._.EngineSize.range%281500..2000%29.%29&sortby=~Price&offset=0&area=Stock&vertical=car&WT.z_srchsrcx=makemodel',
        'https://www.carsales.com.au/cars/results?limit=24&offset=72&setype=pagination&q=%28And.State.New%20South%20Wales._.BodyStyle.SUV._.Service.Carsales._.Price.range%280..20000%29._.Year.range%282013..%29._.Odometer.range%280..60000%29._.EngineSize.range%281500..2000%29.%29&sortby=~Price&offset=0&area=Stock&vertical=car&WT.z_srchsrcx=makemodel',
    ]

    def parse(self, response):
        listings = Selector(response).xpath('//div[contains(@class,"listing-item")]')
    
        for listing in listings:
            item = DealFinderItem()
            #item['listing'] = listing.extract()
            item['title'] = listing.css('div.title a h2 ::text').extract()[0].strip()
            item['url'] = listing.css('div.title a').xpath('@href').extract()[0]
            item['id'] = listing.css('div.title a').xpath('@href').re_first(r'/dealer/details/(.*)/\?')
            item['year'] = self.get_year(item['title'])
            item['make'] = self.get_make(item['title'])
            item['model'] = self.get_model(item['title'])
            item['transmission'] = self.get_transmission(item['title'])
            item['manufacturer_marketing_year'] = self.get_manufacturer_marketing_year(item['title'])
            item['price'] = self.parse_price(listing.css('div.price ::text').extract()[0])
            item['odometer'] = self.parse_odometer(
                self.extract_odometer(listing.css('div.feature-text ::text').extract()))
            engine_details = self.extract_engine_details(
                listing.css('.feature-text ::text').extract()
            )
            item['engine_capacity'] = self.get_engine_capacity(engine_details)
            item['fuel_type'] = self.get_fuel_type(engine_details)
            item['n_cylinders'] = self.get_n_cylinders(engine_details)
            item['drive_type'] = self.get_drive_type(item['title'])
            yield item


    @staticmethod
    def get_drive_type(title):
        m = re.search(r'(2WD|AWD|4WD)', title)
        if m:
            return m.groups()[0]

    @staticmethod
    def get_n_cylinders(engine_details):
        m = re.search(r'(\d)cyl', engine_details)
        if m:
            return m.groups()[0]

    @staticmethod
    def get_fuel_type(engine_details):
        m = re.search(r'(Petrol|Diesel)', engine_details)
        if m:
            return m.groups()[0]

    @staticmethod
    def get_engine_capacity(engine_details):
        m = re.search(r'(\d\.{0,1}\d{0,1})L', engine_details)
        if m:
            return m.groups()[0]

    @staticmethod
    def extract_engine_details(feature_texts):
        for feature_text in feature_texts:
            if ('cyl' in feature_text
                and 'L' in feature_text
                and ('Petrol' in feature_text or 'Diesel' in feature_text)):
                return feature_text

    @staticmethod
    def extract_odometer(feature_texts):
        for feature_text in feature_texts:
            if 'km' in feature_text:
                return feature_text.strip().replace(',', '')
    
    @staticmethod
    def parse_odometer(odometer_string):
        return odometer_string.replace('km', '').strip() 

    @staticmethod
    def parse_price(price_string):
        return price_string.replace('$','').replace(',', '').replace('*', '')

    @staticmethod
    def get_year(title):
        m = re.match(r'^\w*(\d{4})\s', title)
        if m:
            return m.groups()[0]

    @staticmethod
    def get_make(title):
        m = re.match(r'^\w*\d{4}\s(\w*)\s', title)
        if m:
            return m.groups()[0]

    @staticmethod
    def get_model(title):
        m = re.match(r'^\w*\d{4}\s\w+\s(.+)(Manual|Auto)', title)
        if m:
            return m.groups()[0].strip()

    @staticmethod
    def get_transmission(title):
        m = re.search(r'(Manual|Auto)', title)
        if m:
            return m.groups()[0]

    @staticmethod
    def get_manufacturer_marketing_year(title):
        m = re.search(r'(MY\d{2})', title)
        if m:
            return m.groups()[0]

import unittest

class TestParsers(unittest.TestCase):
    def setUp(self):
        self.test_samples = [
            {
                'title':'2014 Jeep Compass Sport Manual MY14',
                'year': '2014',
                'make': 'Jeep',
                'model': 'Compass Sport',
                'transmission': 'Manual',
                'manufacturer_marketing_year': 'MY14'
            },
        ]

    def test_get_year(self):
        for test_sample in self.test_samples:
            self.assertEqual(
                CarsalesSpider.get_year(test_sample['title']),
                test_sample['year']
            ) 

    def test_get_make(self):
        for test_sample in self.test_samples:
            self.assertEqual(
                CarsalesSpider.get_make(test_sample['title']),
                test_sample['make']
            ) 

    def test_get_model(self):
        for test_sample in self.test_samples:
            self.assertEqual(
                CarsalesSpider.get_model(test_sample['title']),
                test_sample['model']
            ) 
            
    def test_get_transmission(self):
        for test_sample in self.test_samples:
            self.assertEqual(
                CarsalesSpider.get_transmission(test_sample['title']),
                test_sample['transmission']
            ) 
            
    def test_get_manufacturer_marketing_year(self):
        for test_sample in self.test_samples:
            self.assertEqual(
                CarsalesSpider.get_manufacturer_marketing_year(test_sample['title']),
                test_sample['manufacturer_marketing_year']
            ) 
