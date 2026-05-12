# Documento di analisi - Sistema Documentale Aziendale in Python

## 1. Scenario e contesto

L'azienda cliente e' una media impresa italiana con circa 150 dipendenti. La documentazione aziendale e' cresciuta nel tempo in modo non governato: contratti, ordini, fatture, curriculum, comunicazioni interne e altri file sono distribuiti tra cartelle condivise, allegati e-mail e postazioni locali. Questo genera tempi di ricerca elevati, duplicazioni, rischio di perdita di informazioni e scarsa visibilita' sugli accessi ai documenti.

L'obiettivo del progetto e' realizzare un sistema documentale interno sviluppato in Python che permetta di:

- caricare documenti in modo controllato;
- estrarre automaticamente il testo dai file supportati;
- salvare metadati e contenuto su MongoDB;
- indicizzare i contenuti in Apache Solr per la ricerca full-text;
- applicare almeno una funzionalita' AI utile e realistica;
- tracciare le principali operazioni utente.

La soluzione scelta e' un backend REST realizzato con FastAPI. Il backend dialoga con MongoDB per la persistenza, con Solr per la ricerca e con un modello LLM esterno per la funzionalita' AI selezionata.

## 2. Attori del sistema

### 2.1 Admin

L'amministratore gestisce il sistema in fase iniziale e durante l'esercizio di laboratorio. I suoi permessi sono:

- accesso completo agli endpoint;
- caricamento e consultazione di tutti i documenti;
- esecuzione della classificazione AI;
- verifica dei log e supporto alla demo finale.

### 2.2 Utente aziendale

L'utente aziendale rappresenta un dipendente autorizzato a usare il sistema documentale per esigenze operative. I suoi permessi sono:

- login con username e password;
- caricamento di nuovi documenti;
- ricerca full-text con filtri;
- visualizzazione dei documenti e download del file originale.

Per questa esercitazione non sono stati introdotti ruoli avanzati o ACL granulari per singolo documento, per mantenere il sistema entro il perimetro realizzabile nelle 8 ore.

## 3. Casi d'uso principali

### UC-01 - Login al sistema

L'utente apre l'applicazione, inserisce username e password e richiede l'accesso. Il sistema verifica le credenziali su MongoDB, genera un token Bearer e lo restituisce al client. Se le credenziali sono errate, l'accesso viene negato.

### UC-02 - Caricamento di un documento

L'utente autenticato invia uno o piu' file nei formati PDF, DOCX o TXT insieme ai metadati richiesti: titolo, tipologia, autore e tag. Il sistema salva il file su filesystem, estrae il testo, memorizza i dati in MongoDB e indicizza il documento in Solr. Se richiesto, avvia anche la classificazione AI.

### UC-03 - Ricerca full-text con filtri

L'utente inserisce una query testuale e puo' restringere i risultati per tipologia, autore e intervallo di date. Il sistema interroga Solr, restituisce i risultati ordinati per rilevanza e mostra eventuali snippet evidenziati. L'operazione viene registrata nell'audit log.

### UC-04 - Consultazione e download del documento

Partendo dall'ID di un documento o da un risultato di ricerca, l'utente richiede il dettaglio completo. Il sistema recupera metadati e testo estratto da MongoDB e genera il link di download del file originale salvato su filesystem.

### UC-05 - Classificazione AI del documento

L'utente puo' attivare la classificazione AI durante l'upload oppure richiederla su un documento gia' caricato. Il sistema invia all'LLM il testo estratto, riceve categoria e sintesi breve, salva i risultati nei metadati e li rende disponibili anche in ricerca.

## 4. Architettura della soluzione

L'architettura e' composta da quattro elementi principali:

1. Backend Python FastAPI
2. MongoDB
3. Apache Solr
4. Servizio LLM esterno via API

### 4.1 Backend FastAPI

FastAPI e' stato scelto perche' permette di costruire rapidamente API tipizzate, con validazione automatica dei dati e documentazione Swagger integrata. Per una demo di laboratorio e' un vantaggio concreto: gli endpoint sono testabili immediatamente dal browser senza dover costruire una UI dedicata.

### 4.2 MongoDB

MongoDB memorizza i documenti in tre collection principali:

- `documents`
- `users`
- `audit_log`

La scelta e' coerente con un dominio documentale in cui i metadati possono evolvere nel tempo e alcuni campi opzionali, come quelli AI, possono essere aggiunti senza migrazioni rigide.

### 4.3 Apache Solr

