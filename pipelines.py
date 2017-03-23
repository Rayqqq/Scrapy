# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import sqlite3
import pymysql
import datetime
import struct
import socket
from ProxyWalker.MQ import MQ
import json

from scrapy.exceptions import DropItem
from scrapy.signalmanager import SignalManager
from ProxyWalker.signals import item_exists
from ProxyWalker.settings import MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PWD, MYSQL_DATABASE
from ProxyWalker.settings import  MQ_HOST, MQ_PROT, MQ_USER, MQ_PASSWORD
import os
import time
import binascii

def ip2int(ip):
    if ip:
        return int(struct.unpack('!L', socket.inet_aton(ip))[0])
    return ip


class ProxySpiderPipeline(object):

    @classmethod
    def open_spider(self, spider):
        self.conn = pymysql.connect(host=MYSQL_HOST, port=MYSQL_PORT, user=MYSQL_USER, passwd=MYSQL_PWD,
                                    db=MYSQL_DATABASE, charset='utf8')
        self.cursor = self.conn.cursor()        #使用python连接MySQL数据库，调用一个API

        #判断是否第一次抓取
        self.first_flag = False
        self.cursor.execute('select * from proxy_spider where source=%s', (spider.name))
        record = self.cursor.fetchall()
        if self.cursor: self.cursor.close()
        if self.conn: self.conn.close()
        if (not record) or (len(record) == 0):
            self.first_flag = True
        #ip004计数器
        self.count = 0

    @classmethod
    def __del__(self):
        if self.cursor: self.cursor.close()
        if self.conn: self.conn.close()

    @classmethod
    def process_item(self, item, spider):
        if spider.name == 'ip004':
            self.count += 1
        self.store_into_db(item, spider)
        return item

    @classmethod
    def store_into_db(self, item, spider):
        #数据库里hashcode的类型为unsinged ，这里需要处理一下hashcode，解决负数的问题
        if item['_id'] > 0:
            item['_id'] = '10'+str(item['_id'])
        else:
            item['_id'] = '11'+str(item['_id']).replace('-', '')
        item['_id'] = int(item['_id']) % (2**64)

        self.conn = pymysql.connect(host=MYSQL_HOST, port=MYSQL_PORT, user=MYSQL_USER, passwd=MYSQL_PWD,
                                    db=MYSQL_DATABASE, charset='utf8')
        self.cursor = self.conn.cursor()
        # 处理重复的数据:
        #   hashcode存在认为是在抓取旧数据
        #   ip和port同时存在,认为爬取的数据需要被丢弃
        #   同一个源第一次爬取的时候不判断是否在抓旧数据
        #   ip004.com前3页不判断是否在抓旧数据（每页50个数据）
        self.cursor.execute('select * from proxy_spider where hashcode=%s', [item['_id']])
        record = self.cursor.fetchall()
        if (not self.first_flag) and (record or len(record) != 0) and (spider.name != 'ip004' or self.count >= 150):
            spider.crawler.signals.send_catch_log(signal=item_exists, item=item, spider=spider)
            raise DropItem
        self.cursor.execute('select * from proxy_spider where ip_addr=%s and port=%s', (ip2int(item['ip']), item['port']))
        record = self.cursor.fetchall()
        if record or len(record) != 0:
            raise DropItem

        params = [ip2int(item['ip']), item['port'], item['source'], item['p_type'], item['_id'], datetime.datetime.today()]

        sql = 'insert into proxy_spider(ip_addr, port, source, proxy_type, hashcode, first_time) values(%s, %s, %s, %s ,%s, %s)'
        self.cursor.execute(sql, params)
        self.conn.commit()

        msg = json.dumps(dict(item))
        mq = MQ(usage='PubSub', exchange='proxy', host=MQ_HOST, port=MQ_PROT, user=MQ_USER, passwd=MQ_PASSWORD)
        mq.pub(msg)