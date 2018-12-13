# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from .mongosave import PengPai, PengPaiUrl


class PengpaiPipeline(object):

    def process_item(self, item, spider):
        p = PengPaiUrl.objects.filter(url=item['url']).first()
        if p:
            pass
        else:
            PengPai(**item).save()
            PengPaiUrl(url=item['url']).save()
