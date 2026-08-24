from __future__ import annotations

from datetime import datetime

from .catalog import all_products, by_name, category_for_item, search_products
from .database import add_item, clear_list, frequent_added_items, list_items, remove_item, update_item
from .nlp import ParsedCommand


def execute_command(command: ParsedCommand) -> dict:
    if command.action == "unknown":
        return {"ok": False, "message": "I couldn't understand that command."}

    if command.action == "clear":
        clear_list()
        return {"ok": True, "message": "Shopping list cleared."}

    if not command.item:
        return {"ok": False, "message": "I understood the action, but not the item name."}

    if command.action == "add":
        product = by_name(command.item)
        if product and not product.available:
            substitute_text = f" Try {', '.join(product.substitutes)} instead." if product.substitutes else ""
            return {"ok": False, "message": f"{product.name} is currently unavailable.{substitute_text}"}
        add_item(command.item, command.quantity, command.unit, category_for_item(command.item))
        return {
            "ok": True,
            "message": f"Added {command.quantity} {display_unit(command.unit, command.quantity)} of {command.item}.",
        }

    if command.action == "remove":
        removed = remove_item(command.item)
        return {
            "ok": removed,
            "message": f"Removed {command.item}." if removed else f"{command.item} is not on your list.",
        }

    if command.action == "update":
        updated = update_item(command.item, command.quantity, command.unit)
        return {
            "ok": updated,
            "message": f"Updated {command.item} to {command.quantity} {display_unit(command.unit, command.quantity)}."
            if updated else f"{command.item} is not on your list yet.",
        }

    if command.action == "search":
        results = search_products(command.item, command.brand, command.max_price)
        return {"ok": True, "message": f"Found {len(results)} matching product(s).", "results": results}

    return {"ok": False, "message": "That command is not supported yet."}


def display_unit(unit: str, quantity: int) -> str:
    if unit == "item":
        return "item" if quantity == 1 else "items"
    if unit == "bottle":
        return "bottle" if quantity == 1 else "bottles"
    if unit == "pack":
        return "pack" if quantity == 1 else "packs"
    return unit


def suggestions(preference: str = "No preference") -> list[dict]:
    current_names = {item["name"].lower() for item in list_items()}
    result: list[dict] = []
    seen: set[str] = set()

    # History-based recommendations.
    for row in frequent_added_items(8):
        product = by_name(row["name"])
        if product and product.available and product.name.lower() not in current_names and product.name not in seen:
            result.append({"product": product, "reason": f"You added this {row['times_added']} time(s) before."})
            seen.add(product.name)

    month = datetime.now().month
    for product in all_products():
        if not product.available or product.name.lower() in current_names or product.name in seen:
            continue
        if month in product.seasonal_months:
            result.append({"product": product, "reason": "Seasonal pick for this month."})
            seen.add(product.name)

    for product in all_products():
        if not product.available or product.name.lower() in current_names or product.name in seen:
            continue
        if product.on_sale:
            result.append({"product": product, "reason": "Currently marked as on sale in the demo catalog."})
            seen.add(product.name)

    if preference == "Plant-based":
        for name in ("Almond Milk", "Soy Milk"):
            product = by_name(name)
            if product and product.name.lower() not in current_names and product.name not in seen:
                result.insert(0, {"product": product, "reason": "Matches your plant-based preference."})
                seen.add(product.name)

    if preference == "Budget-friendly":
        cheap = sorted((p for p in all_products() if p.available), key=lambda p: p.price)
        for product in cheap[:4]:
            if product.name.lower() not in current_names and product.name not in seen:
                result.insert(0, {"product": product, "reason": "Low-price option from the demo catalog."})
                seen.add(product.name)

    return result[:8]


def substitutes_for(name: str, preference: str = "No preference") -> list:
    product = by_name(name)
    if not product:
        return []
    substitute_names = list(product.substitutes)
    if preference == "Plant-based" and product.name == "Milk":
        substitute_names = ["Almond Milk", "Soy Milk"] + substitute_names
    seen: set[str] = set()
    result = []
    for sub_name in substitute_names:
        sub = by_name(sub_name)
        if sub and sub.available and sub.name not in seen:
            result.append(sub)
            seen.add(sub.name)
    return result
