# -*- coding: utf-8 -*-
"""
Synergy Google Calendar Agent
Loads Google OAuth credentials, lists upcoming items, and logs new events.
"""

import os
import json
import datetime
from typing import List, Dict, Any

class CalendarAgent:
    def __init__(self):
        self.config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.json")
        self.service = None
        self._init_calendar_service()

    def _init_calendar_service(self):
        """Builds a secure connection with Google Calendar API using stored client secrets."""
        if not os.path.exists(self.config_path):
            return

        try:
            with open(self.config_path, "r") as f:
                config = json.load(f)

            cal_config = config.get("google_calendar", {})
            creds_path = cal_config.get("credentials_path", "credentials.json")
            token_path = cal_config.get("token_path", "token.json")

            # Resolve relative pathways based on main app workspace directory
            base_dir = os.path.dirname(os.path.dirname(__file__))
            if creds_path and not os.path.isabs(creds_path):
                creds_path = os.path.join(base_dir, creds_path)
            if token_path and not os.path.isabs(token_path):
                token_path = os.path.join(base_dir, token_path)

            if os.path.exists(token_path) or os.path.exists(creds_path):
                from google.auth.transport.requests import Request
                from google.oauth2.credentials import Credentials
                from google_auth_oauthlib.flow import InstalledAppFlow
                from googleapiclient.discovery import build

                # Scopes for calendar manipulation
                scopes = ['https://www.googleapis.com/auth/calendar']
                creds = None

                if os.path.exists(token_path):
                    creds = Credentials.from_authorized_user_file(token_path, scopes)

                if not creds or not creds.valid:
                    if creds and creds.expired and creds.refresh_token:
                        creds.refresh(Request())
                    elif os.path.exists(creds_path):
                        flow = InstalledAppFlow.from_client_secrets_file(creds_path, scopes)
                        creds = flow.run_local_server(port=0)
                        
                        # Save the credentials for subsequent requests
                        with open(token_path, 'w') as token:
                            token.write(creds.to_json())

                if creds:
                    self.service = build('calendar', 'v3', credentials=creds)
                    print("[*] Google Calendar Agent initialized successfully.")
            else:
                print("[*] Calendar client secrets not configured yet. Running Calendar Agent in dry-run mode.")
        except Exception as e:
            print(f"[!] Warning: Google Calendar API initialization skipped: {e}")
            self.service = None

    def is_configured(self) -> bool:
        return self.service is not None

    def execute_action(self, action: str, query: str = "") -> str:
        """Executes Calendar instructions such as listing upcoming events or booking appointments."""
        if not self.is_configured():
            # Return high-fidelity local tracking response if not authenticated
            now_str = datetime.datetime.now().strftime("%I:%M %p")
            return f"Calendar is using the offline trial mode. Simulated calendar action '{action}' on query '{query}' completed at {now_str}."

        try:
            action = action.lower()
            if "add" in action or "create" in action or "schedule" in action:
                return self.add_event(query)
            else:
                # Default is listing events
                return self.list_events()
        except Exception as e:
            return f"Google Calendar Agent experienced an error: {str(e)}"

    def list_events(self, max_results: int = 5) -> str:
        """Queries Google Calendar for upcoming events on the user's primary schedule."""
        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        events_result = self.service.events().list(
            calendarId='primary',
            timeMin=now,
            singleEvents=True,
            orderBy='startTime',
            maxResults=max_results
        ).execute()
        events = events_result.get('items', [])

        if not events:
            return "You have no upcoming events scheduled on your Google Calendar."

        speech_text = "Here are your next upcoming events: "
        event_descriptions = []
        for event in events:
            summary = event.get('summary', 'Untitled Event')
            start = event.get('start', {}).get('dateTime', event.get('start', {}).get('date', ''))
            
            # Format date friendly for TTS
            if "T" in start:
                dt = datetime.datetime.fromisoformat(start.split("+")[0])
                date_str = dt.strftime("%B %d at %I:%M %p")
            else:
                date_str = start # All-day date

            event_descriptions.append(f"'{summary}' scheduled on {date_str}")

        return speech_text + ". ".join(event_descriptions) + "."

    def add_event(self, description: str) -> str:
        """Uses description elements to create a quick insert event on calendar."""
        # Clean query keyword references like "add event block"
        cleaned_desc = description.replace("add event", "").replace("schedule event", "").strip()
        if not cleaned_desc:
            cleaned_desc = "Quick Meeting with Synergy"

        # Design simple default start (1 hour from now)
        start_time = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        end_time = start_time + datetime.timedelta(hours=1)
        
        event_body = {
            'summary': cleaned_desc,
            'description': 'Created automatically by Synergy voice-activated desktop assistant',
            'start': {
                'dateTime': start_time.isoformat() + 'Z',
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': end_time.isoformat() + 'Z',
                'timeZone': 'UTC',
            },
        }

        created_event = self.service.events().insert(calendarId='primary', body=event_body).execute()
        event_link = created_event.get('htmlLink', '')
        summary = created_event.get('summary', 'Meeting')
        
        formatted_time = (datetime.datetime.now() + datetime.timedelta(hours=1)).strftime("%I:%M %p")
        return f"Successfully added event '{summary}' to your calendar for {formatted_time} today."
