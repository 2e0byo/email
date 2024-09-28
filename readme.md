# XOAUTH2 flow for email

This library provides a basic XOauth2 flow for email which handles

- logging in a web browser
- saving refresh token
- getting an access token from the refresh token

I use it with offlineimap and Emacs.

Unlike various other offerings across the web, this is designed to be a single
source of truth for email authentication. Implementing a new provider is as
simple as subclassing and handling getting the refresh token.

The refresh token is stored in a file, with permissions set to 600.  *It can be
read by any process running as your user (and by root)*.  Personally this
doesn't bother me: email isn't secure anyway.  You might want to subclass/edit
and store in something like a keyring.

Microsoft accounts, for some annoying reason, use a 'display' email (frequently
`first.last@company.suffix`) but require authentication with a 'machine' email
(`asdf67@company.suffix`). Or at any rate they do in Durham. This information is
stored on the Class if provided, so we can generate the xoauth2 str reliably. We
could just as easily do this in the client (indeed, I did), but the idea is to
be the sole source of truth, not just another step in an already overcomplicated
process.

For the client id/secret we pretend to be thunderbird.

## Installation

At present this is not on pypi, so you will have to build it yourself:
```bash
# clone and cd to this repo
# pipx install poetry or the like
poetry shell
poetry install
email-auth --help
```

For system istallations you can build a wheel and then pip install it somewhere:

```bash
poetry build
pip install dist/*.whl
```

*however* with the move to "managed python environments" where you are not
supposed to `pip install` stuff into your system, you might want to do one of
the following:

- if you use nix, the flake exports a package you can just install
- use pipx:
  ```shell
  poetry build
  pipx install dist/*.whl
  ```

- do the same thing manually: make a venv and install into that, then use the
  venv's interpreter explicitly:
  ```shell
  python -m venv .venv
  source .venv/bin/activate
  python -m pip install path/to/built/wheel
  deactivate
  ```
  ```bash
  # my script which needs email.sh
  /path/to/venv/python -c "from email_auth.cli import main; main()" --help
  ```
- exactly the same thing, but using the poetry venv (run `which python` after
  `poetry shell`). I prefer not doing this as I tend to break poetry envs by
  hacking on them: having an explicit installation step helps keep my head
  clear.
- dockerise, if you really must


## Initial Setup
Create a config file at the default location (`~/.config/email.toml`) or
elsewhere, with each account:

```toml
[accounts.foo]
token_file = "~/.pass/foo"
email = "foo@gmail.com"
type = "gmail"

[accounts.bar]
token_file = "~/.pass/bar"
email = "bar@gmail.com"
type = "gmail"
```

This is directly validated against the model defined in `creds.py`, dispatching
on the value of `type` with the alias in `config.py`. At the time of writing the
possible values are `gmail` or `o365`.

Run `email-auth --refresh USER@ACCOUNT` for every account defined in `oauth.py`.
This will fire up a web browser (run with `BROWSER=/path/to/browser` to change)
and direct you to your usual company login portal, after which it will extract
the refresh token and save it to disk.

You can pass all the accounts in at once, in which case they will be processed
sequentially.  Warning!  If your browser keeps you logged in---which it probably
will---and you have multiple accounts from the same provider, this may not do
what you think.

## Offlineimap

In my `~/.offlineimaprc` I have:

```python
[Respository RemoteGmail]
pythonfile = path/to/get_settings.py
remoteuser = ...
auth_mechanisms = XOAUTH2
oauth2_access_token_eval = authstr('foo@bar.com')
```

and then:

```python
# get_settings.py
def authstr(account: str) -> str:
    return run(
               ["email-auth", account],
               check=True, capture_output=True, encoding="utf8"
    ).stdout.strip()
```

Alternatively if offlineimap runs in the same venv as email-auth you can import
and work with the object directly.

## Emacs

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
email-auth USER@ACCOUNT # get and print authentication token
email-auth --authstr USER@ACCOUNT # get and print base64 encoded str for xoauth2
email-auth --refresh USER@ACCOUNT USER2@ACCOUNT2 # update refresh token for user.
```

# Credits
The office365 was rewritten from [M-365](https://github.com/UvA-FNWI/M365-IMAP).
Although I would have used `bottle`... but bottle 0.13 *still* isn't out, so the
server can't cleanly be stopped from a request... The differences are mostly
stylistic. The gmail code is straight from the docs.
