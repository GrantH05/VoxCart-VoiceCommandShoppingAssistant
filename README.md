# VoxCart - Voice Command Shopping Assistant

VoxCart is a Python + Streamlit shopping-list assistant built for a software-engineering technical assessment. It accepts typed or spoken commands, understands common natural-language phrasing in multiple languages, manages shopping-list quantities, categorizes products, searches a sample catalog, and generates simple explainable recommendations.

## Features

- Voice commands through `streamlit-mic-recorder`
- English, Hindi, Spanish, and French speech modes
- Natural-language command parser for add, remove, update, clear, and search intents
- Quantity and unit extraction, e.g. `Add 2 bottles of water`
- Automatic product categories
- Product search by item, brand, and maximum price
- Voice search such as `Find toothpaste under $5`
- Shopping-history recommendations
- Seasonal and sale recommendations
- Product substitutes and a plant-based preference mode
- SQLite persistence
- Loading, success, warning, and empty states
- Mobile-friendly Streamlit layout
- Typed-command fallback if microphone permission is unavailable

## Tech stack

- Python
- Streamlit
- streamlit-mic-recorder
- SQLite
- Standard-library regex-based NLP

The NLP layer is intentionally lightweight and explainable for an 8-hour assessment. A production version could replace or augment it with an LLM/NLU API and connect search/recommendations to a real retailer catalog.

## Run locally

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run:

```bash
streamlit run app.py
```

Then open the local URL printed by Streamlit, normally `http://localhost:8501`.

## Demo commands

English:

```text
Add milk
Add 2 bottles of water
I need 5 oranges
Change milk quantity to 3
Remove milk from my list
Find organic apples
Find toothpaste under $5
Clear my list
```

Hindi:

```text
मुझे पांच संतरे चाहिए
दो बोतल पानी जोड़ो
दूध हटाओ
```

Spanish:

```text
Agrega dos botellas de agua
Necesito cinco naranjas
Quita leche
```

French:

```text
Ajoute deux bouteilles d'eau
J'ai besoin de cinq oranges
Retire le lait
```

## Project structure

```text
voice-shopping-assistant-streamlit/
├── app.py
├── core/
│   ├── catalog.py
│   ├── database.py
│   ├── nlp.py
│   └── services.py
├── tests/
│   └── test_nlp.py
├── .streamlit/
│   └── config.toml
├── requirements.txt
├── README.md
└── .gitignore
```
