import json
from datetime import datetime
from typing import List, Dict, Any


# Function to sort events chronologically 
def sort_events_by_time(events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    #Sort events by timestamp in ascending order.
    sorted_list = []
    for event in events:
        sorted_list.append(event)
    
    return sorted(sorted_list, key=lambda e: datetime.fromisoformat(e["timestamp"].replace("Z", "+00:00")))


# Event classification logic
def classify_event(event_text: str, event_source: str) -> str:
  
    #Basic rule-based classifier for events.
    text = event_text.lower()  
    
    # Team/internal stuff
    team_keywords = ["team update", "deadline", "sprint", "review", "standup"]
    for keyword in team_keywords:
        if keyword in text:
            return "team_update"
    
    # External communications
    if event_source == "email":
        return "external_comm"
    # Also checking for client mentions regardless of source
    external_keywords = ["client", "customer", "partner"]
    if any(word in text for word in external_keywords):
        return "external_comm"
    
    # System issues and alerts
    system_problems = ["error", "alert", "timeout", "failed"]
    for problem in system_problems:
        if problem in text:
            return "system_alert"
    
    # Default case - everything else goes here
    return "misc"


def normalize_events(events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    #Transform events into our standard timeline format.
    normalized_events = []
    
    for event in events:
        normalized_event = {
            "t": event["timestamp"],
            "source": event["source"],         
            "type": classify_event(event["text"], event["source"]),
            "text": event["text"]            
        }
        normalized_events.append(normalized_event)
    
    return normalized_events


def build_timeline(raw_events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:

    #Main pipeline function - takes raw JSON events and returns processed timeline.
    # Step 1: Sort by timestamp
    events_sorted = sort_events_by_time(raw_events)
    
    # Step 2: Normalize and classify
    final_timeline = normalize_events(events_sorted)
    
    return final_timeline


if __name__ == "__main__":
    # Sample data for testing - keeping this realistic
    test_events = [
        {"timestamp": "2025-12-05T08:10:00Z", "source": "slack", "text": "Team update: sprint retrospective notes"},
        {"timestamp": "2025-12-05T08:09:30Z", "source": "email", "text": "Client escalated an issue with the API"},
        {"timestamp": "2025-12-03T08:12:45Z", "source": "system", "text": "Error: connection timeout"},
        {"timestamp": "2025-12-05T08:11:30Z", "source": "slack", "text": "Reminder: review the new deadline"},
        {"timestamp": "2025-12-04T08:13:00Z", "source": "email", "text": "Weekly newsletter..."}
    ]
    
    # Process the events
    result = build_timeline(test_events)
    
    # Pretty print the output
    print(json.dumps(result, indent=2))


# Expected result should match this structure:
'''
[
  {
    "t": "2025-12-03T08:12:45Z",
    "source": "system",
    "type": "system_alert",
    "text": "Error: connection timeout"
  },
  {
    "t": "2025-12-04T08:13:00Z", 
    "source": "email",
    "type": "external_comm",
    "text": "Weekly newsletter..."
  },
  {
    "t": "2025-12-05T08:09:30Z",
    "source": "email", 
    "type": "external_comm",
    "text": "Client escalated an issue with the API"
  },
  {
    "t": "2025-12-05T08:10:00Z",
    "source": "slack",
    "type": "team_update", 
    "text": "Team update: sprint retrospective notes"
  },
  {
    "t": "2025-12-05T08:11:30Z",
    "source": "slack",
    "type": "team_update",
    "text": "Reminder: review the new deadline"
  }
]
'''