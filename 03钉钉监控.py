"""
kpi小姐姐 的api接口
https://oapi.dingtalk.com/robot/send?access_token=8daebe660297f090e6839b6a4454ff05382b59f3d515b3d7c14bc07f5fb642dd
"""
import pymysql
import time
import requests


class Moniter:
    def __init__(self):
        self.conn_mysql()
        self.get_data()

    def conn_mysql(self):
        # 创建数据库的连接对象
        # 字符集是utf8 不是utf-8
        self.conn = pymysql.connect(host="127.0.0.1", user="root", password='123',
                                    database="0218", charset="utf8")
        # 创建操作数据库的对象
        self.cur = self.conn.cursor()

    def get_data(self):
        # 定义一天前的时间戳
        day_age = time.time() - 86400
        # 获取需要发送的数据
        # 定义查询出总数和更新数量的sql语句
        sql = """
        select count(*) from lianjia
        UNION 
        select count(*) from lianjia where refresh_time>{}
        UNION
        select phone from source_name where source="lianjia"
        """.format(day_age)

        # 执行sql语句 并获取sql语句查询出来的 数据
        self.cur.execute(sql)
        self.conn.commit()
        # 查询返回的数据
        data = self.cur.fetchall()
        # print(data, type(data))

        # 提取数据 获取总数 和更新数
        total_count = int(data[0][0])
        refresh_count = int(data[1][0])
        phone = data[2][0]

        # print(total_count, refresh_count, phone)

        # 生成刷新数量的百分比
        per_no_refresh = refresh_count / total_count
        if per_no_refresh > 0.4:
            # 化为百分号
            per_no_refresh = "%.2f%%" % (per_no_refresh * 100)
            print(per_no_refresh)

            # 发送钉钉消息
            self.dingding(per_no_refresh, phone)

    def dingding(self, per_no_refresh, phone):
        dd_api = "https://oapi.dingtalk.com/robot/send?access_toke" \
                 "n=8daebe660297f090e6839b6a4454ff05382b59f3d515b3d7c14bc07f5fb642dd"
        print(phone, per_no_refresh)

        dd_data = {
            "msgtype": "text",
            "text": {
                "content": "我是0号机器人！！！！！！{}".format(per_no_refresh)
            },
            "at": {
                "atMobiles": [
                    # "18341845693",
                    "18679030315"
                ],
                "isAtAll": False
            }
        }

        requests.post(dd_api, json=dd_data)
        print("send success")

    def __del__(self):
        self.cur.close()
        self.conn.close()


if __name__ == '__main__':
    Moniter()
