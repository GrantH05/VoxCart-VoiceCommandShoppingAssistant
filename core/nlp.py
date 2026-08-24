from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

from .catalog import alias_map


@dataclass
class ParsedCommand:
    action: str
    item: str = ""
    quantity: int = 1
    unit: str = "item"
    brand: str | None = None
    max_price: float | None = None
    raw: str = ""


NUMBER_WORDS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
    "एक": 1, "दो": 2, "तीन": 3, "चार": 4, "पांच": 5, "पाँच": 5, "छह": 6, "सात": 7, "आठ": 8, "नौ": 9, "दस": 10,
    "uno": 1, "una": 1, "dos": 2, "tres": 3, "cuatro": 4, "cinco": 5, "seis": 6, "siete": 7, "ocho": 8, "nueve": 9, "diez": 10,
    "un": 1, "une": 1, "deux": 2, "trois": 3, "quatre": 4, "cinq": 5, "six": 6, "sept": 7, "huit": 8, "neuf": 9, "dix": 10,
}

UNIT_ALIASES = {
    "bottle": "bottle", "bottles": "bottle", "बोतल": "bottle", "botella": "bottle", "botellas": "bottle", "bouteille": "bottle", "bouteilles": "bottle",
    "kg": "kg", "kilogram": "kg", "kilograms": "kg", "किलो": "kg", "kilo": "kg", "kilos": "kg",
    "pack": "pack", "packs": "pack", "packet": "pack", "packets": "pack", "पैकेट": "pack", "paquete": "pack", "paquets": "pack",
    "dozen": "dozen", "दर्जन": "dozen", "docena": "dozen", "douzaine": "dozen",
}

ACTION_PATTERNS = {
    "clear": [r"\bclear (?:my )?list\b", r"\bempty (?:my )?list\b", r"सूची साफ", r"vaciar (?:mi )?lista", r"vider (?:ma )?liste"],
    "remove": [r"\bremove\b", r"\bdelete\b", r"\btake .* off\b", r"हटाओ", r"हटा दो", r"निकालो", r"elimina", r"quitar", r"quita", r"supprime", r"retire"],
    "update": [r"\bchange\b", r"\bupdate\b", r"\bset\b", r"मात्रा", r"बदल", r"cambia", r"actualiza", r"modifier", r"change"],
    "search": [r"\bfind\b", r"\bsearch\b", r"\bshow me\b", r"ढूंढ", r"खोज", r"buscar", r"busca", r"encuentra", r"trouve", r"chercher", r"recherche"],
    "add": [r"\badd\b", r"\bi need\b", r"\bi want(?: to buy)?\b", r"\bbuy\b", r"\bget me\b", r"\bput\b", r"जोड़", r"चाहिए", r"खरीद", r"agrega", r"añade", r"anade", r"necesito", r"quiero comprar", r"compra", r"ajoute", r"j'ai besoin", r"je veux acheter", r"achète", r"achete"],
}

FILLER_PATTERNS = [
    r"\bto (?:my|the) (?:shopping )?list\b", r"\bon (?:my|the) (?:shopping )?list\b", r"\bplease\b",
    r"मेरी सूची में", r"लिस्ट में", r"कृपया",
    r"a mi lista", r"en mi lista", r"por favor",
    r"à ma liste", r"a ma liste", r"dans ma liste", r"s'il vous plaît", r"s'il vous plait",
]

PRICE_PATTERNS = [
    r"(?:under|below|less than|max(?:imum)?|up to)\s*[$₹€£]?\s*(\d+(?:\.\d+)?)",
    r"[$₹€£]\s*(\d+(?:\.\d+)?)\s*(?:or less|maximum|max)?",
    r"(\d+(?:\.\d+)?)\s*(?:से कम|के नीचे)",
    r"(?:menos de|hasta)\s*[$₹€£]?\s*(\d+(?:\.\d+)?)",
    r"(?:moins de|jusqu['’]?à)\s*[$₹€£]?\s*(\d+(?:\.\d+)?)",
]

BRAND_PATTERNS = [r"\bbrand\s+([\w' -]+)", r"\bby\s+([\w' -]+)", r"marca\s+([\w' -]+)", r"marque\s+([\w' -]+)"]

KNOWN_BRANDS = [
    "amul", "mother dairy", "so good", "raw pressery", "sofit", "britannia", "harvest gold",
    "organic farms", "bisleri", "aquafina", "kinley", "colgate", "pepsodent", "sensodyne",
    "farm fresh", "india gate", "daawat", "lay's", "bingo",
]


