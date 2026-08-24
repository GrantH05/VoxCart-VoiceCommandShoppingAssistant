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

## Run tests

```bash
python -m unittest discover -s tests -v
```

## Deploy on Streamlit Community Cloud

1. Push this folder to a GitHub repository.
2. Sign in to Streamlit Community Cloud.
3. Create a new app from the GitHub repository.
4. Set the main file to `app.py`.
5. Deploy.
6. Allow microphone permission in the browser when testing voice input.

SQLite is suitable for this assessment demo. On some hosted environments the local file system can be ephemeral, so production persistence should use a managed database.

## Approach write-up (under 200 words)

I built VoxCart as a lightweight Python and Streamlit application focused on completing the assessment's user-facing flows within the eight-hour constraint. Voice transcription is handled through a Streamlit microphone component, while a small rule-based NLP layer converts flexible phrases into structured actions such as add, remove, update, clear, and search. The parser also extracts quantities, units, product names, brands, and price limits and supports common phrases in English, Hindi, Spanish, and French. Shopping-list and history data are stored in SQLite, which keeps the demo simple while still providing persistent state locally. A sample product catalog powers category assignment, availability checks, price filtering, sale/seasonal suggestions, and substitutes. Smart suggestions combine previous shopping history with seasonal products, sale flags, and an optional user preference. The UI provides immediate transcription feedback, loading states, confirmations, mobile-friendly list controls, manual typing as a fallback, and separate views for list management, catalog search, suggestions, and history. In production, I would replace the sample catalog with retailer APIs and use a managed database and stronger NLU service.