Solr viene usato esclusivamente come motore di ricerca. Ogni documento caricato viene indicizzato in un core dedicato chiamato `documents`. La ricerca viene eseguita tramite query full-text, ranking per rilevanza, paginazione e filtri strutturati.

### 4.4 Servizio LLM esterno

Per la funzionalita' AI e' previsto l'uso di un modello GPT via API. In ambiente reale la chiamata avviene con SDK ufficiale. Nel progetto e' presente anche un fallback locale per evitare che il flusso si blocchi in caso di assenza della chiave API, timeout o risposta non parsabile.

### 4.5 Motivazione delle scelte

- Python: linguaggio rapido da sviluppare e adatto all'integrazione di librerie backend e AI.
- FastAPI: riduce il tempo di sviluppo, semplifica la validazione e offre una demo immediata.
- MongoDB: adatto a documenti con struttura flessibile.
- Solr: motore solido per ricerca testuale e filtri.
- LLM esterno: consente di aggiungere un supporto intelligente concreto senza sviluppare modelli custom.

### 4.6 Immagine da inserire nel documento

Inserire subito dopo questa sezione un diagramma architetturale semplice, con quattro blocchi:

- client / Swagger UI
- backend FastAPI
- MongoDB
- Apache Solr
- servizio LLM esterno

Collegamenti da mostrare:

- il client invia richieste HTTP al backend;
- il backend salva metadati e testo su MongoDB;
- il backend indicizza e cerca in Solr;
- il backend invia il testo al modello LLM per la classificazione AI.

Didascalia consigliata:

`Figura 1 - Architettura logica del sistema documentale`

## 5. Modello dati

### 5.1 Collection MongoDB `documents`

Campi principali:

- `_id`: identificativo univoco del documento
- `filename`: nome file originale
- `stored_filename`: nome file sul filesystem
- `title`: titolo del documento
- `document_type`: tipologia del documento
- `author`: autore o ufficio di riferimento
- `tags`: lista di tag liberi
- `uploaded_at`: data e ora di caricamento
- `uploaded_by`: utente che ha effettuato l'upload
- `extracted_text`: testo estratto dal contenuto
- `ai_category`: categoria suggerita dall'AI
- `ai_summary`: sintesi breve del documento

### 5.2 Collection MongoDB `users`

Campi principali:

- `_id`
- `username`
- `password_hash`
- `role`

### 5.3 Collection MongoDB `audit_log`

Campi principali:

- `_id`
- `username`
- `action`
- `payload`
- `created_at`

### 5.4 Core Solr `documents`

Campi principali:

- `id`
- `title_txt_it`
- `document_type_s`
- `author_s`
- `tags_ss`
- `uploaded_at_dt`
- `content_txt_it`
- `ai_category_s`
- `ai_summary_txt_it`

I campi testuali principali usano un analyzer per la lingua italiana, con lowercase, stopwords italiane e stemming leggero.

### 5.5 Immagine da inserire nel documento

Inserire dopo questa sezione una tabella o screenshot dello schema dati con:

- collection MongoDB `documents`
- collection `users`
- collection `audit_log`
- campi del core Solr `documents`

Didascalia consigliata:

`Figura 2 - Modello dati MongoDB e campi indicizzati su Solr`

## 6. Tre proposte di utilizzo dell'AI

Questa e' la parte centrale del documento. Sono state definite tre proposte diverse. Una sola viene implementata nel software, mentre le altre due restano progettuali ma realistiche.

### Proposta AI 1 - Classificazione automatica del documento (implementata)

#### Punto del flusso

Durante il caricamento del documento oppure su richiesta successiva dell'utente.

#### Problema risolto

Gli utenti possono sbagliare la tipologia del documento o non valorizzarla in modo uniforme. La classificazione AI propone una categoria coerente, riducendo errori e migliorando la qualita' della ricerca filtrata.

#### Input e output

- input: testo estratto dal documento
- output: categoria tra `contratto`, `ordine`, `fattura`, `cv`, `comunicazione`, `altro` e breve sintesi

#### Salvataggio o visualizzazione

L'output viene salvato nei campi `ai_category` e `ai_summary` del documento in MongoDB e viene indicizzato in Solr, cosi' da essere disponibile nelle ricerche successive.

#### Gestione errori e fallback

Se l'API LLM non e' configurata, va in timeout o restituisce JSON non valido, il sistema non blocca l'upload. Applica invece un fallback locale basato su parole chiave e assegna una categoria minima. In questo modo la robustezza del sistema resta accettabile anche in demo.

### Proposta AI 2 - Riscrittura della query utente in linguaggio documentale

#### Punto del flusso

Fase di ricerca.

#### Problema risolto

