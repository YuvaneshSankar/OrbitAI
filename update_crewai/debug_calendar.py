import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

client = MongoClient(os.getenv('MONGODB_URL'))
db = client['OrbitAI']
collection = db['OrbitAI']

# Get 3 sample records
records = list(collection.find().limit(3))

print("=== SAMPLE RECORDS ===")
for i, record in enumerate(records, 1):
    print(f"\nRECORD {i}:")
    print(f"  _id: {record['_id']}")
    print("  KEYS:")
    for key in record.keys():
        if key != '_id':
            print(f"    '{key}': {type(record[key]).__name__} - {str(record[key])[:100]}...")
