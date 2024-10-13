# TISS Reservations Filter

This project provides a script to filter events from an iCal calendar feed, create a new iCal file with the filtered events, and upload it to a GitHub repository. It is designed to automate the process of filtering calendar events based on specific time ranges and upload the updated calendar file to GitHub.

## Features

- Fetch events from an iCal URL.
- Filter events 
- Change name of events  
- Create a new iCal file with the filtered events.
- Upload the new iCal file to a specified GitHub repository.

## Requirements

- Python 3.x
- requests library
- icalendar library

## Installation

1. Clone the repository:
   `bash
   git clone https://github.com/xMoZz/tiss-reservations-filter.git
   cd tiss-reservations-filter`
   

2. Install the required libraries:
   bash
   pip install requests icalendar
   

## Configuration

Edit the `config.json` file to update the configuration settings:
- api_url: The URL of your iCal feed.
- github_token: Your GitHub token for authentication.
- github_repository: Your repository directory
- github_name: Your name on Github
- file_name: The name of the iCal file to be created and uploaded to github.

## Usage

Run the script:
bash
python filter\ calendar.py


The script will:
1. Fetch events from the specified iCal feed.
2. Filter events outside the 8 AM to 8 PM time range.
3. Change the name of the events to shorter more readable names (you have to configure your prefered names and which events should be renamed yourself).
3. Create a new iCal file with the filtered events.
4. Upload the new iCal file to the specified GitHub repository (from where you can host it on a website, in order to add it as an URL into a prefered calendar service).

The script will repeat this process every 24 hours since most calendar services only sinc once a day.
