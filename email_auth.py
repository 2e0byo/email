import webbrowser
from abc import ABC, abstractmethod
from collections import namedtuple
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from threading import Thread
from urllib.parse import parse_qs, urlparse

import google_auth_oauthlib as gauth
import msal
import requests

Token = namedtuple("Token", "token,id,secret")


class Credentials(ABC):
    def __init__(self, token_file: Path):
        self.token_file = token_file

    @abstractmethod
    def refresh_token(self) -> str:
        pass

    def write_refresh_token(self):
        token = self.refresh_token()
        with self.token_file.open("w") as f:
            f.write(token)
        self.token_file.chmod(0o600)

    def authentication_token(self) -> Token:
        with self.token_file.open() as f:
            token = f.read()
        resp = requests.post(
            self.TOKEN_URL,
            data={
                "client_id": self.ID,
                "client_secret": self.SECRET,
                "refresh_token": token,
                "grant_type": "refresh_token",
            },
        )
        if not resp.status_code == 200:
            raise Exception("Unable authenticate: " + resp.text)
        return Token(resp.json()["access_token"], self.ID, self.SECRET)

    def get_authentication_token(self):
        """Convenience method for libraries."""
        return self.authentication_token().token

    def get_client_id(self):
        """Convenience method for libraries."""
        return self.ID

    def get_client_secret(self):
        """Convenience method for libraries."""
        return self.SECRET


class GmailCredentials(Credentials):
    ID = "406964657835-aq8lmia8j95dhl1a2bvharmfk3t1hgqj.apps.googleusercontent.com"
    SECRET = "kSmqreRr0qwBWJgbf5Y-PjSU"
    SCOPES = "https://mail.google.com/"
    TOKEN_URL = "https://www.googleapis.com/oauth2/v3/token"

    def refresh_token(self) -> str:
        return gauth.get_user_credentials(
            self.SCOPES, self.ID, self.SECRET
        ).refresh_token


class Office365Credentials(Credentials):
    ID = "08162f7c-0fd2-4200-a84a-f25a4db0b584"
    SECRET = "TxRBilcHdC6WGBee]fs?QR:SJ8nI[g82"
    SCOPES = (
        "https://outlook.office.com/IMAP.AccessAsUser.All",
        "https://outlook.office.com/SMTP.Send",
    )
    TOKEN_URL = "https://login.microsoftonline.com/common/oauth2/v2.0/token"

    def refresh_token(self) -> str:
        authcode = None

        PORT = 7598
        redirect_uri = f"http://localhost:{PORT}/"

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                parts = urlparse(self.path)
                query = parse_qs(parts.query)
                nonlocal authcode
                authcode = query.get("code")
                self.send_response(200)
                self.send_header("Content-Type", "text/plain")
                self.end_headers()
                self.wfile.write(b"Success! You can now close this window.")
                nonlocal server
                Thread(target=lambda: server.shutdown()).start()

        app = msal.ConfidentialClientApplication(self.ID, self.SECRET)
        url = app.get_authorization_request_url(self.SCOPES, redirect_uri=redirect_uri)
        webbrowser.open(url)
        server = HTTPServer(("", PORT), Handler)
        server.serve_forever()
        token = app.acquire_token_by_authorization_code(
            authcode,
            list(self.SCOPES),  # has stupid broken isinstance test internally.
            redirect_uri=redirect_uri,
        )
        return token["refresh_token"]
