import requests
from bs4 import BeautifulSoup
from .base_forum import BaseForum


class XenForoForum(BaseForum):
    """
    Handles login and posting for XenForo-based forums.
    """

    def login(self):
        """
        Logs into a XenForo forum using username/password.
        Returns a logged-in requests.Session().
        """

        session = requests.Session()

        login_cfg = self.config.get("login")
        if not login_cfg:
            self.logger.warning(f"[XenForo] No login credentials for {self.base_url}")
            return session  # anonymous session

        login_url = login_cfg.get("login_url")
        username = login_cfg.get("username")
        password = login_cfg.get("password")

        # Step 1: Fetch login page to get CSRF token
        try:
            resp = session.get(login_url, timeout=15)
            resp.raise_for_status()
        except Exception as e:
            self.logger.error(f"[XenForo] Failed to load login page: {e}")
            return session

        soup = BeautifulSoup(resp.text, "html.parser")
        csrf = soup.find("input", {"name": "_xfToken"})
        csrf_token = csrf["value"] if csrf else ""

        # Step 2: Submit login form
        payload = {
            "login": username,
            "password": password,
            "_xfToken": csrf_token,
            "remember": "1",
        }

        try:
            post_resp = session.post(login_url, data=payload, timeout=15)
            post_resp.raise_for_status()
            self.logger.info(f"[XenForo] Logged in as {username}")
        except Exception as e:
            self.logger.error(f"[XenForo] Login failed: {e}")

        return session

    def post_reply(self, session, thread_url, reply_text):
        """
        Posts a reply to a XenForo thread.
        """

        # Step 1: Load thread page to get CSRF token + form action
        try:
            resp = session.get(thread_url, timeout=15)
            resp.raise_for_status()
        except Exception as e:
            self.logger.error(f"[XenForo] Failed to load thread: {e}")
            return False

        soup = BeautifulSoup(resp.text, "html.parser")

        # CSRF token
        csrf = soup.find("input", {"name": "_xfToken"})
        csrf_token = csrf["value"] if csrf else ""

        # Form action (reply endpoint)
        form = soup.find("form", {"class": "block"})
        action_url = form["action"] if form else None

        if not action_url:
            self.logger.error("[XenForo] Could not find reply form action URL")
            return False

        # Step 2: Submit reply
        payload = {
            "message": reply_text,
            "_xfToken": csrf_token,
            "_xfResponseType": "json",
        }

        try:
            post_resp = session.post(action_url, data=payload, timeout=15)
            post_resp.raise_for_status()
            self.logger.info(f"[XenForo] Posted reply to {thread_url}")
            return True
        except Exception as e:
            self.logger.error(f"[XenForo] Failed to post reply: {e}")
            return False
