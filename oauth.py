# path trickery for offlineimap. Other option is to install system-wide...
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from email_auth import GmailCredentials, Office365Credentials
from pathlib import Path

Gmail_2e0byo = GmailCredentials(Path("~/.pass/2e0byo").expanduser())
Wombat = GmailCredentials(Path("~/.pass/Wombat").expanduser())
Durham = Office365Credentials(Path("~/.pass/Durham").expanduser())

ACCOUNTS = {
    "2e0byo": Gmail_2e0byo,
    "Wombat": Wombat,
    "Durham": Durham,
}
if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise Exception(
            "Provide accounts to update refresh token out of "
            + " ".join(ACCOUNTS.keys())
        )
    for k in sys.argv[1:]:
        ACCOUNTS[k].write_refresh_token()
