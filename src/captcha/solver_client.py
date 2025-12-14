import requests
import base64
import time
import os


class CaptchaSolver:
    """
    Generic captcha solver client.
    Supports providers like:
        - 2Captcha
        - CapMonster
        - AntiCaptcha
    """

    def __init__(self):
        self.api_key = os.getenv("CAPTCHA_API_KEY")
        if not self.api_key:
            raise RuntimeError("CAPTCHA_API_KEY environment variable is missing.")

        # Default provider: 2Captcha-compatible API
        self.provider_url = os.getenv("CAPTCHA_PROVIDER_URL", "https://2captcha.com")

    def solve(self, image_url):
        """
        Downloads captcha image and sends it to the solver.
        Returns the solved text.
        """

        # Step 1: Download captcha image
        try:
            img_resp = requests.get(image_url, timeout=15)
            img_resp.raise_for_status()
            img_bytes = img_resp.content
        except Exception as e:
            print(f"[Captcha] Failed to download captcha: {e}")
            return None

        # Step 2: Encode image to base64
        encoded = base64.b64encode(img_bytes).decode()

        # Step 3: Submit captcha to provider
        payload = {
            "key": self.api_key,
            "method": "base64",
            "body": encoded,
            "json": 1
        }

        try:
            submit = requests.post(f"{self.provider_url}/in.php", data=payload, timeout=15)
            submit.raise_for_status()
            captcha_id = submit.json().get("request")
        except Exception as e:
            print(f"[Captcha] Failed to submit captcha: {e}")
            return None

        # Step 4: Poll for result
        result_url = f"{self.provider_url}/res.php?key={self.api_key}&action=get&id={captcha_id}&json=1"

        for _ in range(20):  # ~60 seconds max
            try:
                res = requests.get(result_url, timeout=10).json()
            except Exception:
                time.sleep(3)
                continue

            if res.get("status") == 1:
                return res.get("request")

            time.sleep(3)

        print("[Captcha] Timeout waiting for solution")
        return None
