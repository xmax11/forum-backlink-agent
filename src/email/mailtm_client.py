import requests
import time
import random
import string


MAILTM_BASE = "https://api.mail.tm"


class MailTmClient:
    """
    Handles temporary email creation and verification link extraction
    using the mail.tm API.
    """

    def __init__(self):
        self.session = requests.Session()

    def generate_password(self, length=12):
        """
        Generates a random strong password.
        """
        chars = string.ascii_letters + string.digits
        return "".join(random.choice(chars) for _ in range(length))

    def create_email(self):
        """
        Creates a new temporary email inbox.
        Returns:
            (email_address, token)
        """

        # Step 1: Get available domains
        domains_resp = self.session.get(f"{MAILTM_BASE}/domains")
        domains_resp.raise_for_status()
        domains = domains_resp.json()["hydra:member"]
        domain = domains[0]["domain"]

        # Step 2: Create account
        username = "".join(random.choice(string.ascii_lowercase) for _ in range(10))
        email = f"{username}@{domain}"
        password = self.generate_password()

        payload = {"address": email, "password": password}

        acc_resp = self.session.post(f"{MAILTM_BASE}/accounts", json=payload)
        acc_resp.raise_for_status()

        # Step 3: Login to get token
        token_resp = self.session.post(f"{MAILTM_BASE}/token", json=payload)
        token_resp.raise_for_status()
        token = token_resp.json()["token"]

        self.session.headers.update({"Authorization": f"Bearer {token}"})

        return email, token

    def wait_for_verification_link(self, token, timeout=120):
        """
        Polls inbox for verification email and extracts the first link.
        """

        start = time.time()

        while time.time() - start < timeout:
            msgs = self.session.get(f"{MAILTM_BASE}/messages").json()

            for msg in msgs.get("hydra:member", []):
                msg_id = msg["id"]
                full_msg = self.session.get(f"{MAILTM_BASE}/messages/{msg_id}").json()

                # Extract first link from email body
                body = full_msg.get("text", "") + full_msg.get("html", "")
                link = self._extract_link(body)
                if link:
                    return link

            time.sleep(5)

        return None

    def _extract_link(self, text):
        """
        Extracts the first URL from a block of text.
        """
        import re

        match = re.search(r"https?://[^\s]+", text)
        return match.group(0) if match else None
