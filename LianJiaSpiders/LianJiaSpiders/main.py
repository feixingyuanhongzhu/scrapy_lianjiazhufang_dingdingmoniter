from scrapy import cmdline

cmdline.execute("scrapy crawl lianjia --nolog".split())
# cmdline.execute("scrapy crawl lianjia".split())
# 将所有已删除项目转储到JSON / CSV / XML文件的最简单方法
# cmdline.execute('scrapy crawl lianjia -o items.json'.split())