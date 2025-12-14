import requests
from bs4 import BeautifulSoup
from .base_forum import BaseForum


class IPSForum(BaseForum):
    """
    Handles login and posting for IPS (Invision Power Board).
    """

    def login(self):
        session = requests.Session()

        login_cfg = self.config.get("login")
        if not login_cfg:
            self.logger.warning(f"[IPS] No login credentials for {self.base_url}")
            return session

        login_url = login_cfg.get("login_url")
        username = login_cfg.get("username")
        password = login_cfg.get("password")

        try:
            resp = session.get(login_url, timeout=15)
            resp.raise_for_status()
        except Exception as e:
            self.logger.error(f"[IPS] Failed to load login page: {e}")
            return session

        soup = BeautifulSoup(resp.text, "html.parser")
        form = soup.find("form")
        if not form:
            self.logger.error("[IPS] No login form found")
            return session

        payload = {}
        for inp in form.find_all("input"):
            name = inp.get("name")
            value = inp.get("value", "")
            if not name:
                continue
            payload[name] = value

        payload["auth"] = username
        payload["password"] = password

        action_url = form.get("action") or login_url
        if not action_url.startswith("http"):
            action_url = self.base_url.rstrip("/") + "/" + action_url.lstrip("/")

        try:
            post_resp = session.post(action_url, data=payload, timeout=15)
            post_resp.raise_for_status()
            self.logger.info(f"[IPS] Logged in as {username}")
        except Exception as e:
            self.logger.error(f"[IPS] Login failed: {e}")

        return session

    def post_reply(self, session, thread_url, reply_text):
        try:
            resp = session.get(thread_url, timeout=15)
            resp.raise_for_status()
        except Exception as e:
            self.logger.error(f"[IPS] Failed to load thread: {e}")
            return False

        soup = BeautifulSoup(resp.text, "html.parser")
        form = soup.find("form")
        if not form:
            self.logger.error("[IPS] No reply form found")
            return False

        payload = {}
        for inp in form.find_all("input"):
            name = inp.get("name")
            value = inp.get("value", "")
            if not name:
                continue
            payload[name] = value

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
            self.logger.info(f"[IPS] Posted reply to {thread_url}")
            return True
        except Exception as e:
            self.logger.error(f"[IPS] Failed to post reply: {e}")
            return False
