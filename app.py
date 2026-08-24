from __future__ import annotations

import streamlit as st
from streamlit_mic_recorder import speech_to_text

from core.catalog import all_products, by_name, search_products
from core.database import add_item, history, init_db, list_items, remove_item, update_item
from core.nlp import parse_command
from core.services import execute_command, suggestions, substitutes_for


st.set_page_config(page_title="VoxCart", page_icon="🛒", layout="wide", initial_sidebar_state="expanded")
init_db()

LANGUAGES = {
    "English": "en",
    "Hindi": "hi",
    "Spanish": "es",
    "French": "fr",
}

EXAMPLES = {
    "English": ["Add 2 bottles of water", "I need 5 oranges", "Remove milk", "Find toothpaste under $5"],
    "Hindi": ["दो बोतल पानी जोड़ो", "मुझे पांच संतरे चाहिए", "दूध हटाओ", "टूथपेस्ट 5 से कम ढूंढो"],
    "Spanish": ["Agrega dos botellas de agua", "Necesito cinco naranjas", "Quita leche", "Busca pasta de dientes menos de 5"],
    "French": ["Ajoute deux bouteilles d'eau", "J'ai besoin de cinq oranges", "Retire le lait", "Trouve dentifrice moins de 5"],
}


st.markdown(
    """
    <style>
        .block-container {padding-top: 1.4rem; padding-bottom: 3rem; max-width: 1180px;}
        .hero {padding: 1.2rem 1.4rem; border-radius: 20px; border: 1px solid rgba(128,128,128,.22); margin-bottom: 1rem;}
        .hero h1 {margin: 0 0 .25rem 0; font-size: 2.35rem;}
        .muted {opacity: .72;}
        .pill {display:inline-block; padding:.25rem .55rem; margin:.1rem .15rem .1rem 0; border-radius:999px; border:1px solid rgba(128,128,128,.25); font-size:.83rem;}
        div[data-testid="stMetric"] {border:1px solid rgba(128,128,128,.18); padding:.6rem; border-radius:16px;}
        @media (max-width: 640px) {.hero h1 {font-size:1.8rem;} .block-container {padding-left:1rem; padding-right:1rem;}}
    </style>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("⚙️ Settings")
    language_name = st.selectbox("Voice language", list(LANGUAGES), index=0)
    preference = st.selectbox("Suggestion preference", ["No preference", "Plant-based", "Budget-friendly"])
    st.caption("Voice transcription uses your browser microphone and the speech-to-text component's Google recognition support.")
    st.divider()
    st.subheader("Try saying")
    for sample in EXAMPLES[language_name]:
        st.caption(f"• {sample}")

st.markdown(
    """
    <div class="hero">
        <h1>🛒 VoxCart</h1>
        <div class="muted">Voice-first shopping list manager with multilingual commands, smart suggestions, product search and substitutes.</div>
    </div>
    """,
    unsafe_allow_html=True,
)

items = list_items()
m1, m2, m3 = st.columns(3)
m1.metric("Items on list", len(items))
m2.metric("Total quantity", sum(int(x["quantity"]) for x in items))
m3.metric("Categories", len({x["category"] for x in items}))

st.subheader("🎙️ Voice command")
voice_col, typed_col = st.columns([1, 1.25])

with voice_col:
    st.caption("Click once to start recording, then click again to stop.")
    transcript = speech_to_text(
        language=LANGUAGES[language_name],
        start_prompt="🎙️ Start speaking",
        stop_prompt="⏹️ Stop recording",
        just_once=True,
        use_container_width=True,
        key=f"voice_{LANGUAGES[language_name]}",
    )

with typed_col:
    typed_command = st.text_input(
        "Or type a command",
        placeholder="Add 2 bottles of water",
        label_visibility="visible",
    )
    run_typed = st.button("Run command", use_container_width=True, type="primary")

command_text = transcript or (typed_command if run_typed else "")
if transcript:
    st.info(f"Recognized: **{transcript}**")

if command_text:
    with st.spinner("Understanding your command..."):
        parsed = parse_command(command_text)
        response = execute_command(parsed)

    parsed_bits = [f"Action: {parsed.action}"]
    if parsed.item:
        parsed_bits.append(f"Item: {parsed.item}")
    if parsed.quantity:
        parsed_bits.append(f"Qty: {parsed.quantity}")
    if parsed.brand:
        parsed_bits.append(f"Brand: {parsed.brand}")
    if parsed.max_price is not None:
        parsed_bits.append(f"Max price: ${parsed.max_price:.2f}")
    st.caption(" • ".join(parsed_bits))

    if response["ok"]:
        st.success(response["message"])
    else:
        st.warning(response["message"])

    if response.get("results") is not None:
        st.session_state["voice_search_results"] = [p.name for p in response["results"]]

    # Force fresh values in the sections below after command execution.
    items = list_items()

st.divider()

tab_list, tab_search, tab_suggest, tab_history = st.tabs([
    "📝 Shopping List", "🔎 Product Search", "✨ Suggestions", "🕘 History"
])

with tab_list:
    items = list_items()
    if not items:
        st.info("Your list is empty. Try: “Add milk” or “Add 2 bottles of water”.")
    else:
        categories = {}
        for item in items:
            categories.setdefault(item["category"], []).append(item)

        for category, cat_items in categories.items():
            st.markdown(f"### {category}")
            for item in cat_items:
                c1, c2, c3, c4 = st.columns([3, 1.2, 1.6, 1])
                c1.markdown(f"**{item['name']}**")
                new_qty = c2.number_input(
                    "Quantity", min_value=1, max_value=99, value=int(item["quantity"]),
                    key=f"qty_{item['id']}", label_visibility="collapsed"
                )
                c3.caption(f"Unit: {item['unit']}")
                if c3.button("Update", key=f"update_{item['id']}", use_container_width=True):
                    update_item(item["name"], int(new_qty), item["unit"])
                    st.success(f"Updated {item['name']}.")
                    st.rerun()
                if c4.button("Remove", key=f"remove_{item['id']}", use_container_width=True):
                    remove_item(item["name"])
                    st.rerun()

                subs = substitutes_for(item["name"], preference)
                if subs:
                    st.caption("Substitutes: " + ", ".join(f"{p.name} (${p.price:.2f})" for p in subs))

with tab_search:
    st.markdown("### Search catalog")
    s1, s2, s3 = st.columns([2.2, 1.4, 1.2])
    query = s1.text_input("Item / category", placeholder="organic apples", key="catalog_query")
    brand_options = ["Any brand"] + sorted({brand for p in all_products() for brand in p.brands})
    brand = s2.selectbox("Brand", brand_options)
    max_price = s3.number_input("Max price ($)", min_value=0.0, value=0.0, step=0.5, help="0 means no limit")

    voice_names = st.session_state.get("voice_search_results", [])
    if voice_names and not query:
        results = [p for p in all_products() if p.name in voice_names]
        st.caption("Showing results from your most recent voice search.")
    else:
        results = search_products(
            query=query,
            brand=None if brand == "Any brand" else brand,
            max_price=None if max_price <= 0 else float(max_price),
        )

    if not results:
        st.warning("No matching products found.")
    for idx, product in enumerate(results):
        with st.container(border=True):
            r1, r2, r3 = st.columns([3, 1.2, 1.2])
            r1.markdown(f"**{product.name}**  \n{product.category} • {', '.join(product.brands)}")
            sale = " • SALE" if product.on_sale else ""
            availability = "Available" if product.available else "Unavailable"
            r2.markdown(f"**${product.price:.2f}**  \n{availability}{sale}")
            if product.available:
                if r3.button("Add", key=f"search_add_{idx}_{product.name}", use_container_width=True):
                    add_item(product.name, 1, "item", product.category)
                    st.success(f"Added {product.name}.")
                    st.rerun()
            else:
                subs = substitutes_for(product.name, preference)
                r3.caption("Try: " + ", ".join(p.name for p in subs) if subs else "No substitute listed")

with tab_suggest:
    st.markdown("### Smart suggestions")
    st.caption("Suggestions combine shopping history, seasonal items, sale flags and your selected preference.")
    recs = suggestions(preference)
    if not recs:
        st.info("Add and remove a few products first so history-based recommendations can learn your pattern.")
    for idx, rec in enumerate(recs):
        product = rec["product"]
        with st.container(border=True):
            c1, c2, c3 = st.columns([3, 1.1, 1.1])
            c1.markdown(f"**{product.name}**  \n{rec['reason']}")
            c2.markdown(f"${product.price:.2f}")
            if c3.button("Add", key=f"suggest_add_{idx}_{product.name}", use_container_width=True):
                add_item(product.name, 1, "item", product.category)
                st.rerun()

with tab_history:
    rows = history(100)
    if not rows:
        st.info("No shopping history yet.")
    else:
        st.dataframe(rows, use_container_width=True, hide_index=True)

st.divider()
st.caption("Demo catalog prices and sale/availability flags are sample data for the technical assessment. Replace them with a real commerce API in production.")
