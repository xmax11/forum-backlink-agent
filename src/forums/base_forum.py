class BaseForum:
    """
    Base class for all forum platform handlers.
    Each platform (XenForo, phpBB, Discourse, etc.) must implement:
        - login()
        - post_reply()
    """

    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.base_url = config.get("base_url")
        self.threads = config.get("threads", [])
        self.auto_signup = config.get("auto_signup", False)

    def login(self):
        """
        Must be implemented by platform-specific classes.
        Should return a session object (requests.Session).
        """
        raise NotImplementedError("login() must be implemented in subclass")

    def post_reply(self, session, thread_url, reply_text):
        """
        Must be implemented by platform-specific classes.
        Should perform the actual POST request to submit a reply.
        """
        raise NotImplementedError("post_reply() must be implemented in subclass")
