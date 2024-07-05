import json

from django.conf import settings
from firebase_admin import credentials, auth, initialize_app, _token_gen


with open("firebase-admin-sdk.json") as json_data:
    firebase_config = json.load(json_data)

cred = credentials.Certificate(firebase_config)
default_app = initialize_app(
    cred, {"databaseURL": settings.FIREBASE_CONFIG["databaseURL"]}
)


def generate_firebase_link_for_auth(email):
    action_code_settings = auth.ActionCodeSettings(
        url=settings.DEEP_LINK_APP_URL,
        handle_code_in_app=False,
        dynamic_link_domain=settings.DEEP_LINK_DOMAIN,
    )
    return auth.generate_sign_in_with_email_link(email, action_code_settings)
