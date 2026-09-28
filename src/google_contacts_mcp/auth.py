import os
from pathlib import Path
from typing import Optional
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    "https://www.googleapis.com/auth/contacts",
]

DEFAULT_CONFIG_DIR = Path.home() / ".config" / "google-contacts-mcp"


def get_config_dir() -> Path:
    config_dir = Path(os.getenv("GOOGLE_CONTACTS_CONFIG_DIR", DEFAULT_CONFIG_DIR))
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def get_credentials_path() -> Path:
    env_path = os.getenv("GOOGLE_CONTACTS_CREDENTIALS")
    if env_path:
        return Path(env_path)
    return get_config_dir() / "credentials.json"


def get_token_path() -> Path:
    env_path = os.getenv("GOOGLE_CONTACTS_TOKEN")
    if env_path:
        return Path(env_path)
    return get_config_dir() / "token.json"


def get_credentials() -> Optional[Credentials]:
    """Load valid user credentials from disk, refreshing if expired."""
    token_path = get_token_path()
    creds = None

    if token_path.exists():
        try:
            creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
        except Exception:
            creds = None

    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            # Save refreshed credentials
            with open(token_path, "w", encoding="utf-8") as f:
                f.write(creds.to_json())
        except Exception:
            creds = None

    if creds and creds.valid:
        return creds

    return None


def run_auth_flow(credentials_path: Optional[Path] = None, port: int = 8085) -> Credentials:
    """Run interactive OAuth consent flow and save tokens to disk."""
    creds_file = credentials_path or get_credentials_path()
    if not creds_file.exists():
        raise FileNotFoundError(
            f"Google Cloud OAuth client credentials not found at: {creds_file}\n"
            f"Please download your client secrets JSON from the Google Cloud Console "
            f"and save it to '{creds_file}' (or set GOOGLE_CONTACTS_CREDENTIALS)."
        )

    flow = InstalledAppFlow.from_client_secrets_file(str(creds_file), SCOPES)
    creds = flow.run_local_server(port=port, prompt="consent")

    token_path = get_token_path()
    token_path.parent.mkdir(parents=True, exist_ok=True)
    with open(token_path, "w", encoding="utf-8") as f:
        f.write(creds.to_json())
    
    # Restrict permissions on token file to owner only
    os.chmod(token_path, 0o600)
    return creds
