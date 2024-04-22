import jwt


def try_unwrap_jwt(app_secret: str, token: str) -> tuple[str, str, str]:
    try:
        decoded = jwt.decode(token, app_secret, algorithms=["HS256"])
        return (
            decoded.get("id"),
            decoded.get("credentials").get("email"),
            decoded.get("credentials").get("password"),
        )
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
