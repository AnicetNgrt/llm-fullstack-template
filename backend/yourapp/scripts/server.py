import logging
import os
import argparse
from flask import Flask
from flask_cors import CORS, cross_origin
from supabase import create_client, Client as SupabaseClient
from dotenv import load_dotenv

from yourapp.auth.controller import init_auth_routes
from yourapp.chat.controller import init_chat_routes
from yourapp.sessions import close_all_open_sessions
from yourapp.sessions.controller import add_sessions_routes
from yourapp.user.controller import init_user_routes
from yourapp.utils.logging import setup_simple_logger


load_dotenv()

SUPABASE_PROJECT_URL: str = os.getenv("SUPABASE_PROJECT_URL")
SUPABASE_PRIVATE_API_KEY: str = os.getenv("SUPABASE_PRIVATE_API_KEY")
SUPABASE_PUBLIC_API_KEY: str = os.getenv("SUPABASE_PUBLIC_API_KEY")
supabase: SupabaseClient = create_client(SUPABASE_PROJECT_URL, SUPABASE_PRIVATE_API_KEY)

APP_SECRET = os.getenv("APP_SECRET")

app = Flask(__name__)
CORS(app)


login_required, supbase_user_client_required = init_auth_routes(
    app,
    APP_SECRET,
    SUPABASE_PROJECT_URL,
    SUPABASE_PUBLIC_API_KEY,
    admin_client=supabase,
)
init_chat_routes(app, login_required, supabase)
init_user_routes(app, login_required, supabase)
add_sessions_routes(app, login_required, supabase)


@app.route("/")
@cross_origin()
def index():
    return "Yourapp API"


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, default="localhost", help="Host address")
    parser.add_argument("--port", type=int, default=5000, help="Port number")
    parser.add_argument("--trace", action="store_true", help="Enable trace logging")

    args = parser.parse_args()

    log_level = (
        "trace"
        if args.trace
        else ("debug" if os.getenv("ENVIRONMENT") == "dev" else "info")
    )
    setup_simple_logger(log_level, log_file=".logs/" + os.path.basename(__file__) + ".{time:YYYY-MM-DD_HH-mm-ss!UTC}.log")

    logging.getLogger("werkzeug").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)

    close_all_open_sessions(supabase)

    app.run(host=args.host, port=args.port)
