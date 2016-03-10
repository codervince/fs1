# -*- coding: utf-8 -*
__author__ = 'mizhgun@gmail.com'
import logging
import signal

import scrapy
from scrapy.exceptions import NotConfigured, CloseSpider
from scrapy.http import HtmlResponse
from scrapy.xlib.pydispatch import dispatcher
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class FlatstatsMiddleware(object):
    def __init__(self, settings):
        self.__username = settings.get('FLATSTATS_LOGIN', None)
        self.__passwd = settings.get('FLATSTATS_PASSWORD', None)
        if self.__username is None or self.__passwd is None:
            raise NotConfigured('No FlatStats credentials given')
        self.__driver_name = settings.get('FLATSTATS_DRIVER', 'Firefox')
        if getattr(webdriver, self.__driver_name, None) is None:
            raise NotConfigured('Wrong Selenium driver')
        self.__d = None
        self.driver

    @classmethod
    def from_settings(cls, settings):
        return cls(settings)

    @property
    def driver(self):
        if self.__d is None:
            logging.debug('Initializing Selenium webdriver')
            self.__d = getattr(webdriver, self.__driver_name)()
            dispatcher.connect(self.close_driver, scrapy.signals.spider_closed)

            # Login
            self.__d.get('https://flatstats.co.uk/')
            self.__d.find_element_by_id('dLabel').click()
            el = self.__d.find_element_by_id('username')
            el.clear()
            el.send_keys(self.__username)
            el = self.__d.find_element_by_id('passwd')
            el.clear()
            el.send_keys(self.__passwd)
            self.__d.find_element_by_id('login').click()
            try:
                self.__d.find_element_by_xpath('//button[@id="mAlerts"]')
            except NoSuchElementException:
                raise CloseSpider('Unable to login flatstats.co.uk')

        return self.__d

    def close_driver(self):
        if self.__d:
            logging.debug('Closing Selenium webdriver')
            self.__d.quit()
            try:
                self.__d.service.process.send_signal(signal.SIGTERM)
            except AttributeError:
                pass

    def process_request(self, request, spider):

        if 'flatstats.co.uk/racing-system-builder.php' in request.url:
            self.__d.get(request.url)
            report = '<div id="system">' + self.__d.find_element_by_xpath("//div[@class='panel panel-default']").get_attribute('innerHTML')+ '</div>'
            self.__d.find_element_by_id('b-full-report').click()
            try:
                WebDriverWait(self.__d, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//div[@id="dialog-full-report"]//table')))
                report += self.__d.find_element_by_xpath('//div[@id="dialog-full-report"]').get_attribute('innerHTML')
                self.__d.find_element_by_xpath('//div[@class="ui-dialog-buttonset"]/button[.="Runners"]').click()
                self.__d.find_element_by_xpath('//div[@class="ui-dialog-buttonset"]/button[.="Contenders"]').click()
                whs = self.__d.window_handles
                dh = None
                for wh in whs:
                    self.__d.switch_to_window(wh)
                    if self.__d.current_url == request.url:
                        dh = wh

                    elif self.__d.current_url.endswith('system-builder-runners.php'):
                        self.__d.switch_to_window(wh)
                        WebDriverWait(self.__d, 10).until(
                            EC.presence_of_element_located((By.ID, 'content')))
                        report += '<div id="runners">' + self.__d.find_element_by_id('content').get_attribute(
                            'innerHTML') + '</div>'
                        if dh:
                            self.__d.close()

                    elif self.__d.current_url.endswith('system-builder-contenders.php'):
                        self.__d.switch_to_window(wh)
                        WebDriverWait(self.__d, 10).until(
                            EC.presence_of_element_located((By.ID, 'content')))
                        report += '<div id="contenders">' + self.__d.find_element_by_id('content').get_attribute(
                            'innerHTML') + '</div>'
                        if dh:
                            self.__d.close()
                if dh:
                    self.__d.switch_to_window(dh)
            except TimeoutException:
                report = 'Error'
            return HtmlResponse(url=request.url, request=request, body=report, encoding='utf-8')
