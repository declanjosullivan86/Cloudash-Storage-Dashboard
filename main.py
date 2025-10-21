import os
from flask import Flask, request, redirect, session, url_for, jsonify, render_template
from requests_oauthlib import OAuth2Session
import json

# --- Load Configuration from config.json ---
try:
    with open('config.json') as config_file:
        config = json.load(config_file)
except FileNotFoundError:
    # Exit gracefully if config.json is not found.
    print("ERROR: `config.json` not found. Please create it by copying `config.json.example` and filling in your credentials.")
    exit()
except json.JSONDecodeError:
    print("ERROR: Could not decode `config.json`. Please ensure it is valid JSON.")
    exit()


# --- Application Setup ---
app = Flask(__name__, template_folder='templates', static_folder='static')
# Use the secret key from the config file.
app.secret_key = config.get("FLASK_SECRET_KEY")
if not app.secret_key:
    print("ERROR: FLASK_SECRET_KEY not found in config.json. Please set it.")
    exit()

# --- Google Drive Configuration ---
GOOGLE_CLIENT_ID = config.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = config.get("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = 'http://127.0.0.1:5000/callback/google'
GOOGLE_AUTH_URL = 'https://accounts.google.com/o/oauth2/v2/auth'
GOOGLE_TOKEN_URL = 'https://www.googleapis.com/oauth2/v4/token'
GOOGLE_SCOPE = ['https://www.googleapis.com/auth/drive.metadata.readonly', 'https://www.googleapis.com/auth/userinfo.email']
GOOGLE_API_URL = 'https://www.googleapis.com/drive/v3/about?fields=storageQuota,user'

# --- Dropbox Configuration ---
DROPBOX_CLIENT_ID = config.get("DROPBOX_CLIENT_ID")
DROPBOX_CLIENT_SECRET = config.get("DROPBOX_CLIENT_SECRET")
DROPBOX_REDIRECT_URI = 'http://127.0.0.1:5000/callback/dropbox'
DROPBOX_AUTH_URL = 'https://www.dropbox.com/oauth2/authorize'
DROPBOX_TOKEN_URL = 'https://api.dropbox.com/oauth2/token'
DROPBOX_API_URL_SPACE = 'https://api.dropboxapi.com/2/users/get_space_usage'
DROPBOX_API_URL_ACCOUNT = 'https://api.dropboxapi.com/2/users/get_current_account'

# --- OneDrive Configuration ---
ONEDRIVE_CLIENT_ID = config.get("ONEDRIVE_CLIENT_ID")
ONEDRIVE_CLIENT_SECRET = config.get("ONEDRIVE_CLIENT_SECRET")
ONEDRIVE_REDIRECT_URI = 'http://127.0.0.1:5000/callback/onedrive'
ONEDRIVE_AUTH_URL = 'https://login.microsoftonline.com/common/oauth2/v2.0/authorize'
ONEDRIVE_TOKEN_URL = 'https://login.microsoftonline.com/common/oauth2/v2.0/token'
ONEDRIVE_SCOPE = ['https://graph.microsoft.com/Files.Read.All', 'https://graph.microsoft.com/User.Read']
ONEDRIVE_API_URL = 'https://graph.microsoft.com/v1.0/me/drive'


# --- Helper Functions ---
def save_token(provider, token):
    """Saves token dictionary to session."""
    session[f'{provider}_token'] = token
    session.modified = True

def get_token(provider):
    """Retrieves token from session."""
    return session.get(f'{provider}_token')

# --- Frontend Routes ---
@app.route('/')
def index():
    """Serves the main HTML page."""
    return render_template('index.html')

# --- Authentication Routes ---
@app.route('/login/<provider>')
def login(provider):
    """Redirects user to the provider's OAuth 2.0 consent screen."""
    if provider == 'google':
        if not all([GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET]):
            return "Google credentials not configured on server.", 500
        google = OAuth2Session(GOOGLE_CLIENT_ID, scope=GOOGLE_SCOPE, redirect_uri=GOOGLE_REDIRECT_URI)
        authorization_url, state = google.authorization_url(GOOGLE_AUTH_URL, access_type="offline", prompt="select_account")
        session['oauth_state'] = state
        return redirect(authorization_url)

    if provider == 'dropbox':
        if not all([DROPBOX_CLIENT_ID, DROPBOX_CLIENT_SECRET]):
            return "Dropbox credentials not configured on server.", 500
        dropbox = OAuth2Session(DROPBOX_CLIENT_ID, redirect_uri=DROPBOX_REDIRECT_URI)
        authorization_url, state = dropbox.authorization_url(DROPBOX_AUTH_URL)
        session['oauth_state'] = state
        return redirect(authorization_url)

    if provider == 'onedrive':
        if not all([ONEDRIVE_CLIENT_ID, ONEDRIVE_CLIENT_SECRET]):
            return "OneDrive credentials not configured on server.", 500
        onedrive = OAuth2Session(ONEDRIVE_CLIENT_ID, scope=ONEDRIVE_SCOPE, redirect_uri=ONEDRIVE_REDIRECT_URI)
        authorization_url, state = onedrive.authorization_url(ONEDRIVE_AUTH_URL, prompt="select_account")
        session['oauth_state'] = state
        return redirect(authorization_url)

    return 'Unknown provider', 404

# --- Callback Routes ---
@app.route('/callback/<provider>')
def callback(provider):
    """Handles the redirect back from the provider after authorization."""
    if provider == 'google':
        google = OAuth2Session(GOOGLE_CLIENT_ID, state=session.get('oauth_state'), redirect_uri=GOOGLE_REDIRECT_URI)
        token = google.fetch_token(GOOGLE_TOKEN_URL, client_secret=GOOGLE_CLIENT_SECRET, authorization_response=request.url)
        save_token('google', token)

    if provider == 'dropbox':
        dropbox = OAuth2Session(DROPBOX_CLIENT_ID, state=session.get('oauth_state'), redirect_uri=DROPBOX_REDIRECT_URI)
        token = dropbox.fetch_token(DROPBOX_TOKEN_URL, client_secret=DROPBOX_CLIENT_SECRET, authorization_response=request.url)
        save_token('dropbox', token)
    
    if provider == 'onedrive':
        onedrive = OAuth2Session(ONEDRIVE_CLIENT_ID, state=session.get('oauth_state'), redirect_uri=ONEDRIVE_REDIRECT_URI)
        token = onedrive.fetch_token(ONEDRIVE_TOKEN_URL, client_secret=ONEDRIVE_CLIENT_SECRET, authorization_response=request.url)
        save_token('onedrive', token)

    return redirect(url_for('index'))

# --- API Routes ---
@app.route('/api/accounts')
def get_accounts_data():
    """Fetches and returns data for all connected accounts."""
    accounts = []
    
    # Google Drive
    if GOOGLE_CLIENT_ID and get_token('google'):
        try:
            google = OAuth2Session(GOOGLE_CLIENT_ID, token=get_token('google'))
            response = google.get(GOOGLE_API_URL).json()
            accounts.append({
                'id': 'google',
                'provider': 'Google Drive',
                'email': response['user']['emailAddress'],
                'storageUsed': round(int(response['storageQuota']['usage']) / (1024**3), 2),
                'storageTotal': round(int(response['storageQuota']['limit']) / (1024**3), 2),
                'fileCount': None, # Google Drive API for total file count is complex/paginated
                'status': 'connected'
            })
        except Exception as e:
            print(f"Error fetching Google Drive data: {e}")
            accounts.append({'id': 'google', 'provider': 'Google Drive', 'status': 'error'})

    # Dropbox
    if DROPBOX_CLIENT_ID and get_token('dropbox'):
        try:
            token = get_token('dropbox')
            headers = {'Authorization': f"Bearer {token['access_token']}"}
            space_response = OAuth2Session().post(DROPBOX_API_URL_SPACE, headers=headers).json()
            account_response = OAuth2Session().post(DROPBOX_API_URL_ACCOUNT, headers=headers).json()
            accounts.append({
                'id': 'dropbox',
                'provider': 'Dropbox',
                'email': account_response['email'],
                'storageUsed': round(space_response['used'] / (1024**3), 2),
                'storageTotal': round(space_response['allocation']['allocated'] / (1024**3), 2),
                'fileCount': None, # Dropbox API for total file count is complex/paginated
                'status': 'connected'
            })
        except Exception as e:
            print(f"Error fetching Dropbox data: {e}")
            accounts.append({'id': 'dropbox', 'provider': 'Dropbox', 'status': 'error'})
            
    # OneDrive
    if ONEDRIVE_CLIENT_ID and get_token('onedrive'):
        try:
            onedrive = OAuth2Session(ONEDRIVE_CLIENT_ID, token=get_token('onedrive'))
            response = onedrive.get(ONEDRIVE_API_URL).json()
            user_response = onedrive.get('https://graph.microsoft.com/v1.0/me').json()
            accounts.append({
                'id': 'onedrive',
                'provider': 'OneDrive',
                'email': user_response['userPrincipalName'],
                'storageUsed': round(response['quota']['used'] / (1024**3), 2),
                'storageTotal': round(response['quota']['total'] / (1024**3), 2),
                'fileCount': response.get('folder', {}).get('childCount'), # Top-level item count
                'status': 'connected'
            })
        except Exception as e:
            print(f"Error fetching OneDrive data: {e}")
            accounts.append({'id': 'onedrive', 'provider': 'OneDrive', 'status': 'error'})

    return jsonify(accounts)

@app.route('/api/disconnect/<provider>')
def disconnect(provider):
    """Disconnects a provider by clearing its token from the session."""
    if f'{provider}_token' in session:
        del session[f'{provider}_token']
        session.modified = True
    return jsonify({'status': 'disconnected'})


if __name__ == '__main__':
    # For development, SSL is not strictly required, but OAuth providers
    # often prefer or require HTTPS for callback URLs in production.
    app.run(host='127.0.0.1', port=5000, debug=True)

