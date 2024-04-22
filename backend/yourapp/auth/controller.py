from flask import request, jsonify
from functools import wraps
from supabase import Client as SupabaseClient

from flask_cors import cross_origin
from yourapp.auth.providers import SupabaseAuthProvider
from yourapp.auth import try_unwrap_jwt
from yourapp.user import get_user_infos, onboard_user


def init_auth_routes(
    app,
    app_secret: str,
    supabase_project_url: str,
    supabase_public_api_key: str,
    admin_client: SupabaseClient,
):
    @app.route("/login", methods=["POST"])
    @cross_origin()
    def login():
        credentials = request.json

        auth_provider = SupabaseAuthProvider(
            supabase_public_api_key, supabase_project_url
        )

        if auth_provider is None:
            return jsonify({"error": "Invalid credentials"}), 401

        access_token = auth_provider.authenticate(app_secret, credentials)
        if access_token is None:
            return jsonify({"error": "Invalid credentials"}), 401

        user_id, _, _ = try_unwrap_jwt(app_secret, access_token)

        # TODO: Add a big warning here of the user_id is None

        user_infos = get_user_infos(admin_client, user_id)
        if user_infos is None:
            return jsonify({"error": "Access failure"}), 500
        if user_infos.id == "NOT_FOUND":
            return jsonify({"token": access_token, "first_time_user": True})

        return jsonify({"token": access_token})

    def login_required(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            token = request.args.get("token")

            if token is None:
                return jsonify({"error": "Unauthorized"}), 401

            result = try_unwrap_jwt(app_secret, token)
            if result is None:
                return jsonify({"error": "Unauthorized"}), 401

            user_id, _, _ = result

            if user_id is None:
                return jsonify({"error": "Unauthorized"}), 401

            return func(*args, **kwargs, user_id=user_id)

        return wrapper

    def supbase_user_client_required(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            token = request.args.get("token")
            user_id, email, password = try_unwrap_jwt(app_secret, token)
            client = SupabaseClient(supabase_project_url, supabase_public_api_key)
            data = client.auth.sign_in_with_password(
                {"email": email, "password": password}
            )
            if data is None:
                return jsonify({"error": "Unauthorized"}), 401
            if user_id is None:
                return jsonify({"error": "Unauthorized"}), 401

            return func(*args, **kwargs, user_id=user_id, client=client)

        return wrapper

    @app.route("/user/onboarding", methods=["POST"])
    @cross_origin()
    @supbase_user_client_required
    def onboarding(user_id, client: SupabaseClient):
        data = request.json
        if "username" not in data:
            return jsonify({"error": "Missing username"}), 400
        if "password" not in data:
            return jsonify({"error": "Missing password"}), 400

        result = onboard_user(
            client, admin_client, user_id, data["username"], data["password"]
        )
        client.auth.sign_out()
        if result is None:
            return jsonify({"error": "Onboarding failed"}), 500
        return jsonify({})

    return login_required, supbase_user_client_required
