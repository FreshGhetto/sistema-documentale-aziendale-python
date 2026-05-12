# Sistema Documentale Aziendale in Python

Backend FastAPI per un sistema documentale interno con:

- persistenza dei metadati e del testo estratto su MongoDB;
- indicizzazione e ricerca full-text su Apache Solr;
- autenticazione base con login utente/password;
- audit log delle operazioni;
- classificazione AI del documento con fallback locale.

## Requisiti coperti

- `RF-01` upload di file `PDF`, `DOCX`, `TXT`, anche multipli
- `RF-02` estrazione del testo automatica
- `RF-03` metadati base: titolo, tipologia, autore, data upload, tag
- `RF-04` persistenza su MongoDB
- `RF-05` indicizzazione su Solr
- `RF-06` ricerca full-text con paginazione e rilevanza
- `RF-07` filtri per tipologia, autore, intervallo di date
- `RF-08` dettaglio documento + download file originale
- `RF-09` funzionalità AI: classificazione e sintesi breve
- `RF-10` autenticazione base e log su MongoDB

## Struttura del progetto

```text
app/
  routers/
  services/
dataset/
docs/
solr/
scripts/
main.py
requirements.txt
```

## Installazione

1. Creare ed attivare un ambiente Python 3.11+.
2. Installare le dipendenze:

```bash
pip install -r requirements.txt
```

3. Copiare `.env.example` in `.env` e aggiornare le variabili.
4. Avviare MongoDB.
5. Configurare Apache Solr seguendo [solr/setup_solr.md](solr/setup_solr.md).

Se si usa MongoDB Atlas o DigitalOcean Managed MongoDB, verificare anche:

- allowlist o trusted sources del proprio IP pubblico;
- raggiungibilita' outbound sulla porta `27017`;
- stringa `MONGO_URI` completa di `authSource` e `tls=true` se richiesta dal provider.

## Avvio

```bash
uvicorn app.main:app --reload
```

L'applicazione sarà disponibile su `http://127.0.0.1:8000`.

## Credenziali iniziali

Alla prima partenza, se MongoDB è raggiungibile, viene creato l'utente admin definito nel file `.env`:

- username: `admin`
- password: `Admin123!`

## Endpoint principali

- `POST /auth/login`
- `POST /documents/upload`
- `GET /documents/{document_id}`
- `GET /documents/{document_id}/download`
- `POST /documents/{document_id}/classify`
- `GET /search`
- `GET /health`

La documentazione Swagger è disponibile su `http://127.0.0.1:8000/docs`.

## Esempi di utilizzo

### Login

```bash
curl -X POST "http://127.0.0.1:8000/auth/login" ^
  -H "Content-Type: application/json" ^
  -d "{\"username\":\"admin\",\"password\":\"Admin123!\"}"
```

### Upload di due file

```bash
curl -X POST "http://127.0.0.1:8000/documents/upload" ^
  -H "Authorization: Bearer TOKEN" ^
  -F "files=@dataset/01_contratto_fornitura.txt" ^
  -F "files=@dataset/02_fattura_aprile.txt" ^
  -F "document_type=contratto" ^
  -F "author=Ufficio Acquisti" ^
  -F "tags=fornitori,2026" ^
  -F "use_ai=true"
```

### Ricerca full-text

```bash
curl "http://127.0.0.1:8000/search?q=fornitura&page=1&page_size=10&document_type=contratto" ^
  -H "Authorization: Bearer TOKEN"
```

## Dataset di prova

La cartella `dataset/` contiene 10 documenti fittizi da usare nella demo finale.

## Funzionalità AI implementata

La funzionalità AI scelta è la classificazione del documento durante l'upload o su richiesta:

- input: testo estratto del documento;
- output: categoria suggerita e breve sintesi;
- persistenza: `ai_category` e `ai_summary` nel documento MongoDB, con indicizzazione anche in Solr;
- fallback: se l'API LLM non è configurata o la risposta non è parsabile, il sistema usa regole locali basate su parole chiave.

## Documento di analisi

Il deliverable richiesto è presente in:

- [docs/documento_analisi.md](docs/documento_analisi.md)
- [docs/documento_analisi.docx](docs/documento_analisi.docx)

## Limiti noti

- non è presente OCR per PDF scansionati;
- l'autenticazione è volutamente semplice, adatta a un laboratorio;
- la UI non è inclusa: la demo può essere eseguita via Swagger UI o client HTTP.
