from app.services.ai_service import classify_document


def test_classify_document_uses_fallback_for_invoice_text() -> None:
    text = "Fattura numero 15 con imponibile, IVA e totale da saldare entro 30 giorni."
    result = classify_document(text)

    assert result["category"] == "fattura"
    assert result["source"] in {"fallback", "llm"}
    assert result["summary"]
