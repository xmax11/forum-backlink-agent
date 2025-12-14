import json
from pathlib import Path
import random


ACCOUNTS_FILE = Path("data/accounts.json")


class AccountStore:
    """
    Stores and retrieves forum accounts.
    Supports:
        - loading accounts
        - saving accounts
        - adding new accounts
        - selecting a random account for a forum
    """

    def __init__(self):
        self.accounts = {}
        self._load()

    def _load(self):
        if ACCOUNTS_FILE.exists():
            try:
                with ACCOUNTS_FILE.open("r", encoding="utf-8") as f:
                    self.accounts = json.load(f)
            except Exception:
                self.accounts = {}
        else:
            self.accounts = {}

    def _save(self):
        ACCOUNTS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with ACCOUNTS_FILE.open("w", encoding="utf-8") as f:
            json.dump(self.accounts, f, indent=2)

    def add_account(self, forum_name, username, password):
        """
        Adds a new account for a forum.
        """
        if forum_name not in self.accounts:
            self.accounts[forum_name] = []

        self.accounts[forum_name].append({
            "username": username,
            "password": password
        })

        self._save()

    def get_random_account(self, forum_name):
        """
        Returns a random account for the given forum.
        """
        accounts = self.accounts.get(forum_name, [])
        if not accounts:
            return None
        return random.choice(accounts)
