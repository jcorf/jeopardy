import jscraper
import pymongo as py


class JMongo:
    def __init__(self, database, collection):
        self.client = py.MongoClient()
        self.db = self.client.get_database(database)

        if collection in self.db.collection_names():
            self.collection = self.db.get_collection(collection)
        else:
            self.collection = self.db.create_collection(collection)

    def shutdown(self):
        self.shutdown()

    def insert_clue(self):
        self.collection.insert()


