# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql


class TaobaoPipeline(object):

    def open_spider(self,spider):
        print('打开数据库')
        self.db = pymysql.connect(
            host = '192.168.45.130',
            port = 3306,
            user = 'root',
            password = '1234',
            db = 'taobao',
            charset = 'utf8'
        )
        self.cursor = self.db.cursor()

    def close_spider(self,spider):
        print('关闭数据库')
        self.db.close()

    def process_item(self, item, spider):
        print('开始写入数据库')
        self.cursor.execute('insert into tb(name,y_price,x_price,imgs_url) values(%s,%s,%s,%s)',
                            args=(item['name'],
                                  item['y_price'],
                                  item['x_price'],
                                  item['imgs_url']))

        self.db.commit()
        if self.cursor.rowcount >=1:
            print(item['name'],'数据写入成功')

        return item
