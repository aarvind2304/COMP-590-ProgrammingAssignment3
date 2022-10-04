from pymongo import MongoClient
import certifi
client =MongoClient("mongodb+srv://ani4231:mongo123@cluster0.jqkbpbr.mongodb.net/?retryWrites=true&w=majority",tlsCAFile = certifi.where())
db = client["test_db"]

print("select *")
def printE():
    rows = db.test_collection.find({})
    for x in rows:
        print(x)

print("select classic")
row = db.test_collection.find_one({"category" : "classic"})
print(row["joke"])

print("Add joke")
newjoke = {"category": "classic", "joke": "how do you get a squirrel to like you?"}
db.test_collection.insert_one(newjoke)
printE()

def deleteRows():
    print("delete all of a category")
    myquery = {"category": "classic"}
    db.test_collection.delete_many(myquery)
printE()

print("Update")
myquery = {"category": "technology"}
update_as = {"$set": {"category": "tech"}}
db.test_collection.update_many(myquery, update_as)
printE()


