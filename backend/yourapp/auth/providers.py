from abc import ABC, abstractmethod
from supabase import Client as SupabaseClient
import jwt


class AuthProvider(ABC):
    @abstractmethod
    def corresponds_to_credentials(self, credentials: dict):
        """
        Check if the credentials correspond to this auth provider.
        Returns True if the credentials correspond to this auth provider,
        otherwise returns False.
        """
        pass

    @abstractmethod
    def authenticate(self, app_secret: str, credentials: dict) -> str:
        """
        Authenticate the user with the provided credentials.
        Returns an access token if authentication is successful,
        otherwise returns None.
        """
        pass


class SupabaseAuthProvider(AuthProvider):
    supabase_key: str
    supabase_url: str

    def __init__(self, supabase_key: str, supabase_url: str):
        self.supabase_key = supabase_key
        self.supabase_url = supabase_url

    def corresponds_to_credentials(self, _credentials: dict):
        return True

    def authenticate(self, app_secret: str, credentials: dict):
        # Authenticate with Supabase
        try:
            client = SupabaseClient(self.supabase_url, self.supabase_key)
            data = client.auth.sign_in_with_password(credentials)
            client.auth.sign_out()

            id = data.user.id

            return jwt.encode(
                {"id": id, "credentials": credentials}, app_secret, algorithm="HS256"
            )

        except Exception:
            return None
