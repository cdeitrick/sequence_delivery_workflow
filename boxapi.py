import json
from pathlib import Path
from typing import Dict

from boxsdk import Client, OAuth2

TOKEN_STORAGE = Path.home() / "box_tokens.json"
PARENT_FOLDER_ID = "63336197339"
DEVELOPER_TOKEN = "1popFVeRf3KpCBNCZkWviCPLazVMGXyS"


def get_credentials() -> Dict[str, str]:
	""" Retrieves the client ID and client secret that have been saved previously."""
	filename = Path.home() / "box_credentials.json"
	data = json.loads(filename.read_text())

	return data['boxAppSettings']


def authorize_with_oauth2():
	""" Uses a developer token to authenticate the app."""
	credentials = get_credentials()

	client_id = credentials['clientID']
	client_secret = credentials['clientSecret']

	auth = OAuth2(
		client_id = client_id,
		client_secret = client_secret,
		access_token = DEVELOPER_TOKEN
	)
	return auth


def store_tokens(access_code: str, refresh_code: str):
	TOKEN_STORAGE.write_text(
		json.dumps(
			{'accessCode': access_code, 'refreshCode': refresh_code},
			indent = 4
		)
	)


def authorize_with_login() -> OAuth2:
	credentials = get_credentials()
	redirect_url = "https://migsapp.com/auth"
	client_id = credentials['clientID']
	client_secret = credentials['clientSecret']

	authorization = OAuth2(
		client_id = client_id,
		client_secret = client_secret
	)

	auth_request_url, csrf_token = authorization.get_authorization_url(redirect_url)
	print("Enter this URL into a browser to authorize the app.")
	print(auth_request_url)
	access_code = input("Please enter the access code: ")
	print("Entered ", access_code)

	access_token, refresh_token = authorization.authenticate(access_code)
	store_tokens(access_token, refresh_token)
	return authorization


CLIENT = Client(authorize_with_oauth2())
FOLDER = CLIENT.folder(PARENT_FOLDER_ID).get(fields = None, etag = None)
if __name__ == "__main__":
	pass
