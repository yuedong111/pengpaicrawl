# -*- coding: utf-8 -*-
# @Time : 2018/12/13 10:32
# @Author : chenpeng
# @Site : pengguoko@163.com
# @File : pengpaispider.py
from scrapy.selector import Selector
from scrapy.http import Request
import scrapy
from bs4 import BeautifulSoup
from pengpai.items import PengpaiItem
from pengpai.mongosave import PengPaiUrl
import time
import requests


class pengpai(scrapy.spiders.Spider):
    name = 'pengpai'
    custom_settings = {'DOWNLOAD_DELAY': 0.2, 'CONCURRENT_REQUESTS_PER_IP': 4, 'DOWNLOADER_MIDDLEWARES': {}, }
    allowd_domains = ["www.thepaper.cn"]
    home_url = "https://www.thepaper.cn/"
    start_urls = ["https://www.thepaper.cn/load_index.jsp?nodeids=25434,25436,25433,25438,25435,25437,27234,25485,25432,37978,&topCids=2734118,2732678,2728847",
                  "https://www.thepaper.cn/load_index.jsp?nodeids=25462,25488,25489,25490,25423,25426,25424,25463,25491,25428,27604,25464,25425,25429,25481,25430,25678,25427,25422,25487,25634,25635,25600,&topCids=2732672,2734209,2733777",
                  "https://www.thepaper.cn/load_sparker_masnory.jsp?nodeids=35571,35570,35572,47281,&topCids=2734038,2733742,2691603,2727102,2729423,",
                  "https://www.thepaper.cn/load_index.jsp?nodeids=25444,27224,26525,26878,25483,25457,25574,25455,26937,25450,25482,25445,25456,25446,25536,26506,&topCids=2728184,2733566",
                  "https://www.thepaper.cn/load_index.jsp?nodeids=25448,26609,25942,26015,25599,25842,26862,25769,25990,26173,26202,26404,26490,&topCids=2726364,2727945",
                  "https://www.thepaper.cn/load_chosen.jsp?nodeids=25949&topCids=2734083,2734099,2734140,2732672,",]
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8"
                  "image/webp,image/apng,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "en-US,en;zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4,zh-TW;q=0.2,"
                           "ja;q=0.2,ru;q=0.2,gl;q=0.2,ko;q=0.2",
        "Pragma": "no-cache",
    }

    def start_requests(self):
        for item in self.start_urls:
            yield scrapy.FormRequest(
                url=item,
                headers=self.headers,
                callback=self.parse,
            )

    def parse(self, response):
        page_url = "&pageidx={}&lastTime={}"
        s = str(time.time()).split(".")
        timenum = s[0] + s[1][0:3]
        page = 1
        while True:
            new_url = response.url +page_url.format(page,timenum)
            r = requests.get(new_url)
            if r.text == "":
                break
            else:
                yield scrapy.FormRequest(new_url, headers=self.headers, callback=self.parse_title)
            page = page + 1

    def parse_title(self,response):
        soup = BeautifulSoup(response.body, 'lxml')
        manya = soup.find_all('a')
        for item in manya:
            if item.has_attr("href") and item.has_attr("target"):
                new_url = self.home_url + item['href']
                title = item.text
                yield scrapy.FormRequest(new_url, headers=self.headers, callback=self.parse_news, meta={'title': title})

    def parse_news(self, response):
        pengpai = PengpaiItem()
        pengpai['url'] = response.url
        title1 = response.meta['title']
        soup = BeautifulSoup(response.body, 'lxml')
        keywords = soup.find('div',{'class': 'news_keyword'})
        if keywords:
            keywords = keywords.text.split(">>")[-1].strip()
        else:
            keywords = "其他"
        pengpai['keywords'] = keywords
        content = soup.find('div', {'class': "newscontent"})
        new_about = False
        if content:
            new_about = content.find('div', {'class': 'news_about'})
            classfi = content.find('div', {'class': 'news_path'})
            title = content.find('h1', {'class': 'news_title'})
            if title:
                pengpai['title'] = title.text
            else:
                pengpai['title'] = ''
            if classfi:
                ma = classfi.find_all('a')
                classfication = ma[1].text
            else:
                classfication = "直播"
            pengpai['classification'] = classfication
        else:
            pengpai['classification'] = "其他"
        new_txt = soup.find_all('div', {'class': 'news_txt'})
        new_about_txt = ''
        if new_about:
            temp = ''
            ps = new_about.find_all('p')
            for item in ps:
                new_about_txt = new_about_txt+" "+item.text.strip()
            for item in new_about_txt.split(' '):

                if '-' in item:
                    time = item
                    pengpai['time'] = time
                if '-' not in item and ':' not in item:
                    temp = temp + item.strip()
                pengpai['author'] = temp
        else:
            # print(response.url)
            pass
        new_text = ''
        for item in new_txt:
            new_text = new_text + item.text
        pengpai['content'] = new_text
        yield pengpai
        similar = soup.find('div', {"class": "ctread_bd"})
        if similar:
            cthread = similar.find_all('div',{'class': 'ctread_name'})
            for item in cthread:
                a = item.find('a')
                new_url = self.home_url + a['href']
                title1 = a.text
                p = PengPaiUrl.objects.filter(url=new_url).first()
                if p:
                    pass
                else:
                    yield scrapy.FormRequest(new_url, headers=self.headers, callback=self.parse_news, meta={'title': title1})

