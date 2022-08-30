# path trickery for offlineimap. Other option is to install system-wide...
import sys
from argparse import ArgumentParser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from email_auth import GmailCredentials, Office365Credentials

Gmail_2e0byo = GmailCredentials(Path("~/.pass/2e0byo").expanduser(), "2e0byo@gmail.com")
Wombat = GmailCredentials(
    Path("~/.pass/Wombat").expanduser(), "jmwombat122@googlemail.com"
)
Durham = Office365Credentials(
    Path("~/.pass/Durham").expanduser(),
    "john.morris@durham.ac.uk",
    "lntq46@durham.ac.uk",
)


ACCOUNTS = {x.user: x for x in {Gmail_2e0byo, Wombat, Durham}}
ACCOUNTS |= {x.email: x for x in {Gmail_2e0byo, Wombat, Durham}}

if __name__ == "__main__":
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
