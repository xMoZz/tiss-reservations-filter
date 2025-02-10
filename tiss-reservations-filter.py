import requests
from icalendar import Calendar, Event
from datetime import datetime, time
import base64
import time as time2
import json


#load config:
with open("config.json") as f:
    config = json.load(f)
    api_url = config["api_url"]
    github_token = config["github_token"]
    github_repository = config["github_repository"]
    github_name = config["github_name"]
    file_name = config["file_name"]

#--------------------------------------------

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


def filter_spk(events):
    # Define the time range boundaries (here 8 tp 20 because spks start and end at 8 and 20)
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
        
        if event_end_time != end_time or event_start_time != start_time:  # filter spk events
            filtered_events.append(event)

    events[:] = filtered_events
    return events

def name_change(events):
    for event in events:
        if event['summary'] == "101.A26 VU Angleichungskurs Mathematik":
            event['summary'] = "AKMath (101.A26 VU)"
        elif event['summary'] == "101.A27 VU Angleichungskurs Mathematik für INF und WINF":
            event['summary'] = "AKMath (101.A27 VU)"
        elif event['summary'] == "192.134 VU Grundzüge digitaler Systeme":
            event['summary'] = "GdS (192.134 VU)"
        elif event['summary'] == "185.A91 VU Einführung in die Programmierung 1":
            event['summary'] = "EP1 (185.A91 VU)"
        elif event['summary'] == "104.631 VU Mathematisches Arbeiten für Informatik und Wirtschaftsinformatik":
            event['summary'] = "MAI (104.631 VU)"
        elif event['summary'] == "104.633 VU Algebra und Diskrete Mathematik für Informatik und Wirtschaftsinformatik":
            event['summary'] = "AdM (104.633 VU)"
        elif event['summary'] == "187.B12 VU Denkweisen der Informatik":
            event['summary'] = "Denki (187.B12 VU)"
        elif event['summary'] == "180.766 VU Orientierung Informatik und Wirtschaftsinformatik":
            event['summary'] = "Orientierung (180.766 VU)"

        # 2. Semester:
        elif event['summary'] == "186.866 VU Algorithmen und Datenstrukturen":
            event['summary'] = "AlgoDat (186.866 VU)"
        elif event['summary'] == "185.A92 VU Einführung in die Programmierung 2":
            event['summary'] = "EP2 (185.A92 VU)"
        elif event['summary'] == "191.003 VU Computersysteme":
            event['summary'] = "Computersysteme (191.003 VU)"
        elif event['summary'] == "184.686 VU Datenbanksysteme":
            event['summary'] = "Datenbanksysteme (184.686 VU)"
        elif event['summary'] == "104.634 VU Analysis für Informatik und Wirtschaftsinformatik":
            event['summary'] = "Analysis (104.634 VU)"


        #Gruppen:
        elif event['summary'].startswith("104.633 VU Algebra und Diskrete Mathematik für Informatik und Wirtschaftsinformatik - Gruppe"):
            event['summary'] = "AdM (104.633 VU) - Übungsgruppe"
        elif event['summary'].startswith("104.631 VU Mathematisches Arbeiten für Informatik und Wirtschaftsinformatik -"):
            event['summary'] = "MAI (104.631 VU) - Übungsgruppe"
        elif event['summary'].startswith("185.A91 VU Einführung in die Programmierung 1 - "):
            event['summary'] = "EP1 (185.A91 VU) - Übungsgruppe"
    return events



def create_ical(events):
    calendar = Calendar()

    for event in events:
        event_component = Event()
        event_component.add('summary', event['summary'])
        event_component.add('dtstart', event['start'])
        event_component.add('dtend', event['end'])
        event_component.add('location', event.get('location', ''))
        event_component.add('description', event.get('description', ''))

        calendar.add_component(event_component)

    #back to ical
    ical_data = calendar.to_ical()
    with open(file_name, "wb") as f:
        f.write(ical_data)
    return file_name


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


#--------------------------------------------


def main():
    while True: 
        events = get_events_from_ical(api_url)

        events = filter_spk(events)
        events = name_change(events)

        ical_data = create_ical(events)

        github_upload(file_name, github_name, github_repository, branch='main', commit_message='Updated calendar file!')

        print("Waiting for 24 hours...")
        time2.sleep(60*60*24) #wait a day cause google cal only updates once a day
        

if __name__ == "__main__":
    main()
