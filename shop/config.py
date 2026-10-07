"""Product settings for the landing. Edit here: brand, prices, colors."""
import os

BRAND = os.environ.get("SHOP_BRAND", "QALTA")

# Prices in tenge. Delivery is included.
PRICE_ONE = 25_000
PRICE_TWO = 45_000
MAX_QUANTITY = 10

# Card holder colors: key -> swatch hex. Names live in i18n.py (color_<key>).
COLORS = {
    "black": "#1d1d1f",
    "brown": "#7a4a2b",
    "beige": "#d9c3a5",
}

LANGUAGES = ("kk", "ru", "en")
DEFAULT_LANGUAGE = "kk"


def total_price(quantity):
    """Every pair costs PRICE_TWO, a leftover single costs PRICE_ONE."""
    pairs, single = divmod(quantity, 2)
    return pairs * PRICE_TWO + single * PRICE_ONE


def format_tenge(amount):
    return f"{amount:,}".replace(",", " ") + " ₸"
