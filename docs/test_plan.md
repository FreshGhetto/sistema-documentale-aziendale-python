# Piano di test

## Obiettivo

Verificare in modo ripetibile il comportamento del sistema documentale su tre livelli:

1. test unitari rapidi sui componenti Python;
2. smoke test configurabile contro una API FastAPI in esecuzione;
3. verifica infrastrutturale dei servizi esterni MongoDB e Solr.

## Livello 1 - Test unitari

Comando:

```bash
py -m pytest
```

Copertura prevista:

- classificazione AI con fallback;
- validazione del parsing di `metadata_json`;
- normalizzazione tag;
- persistenza e reindicizzazione della classificazione AI.

## Livello 2 - Smoke test live

Comando:

```bash
py scripts/run_smoke_tests.py
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
6. verifica contenuto restituito

## Livello 3 - Test di integrazione via pytest

Comando:

```bash
set RUN_INTEGRATION_TESTS=1
set TEST_BASE_URL=http://127.0.0.1:8000
py -m pytest -m integration
```

I test live sono disattivati di default per evitare falsi negativi quando i servizi esterni non sono disponibili.

## Esito del collaudo corrente

Data test: 19 maggio 2026

- compilazione Python: superata
- test unitari: `11 passed, 3 skipped`
- test di integrazione live: `3 passed`
- smoke test end-to-end: superato
- MongoDB Docker locale: raggiungibile e funzionante
- Solr Docker locale: raggiungibile e funzionante
- AI fallback: funzionante
- login, upload, ricerca, dettaglio e download: funzionanti

## Ambiente usato nel collaudo

- MongoDB: `localhost:27017`
- Solr: `localhost:8983`
- API FastAPI: `http://127.0.0.1:8000`
- Swagger UI: `http://127.0.0.1:8000/docs`

Nota: eventuali variabili d'ambiente di sistema `MONGO_URI` e `MONGO_DB_NAME` possono sovrascrivere `.env`. Per usare Docker locale, devono puntare rispettivamente a `mongodb://localhost:27017` e `document_management`.

## Verifica con MongoDB online

Per eseguire la stessa verifica usando MongoDB online:

1. configurare `.env` con la stringa remota `MONGO_URI`;
2. impostare `MONGO_DB_NAME` sul database scelto;
3. aggiungere l'IP della macchina di test nella allowlist del provider;
4. avviare Solr e applicare lo schema;
5. avviare FastAPI;
6. controllare `/health`, che deve restituire `mongo: ok` e `solr: ok`;
7. eseguire `py scripts/run_smoke_tests.py`.

Il codice non distingue tra MongoDB locale e online: la scelta dipende solo dalla configurazione.
