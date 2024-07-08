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


def get_credentails_from_id_token(id_token):
    try:
        decoded_token = auth.verify_id_token(id_token)
    except _token_gen.ExpiredIdTokenError:
        return None
    firebase_user_id = decoded_token["user_id"]
    sign_in_provider = decoded_token["firebase"]["sign_in_provider"]
    user_from_user_id = auth.get_user(firebase_user_id)
    provider_related_data = list(
        filter(
            lambda x: x.provider_id == sign_in_provider, user_from_user_id.provider_data
        )
    )[0]
    first_name = ""
    last_name = ""
    if provider_related_data.display_name:
        splitted_name = provider_related_data.display_name.strip().split(" ", 1)
        if len(splitted_name) > 1:
            first_name, last_name = splitted_name
        else:
            first_name = splitted_name[0]
    return {
        "auth_time": decoded_token["auth_time"],
        "token_issued_on": decoded_token["iat"],
        "token_expires_on": decoded_token["exp"],
        "email": decoded_token["email"],
        "additional_email": provider_related_data.email,
        "firebase_user_id": firebase_user_id,
        "first_name": first_name,
        "last_name": last_name,
        "photo_url": provider_related_data.photo_url or "",
        "email_verified": decoded_token["email_verified"],
    }
