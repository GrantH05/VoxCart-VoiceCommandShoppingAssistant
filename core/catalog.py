from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class Product:
    name: str
    category: str
    brands: tuple[str, ...]
    price: float
    available: bool = True
    on_sale: bool = False
    seasonal_months: tuple[int, ...] = ()
    substitutes: tuple[str, ...] = ()
    aliases: tuple[str, ...] = ()


PRODUCTS: tuple[Product, ...] = (
    Product(
        "Milk", "Dairy", ("Amul", "Mother Dairy"), 1.80,
        substitutes=("Almond Milk", "Soy Milk"),
        aliases=("milk", "दूध", "leche", "lait"),
    ),
    Product(
        "Almond Milk", "Dairy Alternatives", ("So Good", "Raw Pressery"), 3.90,
        on_sale=True, aliases=("almond milk", "बादाम दूध", "leche de almendras", "lait d'amande"),
    ),
    Product(
        "Soy Milk", "Dairy Alternatives", ("Sofit",), 3.20,
        aliases=("soy milk", "सोया दूध", "leche de soja", "lait de soja"),
    ),
    Product(
        "Bread", "Bakery", ("Britannia", "Harvest Gold"), 1.50,
        on_sale=True, substitutes=("Whole Wheat Bread",),
        aliases=("bread", "ब्रेड", "pan", "pain"),
    ),
    Product(
        "Whole Wheat Bread", "Bakery", ("Harvest Gold",), 1.90,
        aliases=("whole wheat bread", "brown bread", "गेहूं की ब्रेड", "pan integral", "pain complet"),
    ),
    Product(
        "Bananas", "Produce", ("Fresh",), 0.90,
        seasonal_months=tuple(range(1, 13)),
        aliases=("banana", "bananas", "केला", "केले", "plátano", "platano", "banane", "bananes"),
    ),
    Product(
        "Apples", "Produce", ("Fresh", "Organic Farms"), 2.40,
        seasonal_months=(8, 9, 10, 11),
        aliases=("apple", "apples", "सेब", "manzana", "manzanas", "pomme", "pommes"),
    ),
    Product(
        "Organic Apples", "Produce", ("Organic Farms",), 3.70,
        seasonal_months=(8, 9, 10, 11), on_sale=True,
        aliases=("organic apple", "organic apples", "ऑर्गेनिक सेब", "manzana orgánica", "manzanas organicas", "pomme bio", "pommes bio"),
    ),
    Product(
        "Oranges", "Produce", ("Fresh",), 2.10,
        seasonal_months=(11, 12, 1, 2, 3),
        aliases=("orange", "oranges", "संतरा", "संतरे", "naranja", "naranjas", "orange", "oranges"),
    ),
    Product(
        "Water", "Beverages", ("Bisleri", "Aquafina", "Kinley"), 0.70,
        aliases=("water", "bottle of water", "bottles of water", "पानी", "पानी की बोतल", "agua", "eau"),
    ),
    Product(
        "Toothpaste", "Personal Care", ("Colgate", "Pepsodent", "Sensodyne"), 4.30,
        on_sale=True,
        aliases=("toothpaste", "टूथपेस्ट", "pasta de dientes", "dentifrice"),
    ),
    Product(
        "Eggs", "Dairy & Eggs", ("Farm Fresh",), 2.80,
        aliases=("egg", "eggs", "अंडा", "अंडे", "huevo", "huevos", "oeuf", "oeufs"),
    ),
    Product(
        "Rice", "Pantry", ("India Gate", "Daawat"), 5.40,
        aliases=("rice", "चावल", "arroz", "riz"),
    ),
    Product(
        "Potato Chips", "Snacks", ("Lay's", "Bingo"), 1.20,
        on_sale=True,
        aliases=("chips", "potato chips", "चिप्स", "papas fritas", "chips de pomme de terre"),
    ),
    Product(
        "Tomatoes", "Produce", ("Fresh",), 1.30,
        seasonal_months=tuple(range(1, 13)),
        aliases=("tomato", "tomatoes", "टमाटर", "tomate", "tomates"),
    ),
    Product(
        "Mangoes", "Produce", ("Fresh",), 3.00,
        available=False, seasonal_months=(4, 5, 6, 7), substitutes=("Bananas", "Apples"),
        aliases=("mango", "mangoes", "आम", "mango", "mangue", "mangues"),
    ),
)


def all_products() -> tuple[Product, ...]:
    return PRODUCTS


def by_name(name: str) -> Product | None:
    lower = name.strip().lower()
    for product in PRODUCTS:
        if product.name.lower() == lower:
            return product
    return None


def alias_map() -> dict[str, str]:
    result: dict[str, str] = {}
    for product in PRODUCTS:
        result[product.name.lower()] = product.name
        for alias in product.aliases:
            result[alias.lower()] = product.name
    return result


def search_products(
    query: str = "",
    brand: str | None = None,
    max_price: float | None = None,
    available_only: bool = False,
) -> list[Product]:
    q = query.strip().lower()
    brand_q = brand.strip().lower() if brand else None
    matches: list[Product] = []
    for product in PRODUCTS:
        searchable = " ".join((product.name, product.category, *product.brands, *product.aliases)).lower()
        if q and q not in searchable:
            continue
        if brand_q and not any(brand_q in b.lower() for b in product.brands):
            continue
        if max_price is not None and product.price > max_price:
            continue
        if available_only and not product.available:
            continue
        matches.append(product)
    return matches


def category_for_item(item_name: str) -> str:
    product = by_name(item_name)
    if product:
        return product.category

    name = item_name.lower()
    keyword_categories: list[tuple[Iterable[str], str]] = [
        (("milk", "cheese", "yogurt", "दूध"), "Dairy"),
        (("apple", "banana", "orange", "tomato", "fruit", "vegetable", "सेब", "केला"), "Produce"),
        (("bread", "bun", "cake"), "Bakery"),
        (("chips", "cookie", "snack"), "Snacks"),
        (("water", "juice", "soda"), "Beverages"),
        (("rice", "flour", "oil", "sugar"), "Pantry"),
    ]
    for keywords, category in keyword_categories:
        if any(k in name for k in keywords):
            return category
    return "Other"
