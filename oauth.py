from oauthlib.oauth2 import WebApplicationClient
import requests
from flask import current_app
import json

def get_google_provider_cfg():
    try:
        return requests.get(current_app.config['GOOGLE_DISCOVERY_URL']).json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching Google provider config: {e}")
        return None

def create_oauth_client():
    try:
        return WebApplicationClient(current_app.config['GOOGLE_CLIENT_ID'])
    except Exception as e:
        print(f"Error creating OAuth client: {e}")
        return None
