# Documento unico di consegna - Sistema Documentale Aziendale in Python

## 1. Dati generali dell'esercitazione

Titolo: Sistema Documentale Aziendale in Python

Stack tecnologico utilizzato:

- Python 3.11+
- FastAPI
- MongoDB
- Apache Solr
- OpenAI API opzionale
- Docker per l'ambiente locale di collaudo

Deliverable inclusi nel repository:

- documento di analisi in formato Markdown e Word;
- backend Python funzionante;
- `README.md` con istruzioni di installazione e avvio;
- `requirements.txt` con dipendenze;
- guida e file schema per configurare Solr;
- dataset fittizio con almeno 10 documenti;
- presentazione demo in Markdown e Word;
- piano di test;
- checklist di consegna.

## 2. Scenario e obiettivo

Il progetto risponde al caso di una media impresa italiana che gestisce documenti aziendali distribuiti tra cartelle di rete e caselle di posta. La mancanza di un sistema centralizzato rende difficile ritrovare i documenti, controllare gli accessi e mantenere metadati coerenti.

L'obiettivo e' realizzare un backend documentale che consenta di caricare documenti aziendali, estrarne automaticamente il testo, salvare metadati e contenuto in MongoDB, indicizzare i documenti in Apache Solr, cercare documenti tramite full-text search e filtri, visualizzare e scaricare il file originale, tracciare le operazioni utente e integrare una funzionalita' AI concreta.

## 3. Attori del sistema

### Amministratore

L'amministratore accede con credenziali base e puo' usare tutti gli endpoint disponibili. Nel progetto e' previsto un utente demo creato automaticamente:

- username: `admin`
- password: `Admin123!`

### Utente autenticato

L'utente autenticato puo' caricare documenti, cercarli, visualizzarne i dettagli e scaricare il file originale. Le operazioni rilevanti vengono registrate nell'audit log.

## 4. Casi d'uso principali

### UC-01 - Login

L'utente invia username e password a `POST /auth/login`. Il sistema verifica le credenziali e restituisce un token Bearer JWT.

### UC-02 - Upload documento

L'utente autenticato invia uno o piu' file a `POST /documents/upload`, insieme ai metadati. Il sistema valida il formato, salva il file, estrae il testo, registra il documento in MongoDB e lo indicizza in Solr.

### UC-03 - Ricerca full-text

L'utente esegue una ricerca tramite `GET /search`, con paginazione e filtri per tipologia, autore e intervallo di date. Solr restituisce risultati ordinati per rilevanza, con snippet evidenziati.

### UC-04 - Dettaglio documento

L'utente richiede `GET /documents/{document_id}`. Il sistema restituisce metadati, testo estratto, informazioni AI e link per il download.

### UC-05 - Download documento

L'utente usa `GET /documents/{document_id}/download` per scaricare il file originale salvato su filesystem.

### UC-06 - Classificazione AI

La classificazione AI puo' essere eseguita durante l'upload oppure tramite `POST /documents/{document_id}/classify`.

## 5. Architettura

Il sistema e' composto da client HTTP o Swagger UI, backend FastAPI, MongoDB, Apache Solr, servizio LLM opzionale e filesystem locale per i file originali.

FastAPI coordina le operazioni applicative. MongoDB conserva documenti, utenti e audit log. Solr e' dedicato alla ricerca full-text. L'AI arricchisce il documento con categoria suggerita e sintesi breve.

## 6. Modello dati

### Collection `documents`

Campi principali: `_id`, `filename`, `stored_filename`, `title`, `document_type`, `author`, `tags`, `uploaded_at`, `uploaded_by`, `extracted_text`, `ai_category`, `ai_summary`.

### Collection `users`

Campi principali: `_id`, `username`, `password_hash`, `role`.

### Collection `audit_log`

Campi principali: `_id`, `username`, `action`, `payload`, `created_at`.

### Core Solr `documents`

Campi principali: `id`, `title_txt_it`, `document_type_s`, `author_s`, `tags_ss`, `uploaded_at_dt`, `content_txt_it`, `ai_category_s`, `ai_summary_txt_it`.

I campi testuali usano un analyzer italiano dedicato.

## 7. Proposte AI

La traccia richiede di individuare tre modi diversi di utilizzare l'AI nel sistema documentale. Questa sezione e' quindi centrale nel documento: per ogni proposta vengono indicati il punto del flusso operativo, il problema risolto, l'input e l'output del modello, il modo in cui il risultato viene mostrato o salvato e il comportamento previsto in caso di errore.

### Proposta 1 - Classificazione automatica del documento

Stato: implementata.

Punto del flusso operativo: la funzione viene usata durante l'upload del documento oppure successivamente tramite endpoint dedicato su un documento gia' salvato.

