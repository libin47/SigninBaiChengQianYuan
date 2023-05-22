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

    def close(self):
        self.db.close()

    def insert_one(self, data):
        return self.coll.insert_one(data)

    def count_documents(self, data):
        return self.coll.count_documents(data)

    def find_one(self, data):
        return self.coll.find_one(data)

    def find(self, data):
        return self.coll.find(data)


def getdb():
    return Collection("baicheng")

def getdb_user():
    return Collection("user")

def getdb_dingcan():
    return Collection("dingcan")


if __name__=='__main__':
    pass