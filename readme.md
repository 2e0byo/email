# XOAUTH2 flow for email

This library provides a basic XOauth2 flow for email which handles

- logging in a web browser
- saving refresh token
- getting an access token from the refresh token

I use it with offlineimap and Emacs.

Unlike various other offerings across he web, this is designed to be a single
source of truth for email authentication. Implementing a new provider is as
simple as subclassing and handling getting the refresh token.

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
the model in `oauth_example.py`.

## Offlineimap (or library usage)

In my `~/.offlineimaprc` I have:

```python
[Respository RemoteGmail]
pythonfile = ~/code/email/oauth.py
remoteuser = ...
auth_mechanisms = XOAUTH2
oauth2_access_token_eval = Gmail_2e0byo.authentication_token()
```

## Emacs (or cli usage)

In my `init.el` I have:

```elisp
(require 'oauth2)

(cl-defmethod smtpmail-try-auth-method
  (process (_mech (eql xoauth2)) user password)
  (smtpmail-command-or-throw
   process
   (concat "AUTH XOAUTH2 " (shell-command-to-string (concat "python ~/code/email/oauth.py --authstr " user)))))


(add-to-list 'smtpmail-auth-supported 'xoauth2)
```

The complete cli:

```bash
python oauth.py USER@ACCOUNT # get and print authentication token
python oauth.py --authstr USER@ACCOUNT # get and print base64 encoded str for xoauth2
python oauth.py --refresh USER@ACCOUNT USER2@ACCOUNT2 "# update refresh token for user.
```

# Credits
The office365 was rewritten from [M-365](https://github.com/UvA-FNWI/M365-IMAP).
Although I would have used `bottle`... but bottle 0.13 *still* isn't out, so the
server can't cleanly be stopped from a request... The differences are mostly
stylistic. The gmail code is straight from the docs.
