"""Approximate coordinates (lon, lat) for plotting items on the radar globe.

A blip marks a country, not a city: the point is usually the capital or main
financial centre. Items with no known country are not plotted (the page says
how many are on the globe), so the globe never shows a location we made up.
"""
from __future__ import annotations

from . import rules

BAKU = (49.87, 40.41)

COUNTRY_COORDS: dict[str, tuple[float, float]] = {
    # Azerbaijan and nearby
    "Azerbaijan": BAKU,
    "Georgia": (44.79, 41.72), "Armenia": (44.51, 40.18), "Türkiye": (28.98, 41.01),
    "Kazakhstan": (76.95, 43.24), "Uzbekistan": (69.24, 41.30), "Kyrgyzstan": (74.59, 42.87),
    "Tajikistan": (68.78, 38.56), "Turkmenistan": (58.38, 37.95), "Russia": (37.62, 55.76),
    "Belarus": (27.56, 53.90), "Ukraine": (30.52, 50.45), "Moldova": (28.86, 47.01),
    "United Arab Emirates": (55.27, 25.20), "Saudi Arabia": (46.68, 24.71), "Qatar": (51.53, 25.29),
    "Bahrain": (50.59, 26.23), "Kuwait": (47.98, 29.38), "Oman": (58.41, 23.59), "Iran": (51.39, 35.69),
    # Europe
    "United Kingdom": (-0.13, 51.51), "Ireland": (-6.26, 53.35), "France": (2.35, 48.86),
    "Germany": (8.68, 50.11), "Netherlands": (4.90, 52.37), "Belgium": (4.35, 50.85),
    "Luxembourg": (6.13, 49.61), "Switzerland": (8.54, 47.38), "Austria": (16.37, 48.21),
    "Italy": (9.19, 45.46), "Spain": (-3.70, 40.42), "Portugal": (-9.14, 38.72),
    "Sweden": (18.07, 59.33), "Norway": (10.75, 59.91), "Denmark": (12.57, 55.68),
    "Finland": (24.94, 60.17), "Estonia": (24.75, 59.44), "Latvia": (24.11, 56.95),
    "Lithuania": (25.28, 54.69), "Poland": (21.01, 52.23), "Czech Republic": (14.44, 50.08),
    "Slovakia": (17.11, 48.15), "Hungary": (19.04, 47.50), "Romania": (26.10, 44.43),
    "Bulgaria": (23.32, 42.70), "Greece": (23.73, 37.98), "Serbia": (20.46, 44.79),
    "Croatia": (15.98, 45.81), "Slovenia": (14.51, 46.06), "Albania": (19.82, 41.33),
    "Kosovo": (21.17, 42.66), "North Macedonia": (21.43, 42.00), "Bosnia and Herzegovina": (18.41, 43.86),
    "Montenegro": (19.26, 42.44), "Cyprus": (33.38, 35.19), "Malta": (14.51, 35.90),
    "Iceland": (-21.94, 64.15), "European Union": (4.35, 50.85),
    # Middle East and Africa
    "Israel": (34.78, 32.09), "Jordan": (35.93, 31.95), "Lebanon": (35.50, 33.89), "Iraq": (44.37, 33.31),
    "Egypt": (31.24, 30.04), "Morocco": (-7.59, 33.57), "Tunisia": (10.18, 36.81), "Algeria": (3.06, 36.75),
    "Nigeria": (3.38, 6.52), "Ghana": (-0.19, 5.60), "Kenya": (36.82, -1.29), "Ethiopia": (38.75, 9.03),
    "Tanzania": (39.27, -6.79), "Uganda": (32.58, 0.35), "Rwanda": (30.06, -1.94),
    "South Africa": (28.05, -26.20), "Senegal": (-17.47, 14.72), "Côte d'Ivoire": (-4.01, 5.36),
    "Pakistan": (67.01, 24.86),
    # Asia-Pacific
    "India": (72.88, 19.08), "Bangladesh": (90.41, 23.81), "Sri Lanka": (79.86, 6.93),
    "China": (121.47, 31.23), "Hong Kong": (114.17, 22.32), "Taiwan": (121.56, 25.03),
    "Japan": (139.69, 35.69), "South Korea": (126.98, 37.57), "Singapore": (103.82, 1.35),
    "Malaysia": (101.69, 3.14), "Indonesia": (106.85, -6.21), "Thailand": (100.50, 13.76),
    "Vietnam": (106.70, 10.78), "Philippines": (121.00, 14.60), "Cambodia": (104.92, 11.56),
    "Mongolia": (106.91, 47.89), "Australia": (151.21, -33.87), "New Zealand": (174.76, -36.85),
    # Americas
    "United States": (-74.01, 40.71), "Canada": (-79.38, 43.65), "Mexico": (-99.13, 19.43),
    "Brazil": (-46.63, -23.55), "Argentina": (-58.38, -34.60), "Chile": (-70.67, -33.45),
    "Colombia": (-74.07, 4.71), "Peru": (-77.04, -12.05),
}

ALIASES = {
    "Turkey": "Türkiye", "Turkiye": "Türkiye", "UAE": "United Arab Emirates", "U.A.E.": "United Arab Emirates",
    "UK": "United Kingdom", "Britain": "United Kingdom", "Great Britain": "United Kingdom", "England": "United Kingdom",
    "US": "United States", "USA": "United States", "U.S.": "United States", "United States of America": "United States",
    "Korea": "South Korea", "Republic of Korea": "South Korea", "Czechia": "Czech Republic",
    "KSA": "Saudi Arabia", "Ivory Coast": "Côte d'Ivoire", "EU": "European Union", "Europe": "European Union",
    "Russian Federation": "Russia", "Holland": "Netherlands",
}


def coords_for(item: dict) -> tuple[float, float] | None:
    """(lon, lat) for an item, or None when we don't know where it happened."""
    country = (item.get("country") or "").strip()
    country = ALIASES.get(country, country)
    if country in COUNTRY_COORDS:
        return COUNTRY_COORDS[country]
    if item.get("region") == "Azerbaijan":
        return BAKU
    guess = rules.detect_country(f"{item.get('title', '')} {item.get('summary', '')}")
    if guess:
        guess = ALIASES.get(guess, guess)
        return COUNTRY_COORDS.get(guess)
    return None


def place_name(item: dict) -> str | None:
    """The country name shown on the blip label, matching coords_for."""
    country = ALIASES.get((item.get("country") or "").strip(), (item.get("country") or "").strip())
    if country in COUNTRY_COORDS:
        return country
    if item.get("region") == "Azerbaijan":
        return "Azerbaijan"
    guess = rules.detect_country(f"{item.get('title', '')} {item.get('summary', '')}")
    return ALIASES.get(guess, guess) if guess else None
