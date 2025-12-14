import random

from accounts.store import AccountStore
from accounts.signup import AccountSignup
from groq_client import GroqClient
from thread_parser import parse_thread

from forums.xenforo import XenForoForum
from forums.phpbb import PhpBBForum
from forums.discourse import DiscourseForum
from forums.vbulletin import VBulletinForum
from forums.mybb import MyBBForum
from forums.smf import SMFForum
from forums.ips import IPSForum
from forums.vanilla import VanillaForum


FORUM_CLASSES = {
    "xenforo": XenForoForum,
    "phpbb": PhpBBForum,
    "discourse": DiscourseForum,
    "vbulletin": VBulletinForum,
    "mybb": MyBBForum,
    "smf": SMFForum,
    "ips": IPSForum,
    "vanilla": VanillaForum,
}


class Poster:
    """
    Main posting engine.
    Handles:
        - selecting forum handler
        - login or auto-signup
        - generating replies
        - posting replies
    """

    def __init__(self, config, logger):
        self.config = config
        self.logger = logger

        self.account_store = AccountStore()
        self.signup = AccountSignup(logger)
        self.groq = GroqClient()

    def _get_forum_handler(self, forum_cfg):
        platform = forum_cfg.get("platform")
        cls = FORUM_CLASSES.get(platform)

        if not cls:
            raise ValueError(f"Unsupported forum platform: {platform}")

        return cls(forum_cfg, self.logger)

    def _get_or_create_account(self, forum_name, forum_cfg):
        """
        Returns an account for the forum.
        If auto-signup is enabled and no account exists, creates one.
        """
        account = self.account_store.get_random_account(forum_name)

        if account:
            return account

        if forum_cfg.get("auto_signup"):
            self.logger.info(f"[Poster] No account for {forum_name}, auto-signup enabled")
            return self.signup.signup(forum_name, forum_cfg.get("signup_url"))

        self.logger.error(f"[Poster] No account available for {forum_name}")
        return None

    def run_forum(self, forum_name, forum_cfg):
        """
        Executes posting workflow for a single forum.
        """

        self.logger.info(f"[Poster] Starting forum: {forum_name}")

        handler = self._get_forum_handler(forum_cfg)

        # Step 1: Get or create account
        account = self._get_or_create_account(forum_name, forum_cfg)
        if not account:
            return

        # Step 2: Login
        forum_cfg["login"] = {
            "login_url": forum_cfg.get("login_url"),
            "username": account["username"],
            "password": account["password"],
        }

        session = handler.login()

        # Step 3: Loop through threads
        for thread_url in forum_cfg.get("threads", []):
            self.logger.info(f"[Poster] Processing thread: {thread_url}")

            # Parse thread
            title, text = parse_thread(thread_url)

            # Generate reply
            reply = self.groq.generate_reply(title, text)
            if not reply:
                self.logger.error("[Poster] Failed to generate reply")
                continue

            # Post reply
            success = handler.post_reply(session, thread_url, reply)

            if success:
                self.logger.info(f"[Poster] ✅ Posted reply to {thread_url}")
            else:
                self.logger.error(f"[Poster] ❌ Failed to post reply to {thread_url}")

    def run_all(self):
        """
        Runs posting workflow for all forums in config.
        """
        for forum_name, forum_cfg in self.config.items():
            self.run_forum(forum_name, forum_cfg)