Problema risolto: la classificazione manuale puo' produrre errori, categorie incoerenti o metadati mancanti. L'AI aiuta l'utente proponendo una tipologia coerente con il contenuto del documento e una breve sintesi utile nella consultazione.

Input del modello: testo estratto dal documento, limitato a una porzione significativa per contenere costi e tempi di risposta.

Output del modello: categoria tra `contratto`, `ordine`, `fattura`, `cv`, `comunicazione`, `altro`, piu' sintesi breve.

Salvataggio e visualizzazione: il risultato viene salvato nei campi `ai_category` e `ai_summary` della collection MongoDB `documents`, viene indicizzato anche in Solr e viene restituito nelle risposte degli endpoint di upload e dettaglio documento.

Gestione errori e fallback: se la chiave API manca, il provider non risponde o la risposta non e' valida, il sistema usa un classificatore locale basato su parole chiave e punteggio. In questo modo l'upload non viene bloccato e l'utente riceve comunque un risultato utilizzabile.

### Proposta 2 - Espansione semantica della query

Stato: progettuale.

Punto del flusso operativo: la funzione si collocherebbe nella fase di ricerca, prima dell'interrogazione a Solr.

Problema risolto: gli utenti spesso cercano con parole diverse da quelle presenti nei documenti. Ad esempio, potrebbero cercare "computer ufficio" mentre nei documenti compare "materiale informatico" o "fornitura hardware". L'espansione semantica aiuterebbe a recuperare risultati pertinenti anche quando il lessico dell'utente non coincide con quello del documento.

Input del modello: query originale dell'utente, eventuali filtri selezionati e, in futuro, un piccolo dizionario di categorie aziendali.

Output del modello: query riscritta o arricchita con sinonimi e termini correlati, adatta a essere passata a Solr.

Salvataggio e visualizzazione: la query espansa potrebbe essere mostrata all'utente come suggerimento oppure salvata nell'audit log insieme alla query originale, per analizzare nel tempo come gli utenti cercano i documenti.

Gestione errori e fallback: se il modello AI non risponde o produce una riformulazione non valida, il sistema esegue la ricerca originale senza modifiche. Questo evita che un errore AI impedisca la ricerca standard.

### Proposta 3 - Riassunto contestuale

Stato: progettuale.

Punto del flusso operativo: la funzione si collocherebbe nella consultazione del dettaglio documento, quando l'utente ha gia' aperto un documento e vuole capirne rapidamente il contenuto.

Problema risolto: alcuni documenti aziendali, soprattutto contratti, comunicazioni lunghe o documenti amministrativi, richiedono tempo per essere letti. Un riassunto AI aiuterebbe l'utente a capire subito se il documento e' rilevante.

Input del modello: testo completo del documento o una porzione selezionata, eventualmente insieme alla tipologia documentale e ai metadati principali.

Output del modello: sintesi in linguaggio naturale con i punti principali del documento, eventuali scadenze, soggetti coinvolti o informazioni operative rilevanti.

Salvataggio e visualizzazione: il riassunto potrebbe essere mostrato nella vista dettaglio documento. In una versione successiva potrebbe essere salvato in cache in MongoDB per evitare chiamate ripetute al modello sullo stesso documento.

Gestione errori e fallback: se il servizio AI fallisce, il sistema continua a mostrare il testo estratto originale. L'errore potrebbe essere registrato nell'audit log senza interrompere la consultazione.

Scelta implementativa: tra le tre proposte e' stata implementata la classificazione automatica perche' e' la piu' coerente con il flusso di upload, produce metadati immediatamente utili alla ricerca e rimane realizzabile nel tempo previsto dall'esercitazione. Le altre due proposte sono documentate come sviluppi progettuali, come consentito dalla traccia.

## 8. Copertura requisiti funzionali

- RF-01 Upload documenti: implementato per PDF, DOCX e TXT, anche multipli.
- RF-02 Estrazione testo: implementata per TXT, DOCX e PDF nativi.
- RF-03 Metadati base: titolo, tipologia, autore, data upload e tag gestiti.
- RF-04 Persistenza MongoDB: metadati e testo salvati in MongoDB; file su filesystem.
- RF-05 Indicizzazione Solr: documenti indicizzati nel core `documents`.
- RF-06 Ricerca full-text: endpoint `/search` con paginazione e rilevanza.
- RF-07 Filtri ricerca: tipologia, autore e intervallo date.
- RF-08 Visualizzazione documento: dettaglio documento e link download.
- RF-09 Funzionalita' AI: classificazione automatica implementata.
- RF-10 Autenticazione e log: login JWT e audit log su MongoDB.

## 9. Ambiente di esecuzione

