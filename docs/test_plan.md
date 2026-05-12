# Piano di test

## Obiettivo

Verificare in modo ripetibile il comportamento del sistema documentale su tre livelli:

1. test unitari rapidi sui componenti Python;
2. smoke test configurabile contro una API FastAPI in esecuzione;
3. verifica infrastrutturale dei servizi esterni MongoDB e Solr.

## Livello 1 - Test unitari

Comando:

```bash
pytest
```

Copertura prevista:

- classificazione AI con fallback;
- validazione del parsing di `metadata_json`.

## Livello 2 - Smoke test live

Comando:

```bash
python scripts/run_smoke_tests.py
```

Variabili configurabili:

- `TEST_BASE_URL`
- `TEST_USERNAME`
- `TEST_PASSWORD`
- `TEST_DATASET_FILE`
- `TEST_DOCUMENT_TYPE`
- `TEST_AUTHOR`
- `TEST_TAGS`

Flusso verificato:

1. `GET /health`
2. `POST /auth/login`
3. `POST /documents/upload`
4. `GET /search`
5. `GET /documents/{id}`

## Livello 3 - Test di integrazione via pytest

Comando:

```bash
set RUN_INTEGRATION_TESTS=1
pytest -m integration
```

I test live sono disattivati di default per evitare falsi negativi quando i servizi esterni non sono disponibili.

## Esito del collaudo corrente

Data test: 12 maggio 2026

- compilazione Python: superata
- test unitari: superati
- Solr: raggiungibile e funzionante
- AI fallback: funzionante
- MongoDB DigitalOcean: non raggiungibile dalla macchina di sviluppo sulla porta `27017`

## Diagnosi sul cluster MongoDB

La stringa di connessione e' stata provata direttamente via `pymongo`, ma il nodo:

`db-mongodb-fra1-08385-33daff81.mongo.ondigitalocean.com:27017`

non risponde dal client corrente.

IP pubblico rilevato durante il test:

`81.114.244.148`

Verifica da fare sul provider:

- aggiungere l'IP alla allowlist / trusted sources;
- verificare regole firewall e reachability TCP verso `27017`;
- confermare che il cluster sia attivo e accetti connessioni esterne.
