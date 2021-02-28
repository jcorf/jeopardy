import pymongo as py


class JMongo:
    def __init__(self, database, collection):
        self.client = py.MongoClient("mongodb://localhost:27017/")
        self.db = self.client[database]
        self.collection = self.db[collection]
        print(self.db.collection_names())

    def shutdown(self):
        self.shutdown()

    def insert_clue(self, clue_info):
        id = self.collection.insert_one(clue_info).inserted_id
        print(id)

    def delete_all(self):
        self.collection.drop()


