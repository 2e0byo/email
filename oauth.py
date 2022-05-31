# path trickery for offlineimap. Other option is to install system-wide...
import sys
from argparse import ArgumentParser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from email_auth import GmailCredentials, Office365Credentials

Gmail_2e0byo = GmailCredentials(Path("~/.pass/2e0byo").expanduser())
Wombat = GmailCredentials(Path("~/.pass/Wombat").expanduser())
Durham = Office365Credentials(Path("~/.pass/Durham").expanduser())

ACCOUNTS = {
    "2e0byo": Gmail_2e0byo,
    "Wombat": Wombat,
    "Durham": Durham,
}
if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("account", nargs="*")
    parser.add_argument("--refresh", help="Refresh token", action="store_true")
    args = parser.parse_args()
    for k in args.account:
        account = ACCOUNTS[k]
        if args.refresh:
            account.refresh_token()
        else:
            print(account.get_authentication_token())
