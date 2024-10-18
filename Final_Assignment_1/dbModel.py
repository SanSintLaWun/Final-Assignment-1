import pymongo

class NccAuctionModel:
    def __init__(self):
        pass
    def connect(self):
        connection = pymongo.MongoClient("localhost", 27017)
        self.database = connection["ncc_dip2"]
        self.col = self.database["user_info"]
        self.item_list = self.database["item_data"]
        self.candi = self.database["candidate"]

    def info(self):
        return self.col

    def login(self):
        return self.col

    def item(self):
        item_list = self.connect("items_and_prices")

        return item_list

    def candidate(self):
        collection = self.connect("candidate")
        return collection

    def user_info(self):
        collection = self.connect("user_info")
        return collection

    def info(self):
        collection = self.connect("info")
        return collection
    
    def reg(self):
        collection = self.connect("reg")
        return collection

    def login(self):
        collection = self.connect("login")
        return collection