def strip_accents(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    return "".join(ch for ch in normalized if not unicodedata.combining(ch))


def normalize(text: str) -> str:
    text = text.strip().lower().replace("’", "'")
    text = re.sub(r"[,.!?;:]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def detect_action(text: str) -> str:
    for action in ("clear", "remove", "update", "search", "add"):
        if any(re.search(pattern, text, re.I) for pattern in ACTION_PATTERNS[action]):
            return action
    return "add"


def extract_quantity(text: str) -> tuple[int, str]:
    digit_match = re.search(r"\b(\d+)\b", text)
    quantity = int(digit_match.group(1)) if digit_match else 1
    if not digit_match:
        for token in text.split():
            clean = token.strip(".,")
            if clean in NUMBER_WORDS:
                quantity = NUMBER_WORDS[clean]
                break

    unit = "item"
    for alias, canonical in UNIT_ALIASES.items():
        if re.search(rf"(?<!\w){re.escape(alias)}(?!\w)", text, re.I):
            unit = canonical
            break
    return max(quantity, 1), unit


def extract_price(text: str) -> float | None:
    for pattern in PRICE_PATTERNS:
        match = re.search(pattern, text, re.I)
        if match:
            return float(match.group(1))
    return None


def extract_brand(text: str) -> str | None:
    lower = text.lower()
    for brand in KNOWN_BRANDS:
        if brand in lower:
            return brand.title()
    for pattern in BRAND_PATTERNS:
        match = re.search(pattern, text, re.I)
        if match:
            return match.group(1).strip().title()
    return None


def canonical_product(text: str) -> str | None:
    aliases = alias_map()
    candidates = sorted(aliases, key=len, reverse=True)
    lower = text.lower()
    accentless = strip_accents(lower)
    for alias in candidates:
        if alias in lower or strip_accents(alias) in accentless:
            return aliases[alias]
    return None


def clean_item_text(text: str, action: str, quantity: int, unit: str, max_price: float | None, brand: str | None) -> str:
    cleaned = text
    for pattern in ACTION_PATTERNS.get(action, []):
        cleaned = re.sub(pattern, " ", cleaned, flags=re.I)
    for pattern in FILLER_PATTERNS:
        cleaned = re.sub(pattern, " ", cleaned, flags=re.I)
    for pattern in PRICE_PATTERNS:
        cleaned = re.sub(pattern, " ", cleaned, flags=re.I)
    for pattern in BRAND_PATTERNS:
        cleaned = re.sub(pattern, " ", cleaned, flags=re.I)
    if brand:
        cleaned = re.sub(re.escape(brand), " ", cleaned, flags=re.I)

    cleaned = re.sub(rf"\b{quantity}\b", " ", cleaned)
    for word, value in NUMBER_WORDS.items():
        if value == quantity:
            cleaned = re.sub(rf"(?<!\w){re.escape(word)}(?!\w)", " ", cleaned, flags=re.I)
    for alias in UNIT_ALIASES:
        cleaned = re.sub(rf"(?<!\w){re.escape(alias)}(?!\w)", " ", cleaned, flags=re.I)

    # Extra relation words commonly left after update/search commands.
    cleaned = re.sub(r"\b(quantity|qty|to|of|for|than|organic)\b", " ", cleaned, flags=re.I)
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" -")
    return cleaned


def parse_command(raw_text: str) -> ParsedCommand:
    text = normalize(raw_text)
    if not text:
        return ParsedCommand(action="unknown", raw=raw_text)

    action = detect_action(text)
    if action == "clear":
        return ParsedCommand(action="clear", raw=raw_text)

    quantity, unit = extract_quantity(text)
    max_price = extract_price(text)
    brand = extract_brand(text)
    canonical = canonical_product(text)

    item = canonical or clean_item_text(text, action, quantity, unit, max_price, brand)
    if action == "search" and canonical is None:
        # Keep useful qualifiers such as "organic" for search.
        item = text
        for pattern in ACTION_PATTERNS["search"] + FILLER_PATTERNS + PRICE_PATTERNS:
            item = re.sub(pattern, " ", item, flags=re.I)
        if brand:
            item = re.sub(re.escape(brand), " ", item, flags=re.I)
        item = re.sub(r"\s+", " ", item).strip()

    return ParsedCommand(
        action=action,
        item=item.title() if item and canonical is None else (item or ""),
        quantity=quantity,
        unit=unit,
        brand=brand,
        max_price=max_price,
        raw=raw_text,
    )
