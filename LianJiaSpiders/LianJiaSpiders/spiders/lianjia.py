# -*- coding: utf-8 -*-
# 页码url接口分析：
# 1:https://bj.lianjia.com/zufang/andingmen/pg1/#contentList
# 2:https://bj.lianjia.com/zufang/andingmen/pg2/#contentList
# 3:https://bj.lianjia.com/zufang/andingmen/pg3/#contentList

import scrapy
import re
from day11.LianJiaSpiders.LianJiaSpiders.items import LianjiaspidersItem
import json



class LianjiaSpider(scrapy.Spider):
    name = 'lianjia'
    allowed_domains = ['lianjia.com']
    start_urls = ['https://bj.lianjia.com/zufang/']

    # 解析城区
    def parse(self, response):
        # 检测数据
        # html = response.body.decode('utf-8')
        # print(html)

        # 获取城区信息
        city_area_list = response.xpath("//ul[@data-target='area']/li[position()>1]/a/@href | "
                                        "//ul[@data-target='area']/li[position()>1]/a/text()").extract()
        # print(city_area_list)
        # 拼接完整url
        for index in range(0, len(city_area_list), 2):
            city_url = "https://bj.lianjia.com" + city_area_list[index]
            city_name = city_area_list[index + 1]
            # print("======{}".format(city_name))
            yield scrapy.Request(url=city_url, callback=self.parse_business, dont_filter=True)
            # break
            # 获取商圈url

    # 解析商圈
    def parse_business(self, response):
        # 获取商圈信息
        business_circle_list = response.xpath("//div[@id='filter']/ul[4]/li[position()>1]/a/@href | "
                                              "//div[@id='filter']/ul[4]/li[position()>1]/a/text()").extract()
        # print(business_circle_list)
        # 拼接完整的url
        for index in range(0, len(business_circle_list), 2):
            business_url = "https://bj.lianjia.com" + business_circle_list[index]
            business_name = business_circle_list[index + 1]
            # print('========={}'.format(business_name))
            yield scrapy.Request(url=business_url, callback=self.parse_page)
            # break

    def parse_page(self, response):
        # print(response.url)
        # 获取最大页码
        page_max = response.xpath("//div[@class='content__pg']/@data-totalpage").extract()[0]
        # print(page_max)
        if not page_max:
            return
        for page in range(1, int(page_max) + 1):
            # 拼接页码url
            page_url = str(response.url) + 'pg{}'.format(page)
            # print('============第{}页'.format(page))
            yield scrapy.Request(url=page_url, callback=self.parse_house)

    def parse_house(self, response):
        # print(response)
        # 缩小范围
        div_list = response.xpath("//div[@class='content__list']/div")
        # print(len(div_list))

        for div in div_list:
            # 图片
            pic = div.xpath(".//img/@data-src").extract()[0]
            # print(pic)
            pic = pic.replace("250x182", "1800x865")
            # print(pic)

            # 标题
            title = div.xpath(".//p[@class='content__list--item--title twoline']/a/text()").extract()[0].strip()
            # print(title)

            # 城区
            city_area = div.xpath(".//p[@class='content__list--item--des']/a[1]/text()").extract()[0]
            # print(city_area)

            # 商圈
            business_circle = div.xpath(".//p[@class='content__list--item--des']/a[2]/text()").extract()[0]
            # print(city_area, business_circle)

            # 面积
            area = div.xpath(".//p[@class='content__list--item--des']//text()[4]").extract()
            area = area[0].strip() if area else ""  # 空值处理
            # print(area)

            # 朝向
            toward = div.xpath(".//p[@class='content__list--item--des']//text()[5]").extract()[0].strip()
            # print(toward)

            # 房间信息
            fang_info = div.xpath(".//p[@class='content__list--item--des']//text()[6]").extract()[0].strip()
            # print(fang_info)
            room = re.findall("(\d+)室", fang_info)  # 室
            hall = re.findall("(\d+)厅", fang_info)  # 厅
            toilet = re.findall("(\d+)卫", fang_info)  # 卫
            # 空值处理
            room = int(room[0]) if room else 0
            hall = int(hall[0]) if hall else 0
            toilet = int(toilet[0]) if toilet else 0
            # print(room, hall, toilet)

            # 发布时间
            publish_date = div.xpath(".//p[@class='content__list--item--time oneline']/text()").extract()[0]
            # print(publish_date)

            # 标签
            sign_list = div.xpath(".//p[@class='content__list--item--bottom oneline']/i/text()").extract()
            # print(sign_list)
            # 将标签转换为字符串
            sign = "#".join(sign_list)
            # print(sign)

            # 价格
            price = div.xpath(".//em/text()").extract()[0]
            # print(price)

            # 详情url
            detail_url = div.xpath(".//p[@class='content__list--item--title twoline']/a/@href").extract()[0]
            # 拼接完整的详情url
            detail_url = "https://bj.lianjia.com" + detail_url

            # print(detail_url)

            # 实例化items类
            item = LianjiaspidersItem()

            item['pic'] = pic
            item['title'] = title
            item['city_area'] = city_area
            item['business_circle'] = business_circle
            item['area'] = area
            item['toward'] = toward
            item['room'] = room
            item['hall'] = hall
            item['toilet'] = toilet
            item['publish_date'] = publish_date
            item['sign'] = sign
            item['price'] = price

            yield scrapy.Request(url=detail_url, callback=self.parse_detail, meta={"data": item}, dont_filter=True)

    # 解析详情页信息
    def parse_detail(self, response):

        # 接收item参数
        item = response.meta['data']

        floor = response.xpath("//ul/li[@class='fl oneline'][8]/text()").extract()
        floor = floor[0] if floor else ""
        # print(floor)
        item["floor"] = floor

        # 获取经纪人id号 ucid
        ucid = self.get_ucid(response)
        # print(ucid)
        # 获取house_code
        house_code = re.findall("zufang/(.*?).html", response.url)[0]
        # print(house_code)

        # 拼接完整的经纪人接口
        agent_url = "https://bj.lianjia.com/zufang/aj/house/brokers?" \
                    "house_codes={}&position=bottom" \
                    "&ucid={}".format(house_code, ucid)
        # print(agent_url)
        yield scrapy.Request(url=agent_url, callback=self.get_phone, meta={"data": item, "house_code": house_code},
                             dont_filter=True)

    def get_phone(self, response):
        item = response.meta['data']
        house_code = response.meta.get('house_code')
        try:
            str_data = response.text
            json_data = json.loads(str_data)
            phone = json_data.get("data")[house_code][house_code].get("tp_number")

            # print(phone)
        except Exception as e:
            print(e)
            phone = ''
        item["phone"] = phone
        # print(item)
        yield item

    def get_ucid(self, response):
        try:
            ucid = response.xpath("//span[@class='contact__im im__online']/@data-info").extract()[0]
            # print(ucid)
            self.count_ucid = 1
            return ucid
        except Exception as e:
            print(e)
            if self.count_ucid == 3:
                return ""
            else:
                self.count_ucid += 1
                return self.get_ucid(response)
