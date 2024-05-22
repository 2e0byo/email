from pathlib import Path
from toml import load


from .email_auth import (
    AuthenticatableCredentials,
    Credentials,
    GmailCredentials,
    Office365Credentials,
)

_CREDENTIALS_MAP = {
    "gmail": GmailCredentials,
    "o365": Office365Credentials,
}


def load_config(path: Path) -> dict[str, AuthenticatableCredentials]:
    data = load(path)
    assert data["accounts"]
    accounts = {}
    for account in data["accounts"].values():
        creds = _CREDENTIALS_MAP[account["type"]](**account)
        accounts[creds.user] = creds

    return accounts | {x.email: x for x in accounts.values()}
