import json
from pathlib import Path
from typing import List, Dict



def get_email_credentials(filename: Path = Path.home() / "email_credentials.json"):
	"""
		Opens a json file with the keys `emailAddress` and `emailPassword`
	Parameters
	----------
	filename

	Returns
	-------
	"""
	data = json.loads(filename.read_text())
	return data


def send_email(message, attachments: List[Path] = None):
	import smtplib
	from email.mime.text import MIMEText
	from email.mime.multipart import MIMEMultipart

	credentials = get_email_credentials()
	email = credentials['emailAddress']
	password = credentials['emailPassword']
	send_to_email = 'cld100@pitt.edu'
	subject = "Sequence Upload"
	msg = MIMEMultipart()
	msg['From'] = email
	msg['To'] = send_to_email
	msg['Subject'] = subject

	msg.attach(MIMEText(message, 'plain'))

	server = smtplib.SMTP('smtp.gmail.com', 587)
	server.starttls()
	server.login(email, password)
	text = msg.as_string()
	server.sendmail(email, send_to_email, text)
	server.quit()

def generate_email(projects:Dict[str,Dict]):
	import yaml

	body = yaml.dump(projects, default_flow_style = False)
	print(body)
	send_email(body)

if __name__ == "__main__":
	send_email()
