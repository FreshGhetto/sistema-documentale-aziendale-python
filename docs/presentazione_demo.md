# Presentazione finale - traccia da 10 minuti

## Slide 1 - Titolo

Sistema Documentale Aziendale in Python  
Python, MongoDB, Apache Solr, AI

Messaggio da dire:

"Abbiamo realizzato un backend documentale per una media impresa, con upload controllato, ricerca full-text, gestione metadati, autenticazione e una funzionalita' AI di classificazione."

Immagine da inserire:

- logo del progetto oppure sfondo sobrio con icone documento, database e ricerca

## Slide 2 - Problema aziendale

- documenti distribuiti tra cartelle e mail
- tempi lunghi di ricerca
- duplicazioni
- nessuna tracciabilita' degli accessi

Messaggio da dire:

"Il problema di partenza era la dispersione documentale. L'obiettivo era costruire un sistema semplice ma credibile, adatto a un contesto aziendale reale."

Immagine da inserire:

- schema con file dispersi tra cartelle di rete, email e desktop

## Slide 3 - Obiettivi del progetto

- upload di PDF, DOCX, TXT
- estrazione automatica del testo
- persistenza su MongoDB
- indicizzazione su Solr
- ricerca con filtri
- AI su almeno un caso concreto

Immagine da inserire:

- elenco visuale con icone per upload, database, ricerca e AI

## Slide 4 - Architettura

- FastAPI come backend REST
- MongoDB per utenti, documenti e audit log
- Solr per ricerca full-text
- OpenAI API opzionale con fallback locale

Messaggio da dire:

"Abbiamo separato la persistenza dalla ricerca: MongoDB conserva il dato, Solr ottimizza la consultazione."

Immagine da inserire:

- diagramma architetturale semplificato del sistema

## Slide 5 - Modello dati

Collection:

- `documents`
- `users`
- `audit_log`

Campi rilevanti:

- titolo, tipologia, autore, tag
- testo estratto
- utente di caricamento
- categoria e sintesi AI

Immagine da inserire:

- tabella sintetica delle collection MongoDB e dei campi Solr

## Slide 6 - Funzionalita' AI scelta

Classificazione automatica del documento.

- input: testo estratto
- output: categoria + sintesi breve
- fallback: regole locali se il modello non risponde

Messaggio da dire:

"Abbiamo scelto la proposta AI piu' utile e implementabile nel tempo a disposizione: migliora i metadati e non blocca il flusso in caso di errore."

Immagine da inserire:

- flowchart della classificazione AI oppure screenshot JSON con `category` e `summary`

## Slide 7 - Demo operativa

Sequenza da mostrare:

1. login
2. upload di un documento del dataset
3. classificazione AI
4. ricerca full-text
5. apertura del dettaglio documento

Immagini da inserire:

- screenshot login Swagger
- screenshot upload riuscito
- screenshot ricerca con snippet
- screenshot dettaglio documento

## Slide 8 - Qualita' e test

- validazione input lato API
- gestione errori MongoDB e Solr
- rollback se indicizzazione fallisce
- suite di test unitaria
- test di integrazione live
- smoke test end-to-end

Immagine da inserire:

- screenshot output `py -m pytest`

## Slide 9 - Stato del collaudo

- ambiente Docker locale verificato
- `/health`: `mongo: ok`, `solr: ok`
- login admin funzionante
- upload documento funzionante
- ricerca full-text con snippet e score funzionante
- dettaglio e download documento funzionanti
- AI fallback testata e funzionante

Messaggio da dire:

"Il sistema e' stato collaudato end-to-end con MongoDB e Solr in Docker. La demo mostra il flusso completo richiesto dalla traccia."

Immagine da inserire:

- screenshot `/health` con `mongo:ok` e `solr:ok`
- screenshot smoke test riuscito

## Slide 10 - Conclusioni e sviluppi futuri

- OCR per scansioni: permette di indicizzare PDF scansionati e archivi storici non testuali
- permessi granulari per reparto: limita l'accesso a CV, fatture o contratti in base al ruolo
- UI frontend: rende il sistema usabile da utenti non tecnici senza Swagger
- espansione AI sulla ricerca: migliora query brevi o ambigue con sinonimi e termini correlati
- riassunto contestuale in consultazione: aiuta a leggere rapidamente documenti lunghi
- dashboard audit: mostra caricamenti, ricerche, errori e utilizzo del sistema

Immagine da inserire:

- roadmap semplice in tre colonne: attuale, prossimo passo, sviluppi futuri

## Chiusura consigliata

"Il progetto copre i requisiti richiesti e mostra una struttura realistica: backend modulare, persistenza, ricerca specializzata, audit e una funzione AI concreta con fallback robusto."
