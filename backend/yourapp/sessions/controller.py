from flask import jsonify
from flask_cors import cross_origin
from supabase import Client as SupabaseClient

from yourapp.sessions import get_sessions, get_session


def add_sessions_routes(app, login_required, admin_client: SupabaseClient):
    @app.route("/sessions", methods=["GET"])
    @cross_origin()
    @login_required
    def fetch_sessions(user_id):
        sessions = get_sessions(admin_client, user_id)
        if sessions is None:
            return jsonify({"error": "Internal server error"}), 500
        return jsonify({"sessions": [session.to_dict() for session in sessions]})

    @app.route("/sessions/<session_id>", methods=["GET"])
    @cross_origin()
    @login_required
    def fetch_session(user_id, session_id):
        session = get_session(admin_client, int(session_id))
        if session is None:
            return jsonify({"error": "Session not found"}), 404
        return jsonify(session.to_dict())
