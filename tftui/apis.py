import platform
import socket
import hashlib
import importlib.metadata
import requests
from tftui.constants import nouns, adjectives


class OutboundAPIs:
    is_new_version_available = False
    is_usage_tracking_enabled = True
    generated_handle = None
    posthog = None
    version = importlib.metadata.version("tftui")

    @staticmethod
    def check_for_new_version():
        try:
            response = requests.get("https://pypi.org/pypi/tftui/json")
            if response.status_code == 200:
                ver = response.json()["info"]["version"]
                if ver != OutboundAPIs.version:
                    OutboundAPIs.is_new_version_available = True
        except Exception:
            pass

    @staticmethod
    def generate_handle():
        fingerprint_data = f"{platform.system()}-{platform.node()}-{platform.release()}-{socket.gethostname()}"
        fingerprint = int(hashlib.sha256(fingerprint_data.encode()).hexdigest(), 16)
        OutboundAPIs.generated_handle = (
            adjectives[fingerprint % len(adjectives)]
            + " "
            + nouns[fingerprint % len(nouns)]
        )

    @staticmethod
    def post_usage(message: str, error_message="", platform="", size="") -> None:
        if not OutboundAPIs.is_usage_tracking_enabled:
            return
        if not OutboundAPIs.generated_handle:
            OutboundAPIs.generate_handle()
        if not OutboundAPIs.posthog:
            from posthog import Posthog

            POSTHOG_API_KEY = "phc_tjGzx7V6Y85JdNfOFWxQLXo5wtUs6MeVLvoVfybqz09"  # + "uncomment-while-developing"

            OutboundAPIs.posthog = Posthog(
                project_api_key=POSTHOG_API_KEY,
                host="https://app.posthog.com",
                disable_geoip=False,
            )

        OutboundAPIs.posthog.capture(
            OutboundAPIs.generated_handle,
            message,
            {
                "tftui_version": OutboundAPIs.version,
                "error_message": error_message,
                "platform": platform,
                "size": size,
            },
        )

    @staticmethod
    def disable_usage_tracking() -> None:
        OutboundAPIs.is_usage_tracking_enabled = False
