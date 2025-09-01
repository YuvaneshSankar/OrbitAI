from google_auth_oauthlib.flow import InstalledAppFlow

def get_google_calendar_token():
    SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
    flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', SCOPES)
    creds = flow.run_local_server(port=8080)
    return creds.token 

if __name__ == "__main__":
    token = get_google_calendar_token()
    print("Google Calendar Access Token:", token)
