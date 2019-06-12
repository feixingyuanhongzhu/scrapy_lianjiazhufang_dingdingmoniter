# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql
import time


# 存储数据库
class LianjiaspidersPipeline(object):
    def __init__(self):
        self.count = 1
        self.conn_mysql()

    def conn_mysql(self):
        self.conn = pymysql.connect(host="127.0.0.1", port=3306, user='root', password="123", database="0218",
                                    charset="utf8")
        self.cur = self.conn.cursor()

    def process_item(self, item, spider):
        # print(self.count,item)

        pic = item['pic']
        title = item['title']
        city_area = item['city_area']
        business_circle = item['business_circle']
        area = item['area']
        toward = item['toward']
        room = item['room']
        hall = item['hall']
        toilet = item['toilet']
        publish_date = item['publish_date']
        sign = item['sign']
        price = item['price']
        floor = item['floor']
        phone = item['phone']

        sql = 'insert into lianjia (pic,title,city_area,business_circle,area,toward,room,hall,toilet,publish_date,sign,price,floor,phone,refresh_time) values ("{}","{}","{}","{}","{}","{}",{},{},{},"{}","{}","{}","{}","{}",{})'.format(
            pic, title, city_area, business_circle, area, toward, room, hall, toilet, publish_date, sign, price, floor,
            phone,int(time.time()))

        print(self.count, sql)
        self.count += 1
        self.cur.execute(sql)
        self.conn.commit()
        return item
