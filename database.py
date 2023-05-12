import pymysql


class Collection(object):
    def __init__(self, tablename=''):
        self.db = pymysql.connect(host='localhost', user='bilin', passwd='123456', port=3306, db='baicheng')
        self.table = tablename
        cursor = self.db.cursor()
        sqltext = """CREATE TABLE %s (
                     name  CHAR(200) NOT NULL,
                     phone  CHAR(30) NOT NULL,
                     danwei CHAR(200),
                     time INT"""%tablename
        try:
            cursor.execute(sqltext)
            self.db.commit()
        except:
            pass
        cursor.close()

    def insert_one(self, data):
        sql = """INSERT INTO `%s` (`name`, `phone`, `danwei`, `time`)
                 VALUES ('%s', '%s', '%s', %s)"""%(self.table, data['name'],
                                                   data['phone'],data['danwei'],
                                                   data['time'])
        cursor = self.db.cursor()
        cursor.execute(sql)
        self.db.commit()
        cursor.close()

    def count_documents(self, data):
        sql = """SELECT COUNT(*) 
                 FROM %s
                 WHERE name='%s' AND phone='%s'"""%(self.table, data['name'], data['phone'])
        cursor = self.db.cursor()
        cursor.execute(sql)
        result = cursor.fetchall()[0][0]
        cursor.close()
        return int(result)

def getdb():
    return Collection("baicheng")


if __name__=='__main__':
    d = {
        "name": '测试',
        "href": '测试',
        "date_y": 2000,
        "date_m": 1,
        "date_d": 1,
        "area": '测试',
        "source": "test",
        "city": 'test'
    }
    # db.insert_one(d)