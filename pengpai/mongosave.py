# -*- coding: utf-8 -*-
# @Time : 2018/12/13 12:41
# @Author : chenpeng
# @Site : pengguoko@163.com
# @File : mongosave.py
from mongoengine import Document, StringField, connect
connect("chenpeng", host="192.168.110.51", port=27017)


class PengPai(Document):
    title = StringField()
    time = StringField()
    content = StringField()
    url = StringField()
    classification = StringField()
    keywords = StringField()
    author = StringField()


class PengPaiUrl(Document):
    url = StringField()
