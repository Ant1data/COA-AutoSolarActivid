import os
import json
from datetime import datetime
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

# ============================================================
# 1. Chargement du token OAuth depuis l'environnement
# ============================================================

raw_token = os.environ.get("YOUTUBE_TOKEN_JSON") or os.environ.get("YOUTUBE_TOKEN")

if not raw_token:
    raise RuntimeError(
        "Missing YOUTUBE_TOKEN_JSON or YOUTUBE_TOKEN in environment variables"
    )

try:
    token_info = json.loads(raw_token)
except json.JSONDecodeError as e:
    raise RuntimeError("Invalid JSON in YOUTUBE_TOKEN_JSON") from e

creds = Credentials.from_authorized_user_info(
    token_info,
    scopes=["https://www.googleapis.com/auth/youtube.upload"],
)

# ============================================================
# 2. Client YouTube API
# ============================================================

youtube = build("youtube", "v3", credentials=creds)

# ============================================================
# 3. Paramètres vidéo (via variables d'environnement)
# ============================================================

video_path = os.environ.get("YOUTUBE_VIDEO_PATH")
coa_type = os.environ.get("COA_TYPE", "DAILY").upper()
coa_date_label = os.environ.get("COA_DATE_LABEL")

if not video_path or not os.path.exists(video_path):
    raise RuntimeError(f"Video file not found: {video_path}")

if not coa_date_label:
    coa_date_label = datetime.utcnow().strftime("%Y-%m-%d")

# ============================================================
# 4. Titre, description, tags (Shorts publics)
# ============================================================

title = f"COA {coa_type} {coa_date_label} #cosmic #radiation #airplane #spaceweather #solarflare"

description = (
    "Data Sources & Credits\n"
    "SOHO LASCO C2 – © NASA/ESA: https://soho.nascom.nasa.gov\n"
    "GOES Proton Flux – NOAA SWPC: https://services.swpc.noaa.gov\n"
    "NMDB Neutron Monitor Database: https://www.nmdb.eu\n\n"
    "Thanks to the providers of public data.\n"
    "Attribution overlays appear on each segment."
)

tags = [
    "cosmic",
    "radiation",
    "airplane",
    "spaceweather",
    "solarflare",
    "cosmic on air",
    "COA",
]

# ============================================================
# 5. Upload YouTube
# ============================================================

request = youtube.videos().insert(
    part="snippet,status",
    body={
        "snippet": {
            "title": title[:100],  # sécurité limite YouTube
            "description": description,
            "tags": tags,
            "categoryId": "28",  # Science & Technology
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False,
        },
    },
    media_body=MediaFileUpload(
        video_path,
        chunksize=-1,
        resumable=True,
    ),
)

print("📤 Upload YouTube en cours...")
response = request.execute()

video_id = response.get("id")
if not video_id:
    raise RuntimeError("Upload failed: no video ID returned")

print(f"✅ Upload terminé : https://www.youtube.com/shorts/{video_id}")