Spesso gli utenti formulano query troppo generiche o colloquiali. Un LLM potrebbe trasformare la domanda dell'utente in una query piu' adatta a Solr, arricchita con sinonimi, varianti lessicali e termini tipici del dominio aziendale.

#### Input e output

- input: query originale dell'utente e set minimo di metadati disponibili
- output: query espansa per Solr e spiegazione sintetica della trasformazione

#### Salvataggio o visualizzazione

La query riformulata puo' essere mostrata nel client come suggerimento e loggata nell'audit per fini diagnostici.

#### Gestione errori e fallback

Se l'AI non risponde, il sistema esegue la query originale senza bloccare la ricerca. Questa caratteristica la rende adatta a un secondo step evolutivo, ma non prioritaria nella prima versione.

### Proposta AI 3 - Riassunto contestuale del documento in consultazione

#### Punto del flusso

Durante la visualizzazione del documento.

#### Problema risolto

Documenti lunghi come contratti o comunicazioni estese richiedono tempo per essere compresi. Un riassunto contestuale permette all'utente di capire in pochi secondi se il documento e' quello giusto.

#### Input e output

- input: testo completo del documento o estratti significativi
- output: riassunto di 5-6 righe con punti chiave

#### Salvataggio o visualizzazione

Il riassunto puo' essere generato on demand e mostrato nella scheda documento. Eventualmente si puo' cacheare nel campo `ai_summary`.

#### Gestione errori e fallback

In caso di errore si mostra il testo estratto senza riassunto. Il flusso di consultazione resta operativo.

### 6.4 Scelta della funzionalita' da implementare

La proposta selezionata per l'implementazione e' la classificazione automatica del documento. E' la piu' semplice da realizzare nel tempo disponibile, produce un beneficio immediato sui metadati ed e' coerente con un flusso di caricamento gia' previsto dai requisiti.

### 6.5 Immagine da inserire nel documento

Inserire qui uno schema del flusso AI implementato:

1. upload file
2. estrazione testo
3. invio del testo all'LLM oppure fallback locale
4. ritorno di `categoria` e `sintesi`
5. salvataggio in MongoDB e indicizzazione in Solr

Didascalia consigliata:

`Figura 3 - Flusso della classificazione AI del documento`

## 7. Requisiti funzionali e copertura

Il sistema progettato copre tutti i 10 requisiti indicati dall'esercitazione:

- upload multiplo di PDF, DOCX, TXT;
- estrazione del testo;
- metadati base;
- salvataggio su MongoDB;
- indicizzazione in Solr;
- ricerca full-text;
- filtri di ricerca;
- visualizzazione e download;
- AI opzionale ma implementata;
- autenticazione base e log.

## 8. Gestione errori

La robustezza e' parte della valutazione, quindi il sistema prevede:

- errore 400 per formati non supportati o metadati mancanti;
- errore 401 per autenticazione non valida;
- errore 404 per documento inesistente;
- errore 503 per Solr non raggiungibile;
- fallback AI locale in caso di problema con il modello esterno.

Queste scelte evitano il blocco totale del flusso e rendono la demo piu' affidabile.

### 8.1 Immagine da inserire nel documento

Inserire uno screenshot della risposta JSON di `/health` oppure di un errore `503` gestito dal backend, per dimostrare la robustezza applicativa.

Didascalia consigliata:

`Figura 4 - Esempio di gestione controllata degli errori`

## 9. Limiti noti

- assenza di OCR: i PDF scansionati senza testo non sono gestiti;
- controllo accessi semplificato, senza permessi per reparto o documento;
- assenza di interfaccia frontend dedicata;
- dataset di prova limitato e fittizio;
- classificazione AI basata su poche categorie definite a priori.

## 10. Sviluppi futuri

Gli sviluppi successivi piu' utili sarebbero:

- interfaccia web per utenti non tecnici;
- supporto OCR per scansioni;
- gestione dei permessi per reparto, ufficio o proprietario del documento;
- versioning del documento;
- query expansion AI;
- riassunto on demand in consultazione;
- dashboard amministrativa per i log e gli indicatori di utilizzo.

## 11. Conclusioni

La soluzione proposta risponde al problema aziendale con un'architettura semplice ma credibile, costruita con componenti coerenti con il dominio del document management. L'uso combinato di MongoDB e Solr separa in modo pulito persistenza e ricerca, mentre l'introduzione di una funzionalita' AI concreta migliora la qualita' dei metadati senza complicare eccessivamente il progetto. Per un'esercitazione di 8 ore, questa impostazione massimizza il rapporto tra completezza, robustezza e realizzabilita'.
