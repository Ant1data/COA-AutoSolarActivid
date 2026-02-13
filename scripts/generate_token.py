from google_auth_oauthlib.flow import InstalledAppFlow
import os
from pathlib import Path

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
ROOT = Path(__file__).resolve().parents[1]
CLIENT_SECRET_FILE = str((ROOT / "client_secret.json").resolve())

if not os.path.exists(CLIENT_SECRET_FILE):
    raise FileNotFoundError(f"{CLIENT_SECRET_FILE} introuvable.")

flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
creds = flow.run_local_server(port=0)

with open(str((ROOT / "token.json").resolve()), "w") as f:
    f.write(creds.to_json())

print("✅ token.json généré avec succès")