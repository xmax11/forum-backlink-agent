import requests
from .base_forum import BaseForum


class DiscourseForum(BaseForum):
    """
    Handles login and posting for Discourse-based forums.
    NOTE: Discourse often uses API keys or SSO; this implementation
    assumes username/password login with session cookies is allowed.
    """

    def login(self):
        """
        Logs into a Discourse forum.
        Returns a logged-in requests.Session().
        """
        session = requests.Session()

        login_cfg = self.config.get("login")
        if not login_cfg:
            self.logger.warning(f"[Discourse] No login credentials for {self.base_url}")
            return session

        login_url = login_cfg.get("login_url") or f"{self.base_url.rstrip('/')}/session"
        username = login_cfg.get("username")
        password = login_cfg.get("password")

        payload = {
            "login": username,
            "password": password,
        }

        try:
            resp = session.post(login_url, json=payload, timeout=15)
            resp.raise_for_status()
            self.logger.info(f"[Discourse] Logged in as {username}")
        except Exception as e:
            self.logger.error(f"[Discourse] Login failed: {e}")

        return session

    def post_reply(self, session, thread_url, reply_text):
        """
        Posts a reply to a Discourse topic.
        Uses the /posts.json endpoint.
        """
        # Discourse topic ID typically in URL: /t/slug/topic_id
        try:
            topic_id = int(thread_url.rstrip("/").split("/")[-1])
        except Exception:
            self.logger.error("[Discourse] Could not parse topic ID from URL")
            return False

        api_url = f"{self.base_url.rstrip('/')}/posts.json"
        payload = {
            "raw": reply_text,
            "topic_id": topic_id,
        }

        try:
            resp = session.post(api_url, data=payload, timeout=15)
            resp.raise_for_status()
            self.logger.info(f"[Discourse] Posted reply to topic {topic_id}")
            return True
        except Exception as e:
            self.logger.error(f"[Discourse] Failed to post reply: {e}")
            return False