Per l'ambiente locale e' stato aggiunto `docker-compose.yml`. Per la verifica con MongoDB online non serve modificare il codice: occorre configurare `MONGO_URI` e `MONGO_DB_NAME` nel file `.env`.

Avvio servizi locali:

```bash
docker compose up -d
```

Avvio backend:

```bash
py -m uvicorn app.main:app --reload
```

Esempio configurazione MongoDB online:

```env
MONGO_URI=mongodb+srv://USERNAME:PASSWORD@CLUSTER_HOST/DATABASE_NAME?retryWrites=true&w=majority
MONGO_DB_NAME=document_management
```

Prima della verifica online occorre controllare la allowlist IP del provider MongoDB e la correttezza di utente, password, database e opzioni TLS/authSource richieste dal servizio.

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

## 10. Collaudo finale

Il sistema e' stato collaudato con MongoDB e Solr in Docker locale. La configurazione e' compatibile anche con MongoDB online tramite variabili d'ambiente.

Risultato health:

```json
{"app":"ok","mongo":"ok","solr":"ok"}
```

Test eseguiti:

```text
py -m pytest
11 passed, 3 skipped
```

```text
py -m pytest -m integration
3 passed
```

```text
py scripts/run_smoke_tests.py
health/login/upload/search/detail: OK
```

Lo smoke test ha verificato login, upload di un documento del dataset, classificazione AI con fallback, indicizzazione, ricerca full-text e visualizzazione del dettaglio documento.

## 11. Limiti noti

- OCR non implementato per documenti scansionati.
- Autenticazione semplice, adatta al perimetro laboratoriale.
- Non e' presente una UI frontend dedicata.
- Le funzionalita' AI progettuali 2 e 3 non sono implementate nel codice.

## 12. Sviluppi futuri

Gli sviluppi futuri non sono necessari per soddisfare la consegna dell'esercitazione, ma indicano come il prototipo potrebbe evolvere in un sistema aziendale piu' completo.

### OCR per documenti scansionati

Il sistema attuale estrae testo da PDF nativi, DOCX e TXT. In futuro potrebbe integrare un motore OCR per gestire documenti scansionati o immagini, rendendo ricercabili anche archivi storici e file firmati digitalizzati. L'OCR verrebbe attivato quando l'estrazione standard produce testo vuoto o insufficiente.

### Permessi granulari per reparto o ruolo

L'autenticazione attuale e' di base. Una versione aziendale dovrebbe prevedere ruoli come admin, amministrazione, acquisti, risorse umane e lettore. I documenti potrebbero avere campi come `department` o `allowed_roles`, usati per filtrare ricerca, dettaglio e download in base ai permessi dell'utente.

### Interfaccia web frontend

Swagger e' sufficiente per demo e test tecnico, ma un utente non tecnico avrebbe bisogno di un'interfaccia dedicata. Un frontend potrebbe offrire login, upload guidato, ricerca con filtri, vista dettaglio e download. Il frontend consumerebbe gli endpoint FastAPI gia' presenti.

### Espansione semantica della ricerca

Questa e' una delle proposte AI progettuali. Il sistema potrebbe usare un modello AI per trasformare query brevi o ambigue in ricerche piu' efficaci. Ad esempio, "computer ufficio" potrebbe essere arricchito con termini come "materiale informatico", "hardware" o "postazioni di lavoro". Se l'AI non risponde, il sistema userebbe la query originale.

### Riassunto AI on demand

Oltre alla sintesi breve generata in classificazione, si potrebbe aggiungere un riassunto dettagliato richiesto dall'utente nella vista documento. Sarebbe utile per contratti lunghi o comunicazioni articolate. Il risultato potrebbe essere mostrato a video e salvato in cache per ridurre chiamate ripetute al modello.

### Dashboard amministrativa per audit e statistiche

Poiche' il sistema registra gia' le operazioni in `audit_log`, una dashboard potrebbe mostrare documenti caricati, ricerche effettuate, categorie piu' frequenti, utenti attivi ed errori. Questo aiuterebbe l'amministratore a monitorare l'utilizzo e a migliorare la qualita' dei dati.

### Versioning documentale

In futuro si potrebbe gestire la storia delle versioni di uno stesso documento. Un contratto aggiornato, ad esempio, potrebbe mantenere collegamento con la versione precedente tramite un `document_group_id`, un numero di versione e uno stato come `attivo` o `archiviato`.

## 13. Conclusione

Il progetto copre i requisiti funzionali della traccia e fornisce un backend documentale funzionante, documentato e collaudato. La soluzione integra MongoDB per la persistenza, Solr per la ricerca full-text, FastAPI per gli endpoint e una funzionalita' AI implementata con fallback robusto.
