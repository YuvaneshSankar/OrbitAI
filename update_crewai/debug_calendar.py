# # # # import os
# # # # from pymongo import MongoClient
# # # # from datetime import datetime
# # # # import pytz
# # # # from dotenv import load_dotenv

# # # # load_dotenv()

# # # # client = MongoClient(os.getenv('MONGODB_URL'))
# # # # db = client['OrbitAI']
# # # # collection = db['OrbitAI']

# # # # print("=== FINDING ALL CALENDAR EVENTS ===")

# # # # unique_events = set()
# # # # all_events = []

# # # # for record in collection.find():
# # # #     for key in record.keys():
# # # #         if key.startswith('calendar:') and 'name:' in key and 'start:' in key:
# # # #             # Parse the calendar data from the key
# # # #             lines = key.replace('calendar: ', '').split('\n')
# # # #             event_data = {}
            
# # # #             for line in lines:
# # # #                 if ':' in line:
# # # #                     k, v = line.split(':', 1)
# # # #                     event_data[k.strip()] = v.strip()
            
# # # #             if 'name' in event_data and 'start' in event_data and 'id' in event_data:
# # # #                 event_id = event_data['id']
# # # #                 if event_id not in unique_events:
# # # #                     unique_events.add(event_id)
# # # #                     all_events.append(event_data)

# # # # print(f"Found {len(all_events)} unique events:")
# # # # for event in all_events:
# # # #     print(f"- {event.get('name')} at {event.get('start')}")

# # # # # Filter for today (2025-09-06)
# # # # ist = pytz.timezone('Asia/Kolkata')
# # # # today = datetime.now(ist).date()

# # # # print(f"\nToday's events ({today}):")
# # # # for event in all_events:
# # # #     start_str = event.get('start')
# # # #     if '2025-09-05' in start_str:  # Simple string check for today
# # # #         try:
# # # #             dt = datetime.fromisoformat(start_str.replace('+05:30', ''))
# # # #             time_str = dt.strftime('%I:%M %p')
# # # #             print(f"• {event.get('name')} at {time_str}")
# # # #         except:
# # # #             print(f"• {event.get('name')}")



# import os
# from pymongo import MongoClient
# from datetime import datetime
# import pytz
# from dotenv import load_dotenv

# load_dotenv()

# client = MongoClient(os.getenv('MONGODB_URL'))
# db = client['OrbitAI']
# collection = db['OrbitAI']

# print("=== FINDING ALL CALENDAR EVENTS (INCLUDING MULTIPLE EVENTS PER FIELD) ===")

# unique_events = set()
# all_events = []

# for record in collection.find():
#     for key in record.keys():
#         if key.startswith('calendar:') or key.startswith('id:') and 'name:' in key and 'start:' in key:
#             # Split by 'id:' to get multiple events from one field
#             event_blocks = key.split('id:')[1:]  # Skip first empty part
            
#             for block in event_blocks:
#                 if not block.strip():
#                     continue
                    
#                 # Parse this event block
#                 lines = block.strip().split('\n')
#                 event_data = {}
                
#                 # First line is the event ID
#                 if lines:
#                     event_data['id'] = lines[0].strip()
                
#                 # Parse remaining lines
#                 for line in lines[1:]:
#                     if ':' in line:
#                         k, v = line.split(':', 1)
#                         event_data[k.strip()] = v.strip()
                
#                 # Check if valid event and not duplicate
#                 if 'name' in event_data and 'start' in event_data and 'id' in event_data:
#                     event_id = event_data['id']
#                     if event_id not in unique_events:
#                         unique_events.add(event_id)
#                         all_events.append(event_data)

# print(f"Found {len(all_events)} unique events:")
# for event in all_events:
#     print(f"- {event.get('name')} at {event.get('start')}")

# # Filter for today (2025-09-06)
# ist = pytz.timezone('Asia/Kolkata')
# today = datetime.now(ist).date()

# print(f"\nToday's events ({today}):")
# for event in all_events:
#     start_str = event.get('start')
#     if '2025-09-06' in start_str:  # Simple string check for today
#         try:
#             dt = datetime.fromisoformat(start_str.replace('+05:30', ''))
#             time_str = dt.strftime('%I:%M %p')
#             print(f"• {event.get('name')} at {time_str}")
#         except:
#             print(f"• {event.get('name')}")


# # import os
# # from pymongo import MongoClient
# # from datetime import datetime
# # import pytz
# # import re
# # from dotenv import load_dotenv

# # load_dotenv()

# # client = MongoClient(os.getenv('MONGODB_URL'))
# # db = client['OrbitAI']
# # collection = db['OrbitAI']

# # print("=== SIMPLE CALENDAR DEBUG ===")

# # # processed_fields = set()  # To avoid duplicates
# # # all_events = []
# # # namesfound=set()

# # # for record in collection.find():
# # #     for key in record.keys():
# # #         if key.startswith('calendar:') and key not in processed_fields:
# # #             processed_fields.add(key)
            
# # #             # Simple extraction using different regex patterns
# # #             names = re.findall(r'name:([^n\r]+?)(?=\s+organizer)', key)
# # #             starts = re.findall(r'start:([^\s\n]+)', key)
            
            
# # #             # Match names with starts
# # #             for i, name in enumerate(names):
# # #                 if i < len(starts):
# # #                     all_events.append({
# # #                         'name': name.strip(),
# # #                         'start': starts[i].strip()
# # #                     })



# # namefound=set()

# # for record in collection.find():
# #     for 
# # print(f"\n=== RESULTS ===")
# # print(f"Total events: {len(all_events)}")

# # for event in all_events:
# #     print(f"- {event['name']} at {event['start']}")

# # # Check today's events
# # print(f"\nToday's events (2025-09-06):")
# # for event in all_events:
# #     if '2025-09-06' in event['start']:
# #         print(f"• {event['name']} at {event['start']}")



import os
from pymongo import MongoClient
from datetime import datetime
import pytz
from dotenv import load_dotenv

def get_todays_calendar_events():
    load_dotenv()
    
    client = MongoClient(os.getenv('MONGODB_URL'))
    db = client['OrbitAI']
    collection = db['OrbitAI']
    
    unique_events = set()
    all_events = []
    
    for record in collection.find():
        for key in record.keys():
            if key.startswith('calendar:') or key.startswith('id:') and 'name:' in key and 'start:' in key:
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
    
    # Filter for today and format
    ist = pytz.timezone('Asia/Kolkata')
    today = datetime.now(ist).date()
    
    todays_events = []
    for event in all_events:
        start_str = event.get('start')
        if today.strftime('%Y-%m-%d') in start_str:  # Check for today
            try:
                dt = datetime.fromisoformat(start_str.replace('+05:30', ''))
                time_str = dt.strftime('%I:%M %p')
                todays_events.append(f"• {event.get('name')} at {time_str}")
            except:
                todays_events.append(f"• {event.get('name')}")
    
    return '\n'.join(todays_events) if todays_events else "No calendar events found for today."
