# import os
# from pymongo import MongoClient
# from datetime import datetime
# import pytz
# from dotenv import load_dotenv

# load_dotenv()

# client = MongoClient(os.getenv('MONGODB_URL'))
# db = client['OrbitAI']
# collection = db['OrbitAI']

# print("=== FINDING ALL CALENDAR EVENTS ===")

# unique_events = set()
# all_events = []

# for record in collection.find():
#     for key in record.keys():
#         if key.startswith('calendar:') and 'name:' in key and 'start:' in key:
#             # Parse the calendar data from the key
#             lines = key.replace('calendar: ', '').split('\n')
#             event_data = {}
            
#             for line in lines:
#                 if ':' in line:
#                     k, v = line.split(':', 1)
#                     event_data[k.strip()] = v.strip()
            
#             if 'name' in event_data and 'start' in event_data and 'id' in event_data:
#                 event_id = event_data['id']
#                 if event_id not in unique_events:
#                     unique_events.add(event_id)
#                     all_events.append(event_data)

# print(f"Found {len(all_events)} unique events:")
# for event in all_events:
#     print(f"- {event.get('name')} at {event.get('start')}")

# # Filter for today (2025-09-06)
# ist = pytz.timezone('Asia/Kolkata')
# today = datetime.now(ist).date()

# print(f"\nToday's events ({today}):")
# for event in all_events:
#     start_str = event.get('start')
#     if '2025-09-05' in start_str:  # Simple string check for today
#         try:
#             dt = datetime.fromisoformat(start_str.replace('+05:30', ''))
#             time_str = dt.strftime('%I:%M %p')
#             print(f"• {event.get('name')} at {time_str}")
#         except:
#             print(f"• {event.get('name')}")



import os
from pymongo import MongoClient
from datetime import datetime
import pytz
from dotenv import load_dotenv

load_dotenv()

client = MongoClient(os.getenv('MONGODB_URL'))
db = client['OrbitAI']
collection = db['OrbitAI']

print("=== FINDING ALL CALENDAR EVENTS (INCLUDING MULTIPLE EVENTS PER FIELD) ===")

unique_events = set()
all_events = []

for record in collection.find():
    for key in record.keys():
        if key.startswith('calendar:') and 'name:' in key and 'start:' in key:
            # Split by 'id:' to get multiple events from one field
            event_blocks = key.split('id:')[1:]  # Skip first empty part
            
            for block in event_blocks:
                if not block.strip():
                    continue
                    
                # Parse this event block
                lines = block.strip().split('\n')
                event_data = {}
                
                # First line is the event ID
                if lines:
                    event_data['id'] = lines[0].strip()
                
                # Parse remaining lines
                for line in lines[1:]:
                    if ':' in line:
                        k, v = line.split(':', 1)
                        event_data[k.strip()] = v.strip()
                
                # Check if valid event and not duplicate
                if 'name' in event_data and 'start' in event_data and 'id' in event_data:
                    event_id = event_data['id']
                    if event_id not in unique_events:
                        unique_events.add(event_id)
                        all_events.append(event_data)

print(f"Found {len(all_events)} unique events:")
for event in all_events:
    print(f"- {event.get('name')} at {event.get('start')}")

# Filter for today (2025-09-06)
ist = pytz.timezone('Asia/Kolkata')
today = datetime.now(ist).date()

print(f"\nToday's events ({today}):")
for event in all_events:
    start_str = event.get('start')
    if '2025-09-06' in start_str:  # Simple string check for today
        try:
            dt = datetime.fromisoformat(start_str.replace('+05:30', ''))
            time_str = dt.strftime('%I:%M %p')
            print(f"• {event.get('name')} at {time_str}")
        except:
            print(f"• {event.get('name')}")


