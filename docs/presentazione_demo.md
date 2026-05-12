# Presentazione finale - traccia da 10 minuti

## Slide 1 - Titolo

Sistema Documentale Aziendale in Python  
Python, MongoDB, Apache Solr, AI

Messaggio da dire:

"Abbiamo realizzato un backend documentale per una media impresa, con upload controllato, ricerca full-text, gestione metadati, autenticazione e una funzionalita' AI di classificazione."

## Slide 2 - Problema aziendale

- documenti distribuiti tra cartelle e mail
- tempi lunghi di ricerca
- duplicazioni
- nessuna tracciabilita' degli accessi

Messaggio da dire:

"Il problema di partenza era la dispersione documentale. L'obiettivo era costruire un sistema semplice ma credibile, adatto a un contesto aziendale reale."

## Slide 3 - Obiettivi del progetto

- upload di PDF, DOCX, TXT
- estrazione automatica del testo
- persistenza su MongoDB
- indicizzazione su Solr
- ricerca con filtri
- AI su almeno un caso concreto

## Slide 4 - Architettura

- FastAPI come backend REST
- MongoDB per utenti, documenti e audit log
- Solr per ricerca full-text
- OpenAI API opzionale con fallback locale

Messaggio da dire:

"Abbiamo separato la persistenza dalla ricerca: MongoDB conserva il dato, Solr ottimizza la consultazione."

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

## Slide 6 - Funzionalita' AI scelta

Classificazione automatica del documento.

- input: testo estratto
- output: categoria + sintesi breve
- fallback: regole locali se il modello non risponde

Messaggio da dire:

"Abbiamo scelto la proposta AI piu' utile e implementabile nel tempo a disposizione: migliora i metadati e non blocca il flusso in caso di errore."

## Slide 7 - Demo operativa

Sequenza da mostrare:

1. login
2. upload di un documento del dataset
3. classificazione AI
4. ricerca full-text
5. apertura del dettaglio documento

## Slide 8 - Qualita' e test

- validazione input lato API
- gestione errori MongoDB e Solr
- rollback se indicizzazione fallisce
- suite di test unitaria e smoke test configurabile

## Slide 9 - Stato del collaudo

- applicazione avviabile
- Solr testato
- AI fallback testata
- MongoDB remoto bloccato da allowlist/firewall del provider

Messaggio da dire:

"Il codice e' pronto anche per il cluster remoto, ma l'ultimo vincolo emerso e' infrastrutturale, non applicativo."

## Slide 10 - Conclusioni e sviluppi futuri

- OCR per scansioni
- permessi granulari per reparto
- UI frontend
- espansione AI sulla ricerca
- riassunto contestuale in consultazione

## Chiusura consigliata

"Il progetto copre i requisiti richiesti e mostra una struttura realistica: backend modulare, persistenza, ricerca specializzata, audit e una funzione AI concreta con fallback robusto."
