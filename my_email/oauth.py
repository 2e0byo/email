from argparse import ArgumentParser
from pathlib import Path

from .email_auth import GmailCredentials, Office365Credentials
from .config import load_config


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument("account", nargs="*")
    parser.add_argument("--refresh", help="Refresh token", action="store_true")
    parser.add_argument("--authstr", help="Xoauth2 string", action="store_true")
    parser.add_argument(
        "--config", type=Path, help="Config file", default=Path("~/.config/email.toml")
    )
    args = parser.parse_args()
    accounts = load_config(args.config)
    for k in args.account:
        account = accounts[k]
        if args.refresh:
            account.write_refresh_token()
        elif args.authstr:
            print(account.xoauth_string())
        else:
            print(account.authentication_token())


if __name__ == "__main__":
    main()
