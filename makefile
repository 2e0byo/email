Durham:
	cd M365-IMAP && poetry run python get_token.py
	cat M365-IMAP/imap_smtp_refresh_token > ~/.pass/Durham
	chmod a=,u=rw ~/.pass/Durham
