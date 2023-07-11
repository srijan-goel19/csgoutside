from pymongo import MongoClient
conn = MongoClient("mongodb://localhost:27018/csgoutside")
# print(conn)
# db = conn.get_database()
# print(db['players'].find_one({"Name": "Srijan"}))
