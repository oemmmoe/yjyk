import base64
import random
import requests
import logging
from seleniumbase import SB

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

GEO_API = "http://ip-api.com/json/"
NAME_B64 = "YnJ1dGFsbGVz"
PROXY = False


def safe_request_geo():
    """Fetch geo data safely."""
    try:
        r = requests.get(GEO_API, timeout=10)
        r.raise_for_status()
        data = r.json()

        return (
            data.get("lat", 0),
            data.get("lon", 0),
            data.get("timezone", "UTC"),
            data.get("countryCode", "US").lower(),
        )
    except Exception as e:
        logging.warning(f"Geo lookup failed: {e}")
        return 0, 0, "UTC", "us"


def safe_decode_base64(value):
    """Safely decode base64 strings."""
    try:
        return base64.b64decode(value).decode("utf-8")
    except Exception as e:
        logging.warning(f"Base64 decode failed: {e}")
        return ""


def safe_element(driver, selector):
    """Safe element presence check."""
    try:
        return driver.is_element_present(selector)
    except Exception:
        return False


def safe_click(driver, selector, timeout=4):
    """Safe click wrapper."""
    try:
        if driver.is_element_present(selector):
            driver.cdp.click(selector, timeout=timeout)
            return True
    except Exception as e:
        logging.debug(f"Click failed {selector}: {e}")
    return False


def create_driver(url, tz, lat, lon):
    """Create and initialize driver safely."""
    try:
        driver = SB(
            uc=True,
            locale="en",
            ad_block=True,
            chromium_arg="--disable-webgl",
            proxy=PROXY
        ).__enter__()

        driver.activate_cdp_mode(
            url,
            tzone=tz,
            geoloc=(lat, lon)
        )

        return driver
    except Exception as e:
        logging.error(f"Driver creation failed: {e}")
        return None


# --- Fetch geo data ---
latitude, longitude, timezone_id, language_code = safe_request_geo()

# --- Decode name ---
fulln = safe_decode_base64(NAME_B64)
urlt = f"https://www.twitch.tv/{fulln}"

logging.info(f"Target URL: {urlt}")

while True:
    try:
        with SB(
            uc=True,
            locale="en",
            ad_block=True,
            chromium_arg="--disable-webgl",
            proxy=PROXY
        ) as awtrtw:

            rnd = random.randint(450, 800)

            awtrtw.activate_cdp_mode(
                urlt,
                tzone=timezone_id,
                geoloc=(latitude, longitude)
            )

            awtrtw.sleep(2)

            safe_click(awtrtw, 'button:contains("Accept")')

            awtrtw.sleep(2)
            awtrtw.sleep(12)

            if safe_click(awtrtw, 'button:contains("Start Watching")'):
                awtrtw.sleep(10)

            safe_click(awtrtw, 'button:contains("Accept")')

            if safe_element(awtrtw, "#live-channel-stream-information"):

                safe_click(awtrtw, 'button:contains("Accept")')

                try:
                    awtrtw2 = awtrtw.get_new_driver(undetectable=True)

                    awtrtw2.activate_cdp_mode(
                        urlt,
                        tzone=timezone_id,
                        geoloc=(latitude, longitude)
                    )

                    awtrtw2.sleep(10)

                    if safe_click(awtrtw2, 'button:contains("Start Watching")'):
                        awtrtw2.sleep(10)

                    safe_click(awtrtw2, 'button:contains("Accept")')

                except Exception as e:
                    logging.warning(f"Second driver failed: {e}")

                awtrtw.sleep(10)

                awtrtw.sleep(rnd)

            else:
                logging.info("Stream info not found, stopping loop.")
                break

    except Exception as e:
        logging.error(f"Loop error: {e}")
        continue
