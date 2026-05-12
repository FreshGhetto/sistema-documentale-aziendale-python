import json
from collections.abc import Iterable

from openai import OpenAI

from app.config import get_settings


ALLOWED_CATEGORIES = ["contratto", "ordine", "fattura", "cv", "comunicazione", "altro"]


def _fallback_category(text: str) -> tuple[str, str]:
    lowered = text.lower()
    mapping: Iterable[tuple[str, list[str], str]] = [
        ("fattura", ["fattura", "iva", "imponibile"], "Documento economico con importi e dati di fatturazione."),
        ("contratto", ["contratto", "clausola", "durata"], "Documento contrattuale con condizioni e durata."),
        ("ordine", ["ordine", "acquisto", "fornitura"], "Documento operativo relativo a un ordine o acquisto."),
        ("cv", ["curriculum", "esperienza", "competenze"], "Documento di candidatura con esperienze e competenze."),
        ("comunicazione", ["circolare", "comunicazione", "avviso"], "Comunicazione interna o esterna."),
    ]
    for category, keywords, summary in mapping:
        if any(keyword in lowered for keyword in keywords):
            return category, summary
    return "altro", "Classificazione automatica non disponibile: documento assegnato alla categoria generica."


def classify_document(text: str) -> dict[str, str]:
    settings = get_settings()
    excerpt = text[:6000]
    if not settings.openai_api_key:
        category, summary = _fallback_category(excerpt)
        return {"category": category, "summary": summary, "source": "fallback"}

    client = OpenAI(api_key=settings.openai_api_key)
    prompt = (
        "Classifica il documento in una categoria tra: "
        f"{', '.join(ALLOWED_CATEGORIES)}. "
        "Rispondi solo con JSON valido nel formato "
        '{"category":"...","summary":"..."} '
        "dove summary e' una sintesi in massimo 30 parole."
    )
    response = client.chat.completions.create(
        model=settings.openai_model,
        temperature=0,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": excerpt},
        ],
    )
    content = response.choices[0].message.content or "{}"
    try:
        parsed = json.loads(content)
        category = parsed.get("category", "altro")
        summary = parsed.get("summary", "Sintesi non disponibile.")
        if category not in ALLOWED_CATEGORIES:
            category = "altro"
        return {"category": category, "summary": summary, "source": "llm"}
    except json.JSONDecodeError:
        category, summary = _fallback_category(excerpt)
        return {"category": category, "summary": summary, "source": "fallback"}
