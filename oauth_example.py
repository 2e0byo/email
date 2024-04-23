# path trickery for offlineimap. Other option is to install system-wide...
import sys
from argparse import ArgumentParser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from email_auth import GmailCredentials, Office365Credentials

Gmail1 = GmailCredentials(Path("~/.pass/account1").expanduser(), "one@gmail.com")
Gmail2 = GmailCredentials(Path("~/.pass/account2").expanduser(), "two@gmail.com")
Microsoft = Office365Credentials(
    Path("~/.pass/Microsoft").expanduser(),
    "first.last@uni.ac.uk",
    "abcd45@uni.ac.uk",
)


# accounts by username
ACCOUNTS = {x.user: x for x in {Gmail1, Gmail2, Microsoft}}
# accounts by email, if different
ACCOUNTS |= {x.email: x for x in {Gmail1, Gmail2, Microsoft}}

def main()  -> None:
    parser = ArgumentParser()
    parser.add_argument("account", nargs="*")
    parser.add_argument("--refresh", help="Refresh token", action="store_true")
    parser.add_argument("--authstr", help="Xoauth2 string", action="store_true")
    args = parser.parse_args()
    for k in args.account:
        account = ACCOUNTS[k]
        if args.refresh:
            account.write_refresh_token()
        elif args.authstr:
            print(account.xoauth_string())
        else:
            print(account.authentication_token())

if __name__ == "__main__":
    main()
