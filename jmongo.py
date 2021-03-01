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
        self.collection.insert_one(clue_info)

    def update_set(self, query, update):
        self.collection.update_many(query, update)

    def delete_all(self):
        self.collection.drop()


