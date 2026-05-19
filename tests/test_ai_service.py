from types import SimpleNamespace

from app.services.ai_service import classify_document


def test_classify_document_uses_fallback_for_invoice_text() -> None:
    text = "Fattura numero 15 con imponibile, IVA e totale da saldare entro 30 giorni."
    result = classify_document(text)

    assert result["category"] == "fattura"
    assert result["source"] in {"fallback", "llm"}
    assert result["summary"]


def test_classify_document_uses_strongest_fallback_category() -> None:
    text = (
        "Contratto di fornitura annuale con durata di 12 mesi. "
        "Le clausole prevedono pagamento a 30 giorni data fattura."
    )
    result = classify_document(text)

    assert result["category"] == "contratto"


def test_classify_document_falls_back_when_provider_fails(monkeypatch) -> None:
    class FailingCompletions:
        @staticmethod
        def create(**_: object) -> object:
            raise RuntimeError("provider unavailable")

    class FailingOpenAI:
        def __init__(self, **_: object) -> None:
            self.chat = SimpleNamespace(completions=FailingCompletions())

    monkeypatch.setattr(
        "app.services.ai_service.get_settings",
        lambda: SimpleNamespace(openai_api_key="test-key", openai_model="test-model"),
    )
    monkeypatch.setattr("app.services.ai_service.OpenAI", FailingOpenAI)

    result = classify_document("Contratto di consulenza con durata annuale.")

    assert result["category"] == "contratto"
    assert result["source"] == "fallback"
