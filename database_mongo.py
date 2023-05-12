import pymongo

myclient = pymongo.MongoClient("mongodb://localhost:27017")
db = myclient['baicheng']


class DB(object):
    def close(self):
        pass


class Collection(object):
    def __init__(self, tablename=''):
        self.db = DB()
        self.coll = db[tablename]

    def insert_one(self, data):
        return self.coll.insert_one(data)

    def count_documents(self, data):
        return self.coll.count_documents(data)


def getdb():
    return Collection("baicheng")


if __name__=='__main__':
    pass