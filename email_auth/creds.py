import ssl
from typing import Annotated, ClassVar
import webbrowser
from abc import ABC, abstractmethod
from base64 import b64encode
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from threading import Thread
from urllib.parse import parse_qs, urlparse
from pydantic import BaseModel, AfterValidator

import google_auth_oauthlib as gauth
import msal
import requests
from O365 import Account, FileSystemTokenBackend

ResolvedPath = Annotated[Path, AfterValidator(lambda p: p.expanduser().resolve())]


class Credentials(ABC, BaseModel):
    """Credentials which can generate a refresh token."""

    token_file: ResolvedPath
    email: str
    username: str | None = None

    @property
    def user(self):
        """Get the user or email."""
        return self.username or self.email

    @abstractmethod
    def refresh_token(self) -> str:
        """Get a new refresh token."""
        pass

    def write_refresh_token(self):
        """Get a new refresh token and write it to disk."""
        token = self.refresh_token()
        self.token_file.write_text(token)
        self.token_file.chmod(0o600)


class AuthenticatableCredentials(Credentials):
    """Credentials which can meaningfully generate an auth token."""

    def authentication_token(self) -> str:
        """Get a new authentication token."""
        with self.token_file.open() as f:
            token = f.read()

        data = {
            "client_id": self.ID,
            "refresh_token": token,
            "grant_type": "refresh_token",
        }
        if getattr(self, "SECRET", None):
            data["client_secret"] = self.SECRET
        resp = requests.post(
            self.TOKEN_URL,
            data=data,
        )
        if not resp.status_code == 200:
            raise Exception("Unable authenticate: " + resp.text)
        return resp.json()["access_token"]

    def xoauth_string(self) -> str:
        """Get a base64 encoded string all ready for dropping into connection."""
        return b64encode(
            f"user={self.user}\1auth=Bearer {self.authentication_token()}\1\1".encode()
        ).decode()


class GmailCredentials(AuthenticatableCredentials):
    """OAUTH Credentials for Gmaili."""

    ID: ClassVar[str] = (
        "406964657835-aq8lmia8j95dhl1a2bvharmfk3t1hgqj.apps.googleusercontent.com"
    )
    SECRET: ClassVar[str] = "kSmqreRr0qwBWJgbf5Y-PjSU"
    SCOPES: ClassVar[str] = "https://mail.google.com/"
    TOKEN_URL: ClassVar[str] = "https://www.googleapis.com/oauth2/v3/token"

    def refresh_token(self) -> str:
        """Get a new refresh token."""
        return gauth.get_user_credentials(
            self.SCOPES, self.ID, self.SECRET
        ).refresh_token


class WebbrowserTokenMixin:
    """Mixin for getting a token via a webbrowser."""

    @staticmethod
    def get_response_url(url, port):
        """Authenticate and return the url (containing the authcode)."""

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                nonlocal url
                url = self.path
                self.send_response(200)
                self.send_header("Content-Type", "text/plain")
                self.end_headers()
                self.wfile.write(b"Success! You can now close this window.")
                nonlocal server
                Thread(target=lambda: server.shutdown()).start()

        server = HTTPServer(("", port), Handler)
        root = Path(__file__).parent
        keyf, certf = root / "server.key", root / "server.cert"
        assert keyf.exists() and certf.exists()
        context = ssl.SSLContext()
        context.load_cert_chain(certf, keyf)
        server.socket = context.wrap_socket(
            server.socket,
            server_side=True
        )
        t = Thread(target=server.serve_forever)
        t.start()
        webbrowser.open(url)
        t.join()
        return url

    def get_authcode(self, url, port):
        """Authenticate and extract the authcode."""
        resp_url = self.get_response_url(url, port)
        parts = urlparse(resp_url)
        query = parse_qs(parts.query)
        return query["code"]


class Office365Credentials(AuthenticatableCredentials, WebbrowserTokenMixin):
    """Credentials for Office365 accounts."""

    ID: ClassVar[str] = "9e5f94bc-e8a4-4e73-b8be-63364c29d753"
    SCOPES: ClassVar[tuple[str, ...]] = (
        "https://outlook.office365.com/IMAP.AccessAsUser.All",
        "https://outlook.office365.com/SMTP.Send",
    )
    TOKEN_URL: ClassVar[str] = (
        "https://login.microsoftonline.com/common/oauth2/v2.0/token"
    )

    def refresh_token(self) -> str:
        """Get a new refresh token."""
        PORT = 7598
        redirect_uri = f"https://localhost:{PORT}/"
        app = msal.ConfidentialClientApplication(self.ID)
        url = app.get_authorization_request_url(self.SCOPES, redirect_uri=redirect_uri)
        authcode = self.get_authcode(url, PORT)
        token = app.acquire_token_by_authorization_code(
            authcode,
            list(self.SCOPES),  # has stupid broken isinstance test internally.
            redirect_uri=redirect_uri,
        )
        return token["refresh_token"]


class EWSCredentials(Credentials, WebbrowserTokenMixin):
    """Credentials for EWS accounts, to be used by py-o365."""

    ID: ClassVar[str] = "20460e5d-ce91-49af-a3a5-70b6be7486d1"
    SCOPES: ClassVar[tuple[str, ...]] = (
        "https://graph.microsoft.com/Mail.ReadWrite",
        "https://graph.microsoft.com/User.Read",
        "https://graph.microsoft.com/Mail.Send",
    )

    def __init__(self, *args, **kwargs):
        """Initialise a new EWSCredentials() object."""
        super().__init__(*args, **kwargs)
        self.token_file.mkdir(exist_ok=True)
        self.token_backend = FileSystemTokenBackend(self.token_file)

    def refresh_token(self):
        """Get a new refresh token and write it to the backend store."""
        PORT = 7598
        redirect_uri = f"http://localhost:{PORT}/"
        account = Account((self.ID,), auth_flow_type="public")
        url, state = account.con.get_authorization_url(
            requested_scopes=self.SCOPES,
            redirect_uri=redirect_uri,  # Fails as wrong redirect uri
            token_backend=self.token_backend,
        )
        resp_url = self.get_response_url(url, PORT)
        result = account.con.request_token(resp_url, state=state)
        if not result:
            raise Exception("Failed to get token.")

    write_refresh_token = refresh_token

    def xoauth_string(self):
        """Tell callers we don't do authstrs."""
        raise NotImplementedError("An authstr does not make sense here.")
