import requests
from bs4 import BeautifulSoup
from .base_forum import BaseForum


class PhpBBForum(BaseForum):
    """
    Handles login and posting for phpBB-based forums.
    """

    def login(self):
        """
        Logs into a phpBB forum using username/password.
        Returns a logged-in requests.Session().
        """
        session = requests.Session()

        login_cfg = self.config.get("login")
        if not login_cfg:
            self.logger.warning(f"[phpBB] No login credentials for {self.base_url}")
            return session  # anonymous session

        login_url = login_cfg.get("login_url")
        username = login_cfg.get("username")
        password = login_cfg.get("password")

        try:
            # Load login page for any hidden tokens
            resp = session.get(login_url, timeout=15)
            resp.raise_for_status()
        except Exception as e:
            self.logger.error(f"[phpBB] Failed to load login page: {e}")
            return session

        soup = BeautifulSoup(resp.text, "html.parser")
        form = soup.find("form")
        payload = {}

        # Collect form fields
        for inp in form.find_all("input"):
            name = inp.get("name")
            value = inp.get("value", "")
            if not name:
                continue
            payload[name] = value

        # Override username/password fields (common phpBB names)
        payload["username"] = username
        payload["password"] = password

        action_url = form.get("action") or login_url
        if not action_url.startswith("http"):
            action_url = self.base_url.rstrip("/") + "/" + action_url.lstrip("/")

        try:
            post_resp = session.post(action_url, data=payload, timeout=15)
            post_resp.raise_for_status()
            self.logger.info(f"[phpBB] Logged in as {username}")
        except Exception as e:
            self.logger.error(f"[phpBB] Login failed: {e}")

        return session

    def post_reply(self, session, thread_url, reply_text):
        """
        Posts a reply to a phpBB thread.
        """
        try:
            resp = session.get(thread_url, timeout=15)
            resp.raise_for_status()
        except Exception as e:
            self.logger.error(f"[phpBB] Failed to load thread: {e}")
            return False

        soup = BeautifulSoup(resp.text, "html.parser")

        # Find reply form
        form = soup.find("form", {"id": "postform"}) or soup.find("form")
        if not form:
            self.logger.error("[phpBB] Could not find reply form")
            return False

        payload = {}
        for inp in form.find_all("input"):
            name = inp.get("name")
            value = inp.get("value", "")
            if not name:
                continue
            payload[name] = value

        # Textarea for message
        textarea = form.find("textarea")
        if textarea and textarea.get("name"):
            payload[textarea.get("name")] = reply_text
        else:
            payload["message"] = reply_text

        action_url = form.get("action") or thread_url
        if not action_url.startswith("http"):
            action_url = self.base_url.rstrip("/") + "/" + action_url.lstrip("/")

        try:
            post_resp = session.post(action_url, data=payload, timeout=15)
            post_resp.raise_for_status()
            self.logger.info(f"[phpBB] Posted reply to {thread_url}")
            return True
        except Exception as e:
            self.logger.error(f"[phpBB] Failed to post reply: {e}")
            return False
