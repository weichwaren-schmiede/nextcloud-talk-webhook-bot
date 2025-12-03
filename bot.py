import os
import secrets
import hmac
import hashlib
import requests
import dotenv


class NextcloudBot:
    def __init__(self):
        # Load environment variables from .env file if it exists
        dotenv.load_dotenv()

        # Load configuration from Environment Variables
        self.nc_url = os.environ.get("NC_URL")
        self.token = os.environ.get("TOKEN")
        self.secret = os.environ.get("SECRET")

        # Validate environment variables
        if not all([self.nc_url, self.token, self.secret]):
            print("Error: Missing environment variables.")
            print("Please ensure NC_URL, TOKEN, and SECRET are set.")
            raise ValueError("Missing environment variables.")

        self.nc_url = self.nc_url.rstrip("/")


    def send_message(self, message: str) -> dict:
        # Generate Random Header and Signature
        # Equivalent to: openssl rand -hex 32
        random_header = secrets.token_hex(32)

        # Prepare string to sign
        message_to_sign = f"{random_header}{message}"

        # Calculate HMAC SHA256 signature
        # Equivalent to: openssl dgst -sha256 -hmac "${SECRET}"
        signature = hmac.new(
            key=self.secret.encode('utf-8'),
            msg=message_to_sign.encode('utf-8'),
            digestmod=hashlib.sha256
        ).hexdigest()

        # Send the request
        api_endpoint = f"{self.nc_url}/ocs/v2.php/apps/spreed/api/v1/bot/{self.token}/message"

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "OCS-APIRequest": "true",
            "X-Nextcloud-Talk-Bot-Random": random_header,
            "X-Nextcloud-Talk-Bot-Signature": signature
        }

        payload = {
            "message": message
        }

        try:
            response = requests.post(api_endpoint, json=payload, headers=headers)
            response.raise_for_status()  # Raise an exception for HTTP errors
            print("Message sent successfully.")
            print(f"Response: {response.json()}")
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error sending message: {e}")
            return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    NextcloudBot().send_message("Hello, this is a test message from the webhook bot.")
