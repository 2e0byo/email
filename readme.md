# XOAUTH2 flow for email

This library provides a basic XOauth2 flow for email which handles

- logging in a web browser
- saving refresh token
- getting an access token from the refresh token

I use it with offlineimap and Emacs.

The refresh token is stored in a file, with permissions set to 600.  *It can be
read by any process running as your user (and by root)*.  Personally this
doesn't bother me: email isn't secure anyway.  You might want to subclass/edit
and store in something like a keyring.

For the client id/secret we pretend to be thunderbird.

## Installation

```bash
pip install -r requirements.txt
```
Put `email.py` somewhere sensible.  Then create yourself a `oauth.py` following
the model.

## Offlineimap

In my `~/.offlineimaprc` I have:

```python
[Respository RemoteGmail]
pythonfile = ~/code/email/oauth.py
remoteuser = ...
oauth2_access_token_eval = Gmail_2e0byo.get_authentication_token()
auth_mechanisms = XOAUTH2
oauth2_request_url_eval =  Gmail_2e0byo.TOKEN_URL
oauth2_client_id_eval = Gmail_2e0byo.ID
oauth2_client_secret_eval = Gmail_2e0byo.SECRET
```

