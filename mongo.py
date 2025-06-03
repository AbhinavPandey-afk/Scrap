from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

uri = "mongodb+srv://abhinavpandey2023:9kjRNRLzui2Kh3bh@cluster0.fc83wkp.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))
db = client['mydatabase']
collect = db['myCollect']
document = {"Name":"Bank1","Quarter":"1Q25","Revenue":"$1 Billion","Net Income":"$1 Billion","Date":"01/01/0111"}
insertion = collect.insert_one(document)
print(f"inserted document ID: {insertion.inserted_id}")
# Send a ping to confirm a successful connection
# try:
#     client.admin.command('ping')
#     print("Pinged your deployment. You successfully connected to MongoDB!")
# except Exception as e:
#     print(e)