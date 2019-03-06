import json
from pathlib import Path
from typing import Dict

from boxsdk import Client, OAuth2

TOKEN_STORAGE = Path.home() / "box_tokens.json"

DEVELOPER_TOKEN = "1popFVeRf3KpCBNCZkWviCPLazVMGXyS"


def get_credentials() -> Dict[str, str]:
	""" Retrieves the client ID and client secret that have been saved previously."""
	beagle_path = Path("/home/data/boxapi.txt")
	if beagle_path.exists():
		contents = [i.strip() for i in beagle_path.read_text().split("\n") if i]
		key, secret, folder_id = contents
		data = {
			"boxAppSettings": {
				"clientID":     key,
				"clientSecret": secret
			}
		}
		global PARENT_FOLDER_ID
		PARENT_FOLDER_ID = folder_id
	else:
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


def store_tokens(access_token: str, refresh_token: str):
	TOKEN_STORAGE.write_text(
		json.dumps(
			{'accessToken': access_token, 'refreshToken': refresh_token},
			indent = 4
		)
	)


def parse_url(url: str):
	head, sep, parameters = url.rpartition('/')
	auth, sep, response = parameters.rpartition('?')
	elements = response.split('&')
	data = dict()
	for element in elements:
		key, value = element.split('=')
		data[key] = value
	return data


def authorize_with_login() -> OAuth2:
	credentials = get_credentials()
	redirect_url = "https://migsapp.com/auth"
	client_id = credentials['clientID']
	client_secret = credentials['clientSecret']
	if not TOKEN_STORAGE.exists():
		authorization = OAuth2(
			client_id = client_id,
			client_secret = client_secret,
		store_tokens = store_tokens
		)
		auth_request_url, csrf_token = authorization.get_authorization_url(redirect_url)
		print("Enter this URL into a browser to authorize the app.")
		print(auth_request_url)

		access_code_url = input("Please enter the access code url: ")
		parameters = parse_url(access_code_url)
		access_code = parameters['code']

		access_token, refresh_token = authorization.authenticate(access_code)
		#store_tokens(access_code, access_token, refresh_token)
	else:
		token_data = json.loads(TOKEN_STORAGE.read_text())
		authorization = OAuth2(
			client_id = client_id,
			client_secret = client_secret,
			store_tokens = store_tokens,
			access_token = token_data['accessToken'],
			refresh_token = token_data['refreshToken']
		)
		authorization.refresh(token_data['accessToken'])

	return authorization


#CLIENT = Client(authorize_with_oauth2())
CLIENT = Client(authorize_with_login())
PARENT_FOLDER_ID = "63336197339"
print("parent folder ID: ", PARENT_FOLDER_ID)
FOLDER = CLIENT.folder(PARENT_FOLDER_ID).get(fields = None, etag = None)
if __name__ == "__main__":
	pass
