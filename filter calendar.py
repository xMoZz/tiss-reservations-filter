import requests
from icalendar import Calendar, Event
from datetime import datetime, time
import base64
import time as time2

# Config:
api_url = "your-tiss-api-url" 
github_token = "your-github-token" 



#------------------------------------------------------------

def get_events_from_ical(api):
    response = requests.get(api)
    if response.status_code == 200:
        ical_data = response.content
        calendar = Calendar.from_ical(ical_data)
        
        events = []
        for component in calendar.walk():
            if component.name == "VEVENT":
                event_details = {
                    "summary": component.get('summary'),
                    "start": component.get('dtstart').dt,
                    "end": component.get('dtend').dt,
                    "location": component.get('location'),
                    "description": component.get('description'),
                }
                events.append(event_details)
        return events
    else:
        print(f"Error fetching events: {response.status_code}")
        return []


def filter_events(events):
    # Define the time range boundaries
    start_time = time(8, 0)
    end_time = time(20, 0)

    def get_event_time(event_time):
        if isinstance(event_time, datetime):  # If it's a datetime object, extract the time
            return event_time.time()
        else:  # If it's a date object, assume the event starts at midnight
            return time(0, 0)


    filtered_events = []
    
    for event in events:
        event_start_time = get_event_time(event['start'])
        event_end_time = get_event_time(event['end'])
        
        if event_end_time != end_time or event_start_time != start_time:  # Check if the event is within the time range
            filtered_events.append(event)

    events[:] = filtered_events
    
    return events


def create_ical(events):
    # Create a new calendar object
    calendar = Calendar()

    for event in events:
        # Create an Event object instead of a dictionary
        event_component = Event()
        event_component.add('summary', event['summary'])
        event_component.add('dtstart', event['start'])
        event_component.add('dtend', event['end'])
        event_component.add('location', event.get('location', ''))  # Use get() to avoid errors
        event_component.add('description', event.get('description', ''))  # Use get() to avoid errors

        # Add the event to the calendar
        calendar.add_component(event_component)

    # Convert the calendar to iCal format
    ical_data = calendar.to_ical()
    return ical_data


def get_file(ical_data):
    with open("filtered_calendar.ics", "wb") as f:
        f.write(ical_data)
    return "filtered_calendar.ics"

def upload_to_dropbox(filename, dropbox_access_token):
    dbx = dropbox.Dropbox(dropbox_access_token)
    
    with open(filename, "rb") as f:
        dbx.files_upload(f.read(), f'/{filename}', mute=True, mode=dropbox.files.WriteMode.overwrite)
    



def github_upload(filename, repo_owner, repo_name, branch='main', commit_message='Upload file'):
    # Read the file content
    with open(filename, 'rb') as f:
        content = f.read()
    
    # Encode the content in base64
    encoded_content = base64.b64encode(content).decode('utf-8')
    
    # Prepare the API URL
    url = f'https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{filename}'
    
    # Get the SHA of the existing file, if it exists
    response = requests.get(url, headers={
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github.v3+json"
    })
    
    sha = None
    if response.status_code == 200:  # File exists
        sha = response.json().get('sha')
    
    # Prepare the data payload for the request
    data = {
        'message': commit_message,
        'content': encoded_content,
        'branch': branch
    }
    
    if sha:  # If the file exists, include the SHA for updating
        data['sha'] = sha
    
    # Make the PUT request to upload or update the file
    response = requests.put(url, json=data, headers={
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github.v3+json"
    })
    
    if response.status_code in (201, 200):  # 201 Created or 200 OK (updated)
        print('File uploaded successfully.')
    else:
        print('Failed to upload file:', response.json())







#------------------------------------------------------------

def main():
    while True: 
        events = get_events_from_ical(api_url)
        filtered_events = filter_events(events)
        ical_data = create_ical(filtered_events)
        path = get_file(ical_data)
        github_upload("filtered_calendar.ics", "your-github-name", "your-repository", branch='main', commit_message='Upload file')

        print("Waiting for 24 hours...")
        time2.sleep(60*60*24) #wait a day cause google cal only updates once a day
        


if __name__ == "__main__":
    main()
