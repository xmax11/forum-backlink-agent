import requests
from bs4 import BeautifulSoup

from email.mailtm_client import MailTmClient
from captcha.solver_client import CaptchaSolver
from accounts.store import AccountStore


class AccountSignup:
    """
    Automates account creation for forums that allow open registration.
    """

    def __init__(self, logger):
        self.logger = logger
        self.email_client = MailTmClient()
        self.captcha_solver = CaptchaSolver()
        self.store = AccountStore()

    def signup(self, forum_name, signup_url):
        """
        Creates a new account for a forum.
        Steps:
            1. Generate temp email
            2. Load signup page
            3. Extract form fields
            4. Solve captcha (if present)
            5. Submit registration
            6. Wait for verification email
            7. Extract verification link
            8. Activate account
            9. Save credentials
        """

        # Step 1: Generate temp email
        email_addr, email_token = self.email_client.create_email()
        username = email_addr.split("@")[0]
        password = self.email_client.generate_password()

        self.logger.info(f"[Signup] Creating account for {forum_name}: {email_addr}")

        # Step 2: Load signup page
        try:
            session = requests.Session()
            resp = session.get(signup_url, timeout=15)
            resp.raise_for_status()
        except Exception as e:
            self.logger.error(f"[Signup] Failed to load signup page: {e}")
            return None

        soup = BeautifulSoup(resp.text, "html.parser")
        form = soup.find("form")
        if not form:
            self.logger.error("[Signup] No signup form found")
            return None

        # Step 3: Extract form fields
        payload = {}
        for inp in form.find_all("input"):
            name = inp.get("name")
            value = inp.get("value", "")
            if not name:
                continue
            payload[name] = value

        # Override common fields
        payload["username"] = username
        payload["email"] = email_addr
        payload["password"] = password
        payload["password_confirm"] = password

        # Step 4: Solve captcha if present
        captcha_img = soup.find("img", {"class": "captcha"})
        if captcha_img:
            captcha_url = captcha_img.get("src")
            if not captcha_url.startswith("http"):
                captcha_url = signup_url.rsplit("/", 1)[0] + "/" + captcha_url.lstrip("/")

            captcha_solution = self.captcha_solver.solve(captcha_url)
            payload["captcha"] = captcha_solution

        # Step 5: Submit registration
        action_url = form.get("action") or signup_url
        if not action_url.startswith("http"):
            action_url = signup_url.rsplit("/", 1)[0] + "/" + action_url.lstrip("/")

        try:
            post_resp = session.post(action_url, data=payload, timeout=15)
            post_resp.raise_for_status()
        except Exception as e:
            self.logger.error(f"[Signup] Registration failed: {e}")
            return None

        self.logger.info("[Signup] Registration submitted, waiting for verification email...")

        # Step 6: Wait for verification email
        verification_link = self.email_client.wait_for_verification_link(email_token)
        if not verification_link:
            self.logger.error("[Signup] No verification email received")
            return None

        # Step 7: Activate account
        try:
            verify_resp = session.get(verification_link, timeout=15)
            verify_resp.raise_for_status()
            self.logger.info("[Signup] Account verified successfully")
        except Exception as e:
            self.logger.error(f"[Signup] Verification failed: {e}")
            return None

        # Step 8: Save credentials
        self.store.add_account(forum_name, username, password)

        return {
            "username": username,
            "password": password,
            "email": email_addr
        }
