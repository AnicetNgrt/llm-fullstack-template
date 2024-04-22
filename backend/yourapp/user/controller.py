from flask import jsonify
from flask_cors import cross_origin
from supabase import Client as SupabaseClient

from yourapp.user import get_user_infos


def init_user_routes(app, login_required, client: SupabaseClient):
    @app.route("/user", methods=["GET"])
    @cross_origin()
    @login_required
    def get_user(user_id):
        infos = get_user_infos(client, user_id)
        return jsonify(infos)
