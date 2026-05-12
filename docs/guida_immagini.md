# Guida immagini per documento e presentazione

## Obiettivo

Questa guida indica esattamente quali immagini inserire, dove inserirle e cosa devono mostrare, per rendere il materiale finale piu' professionale e scorrevole.

## Documento di analisi

### Figura 1 - Architettura logica

Posizione:

- dopo il capitolo `4. Architettura della soluzione`

Contenuto:

- blocco `Client / Swagger UI`
- blocco `FastAPI Backend`
- blocco `MongoDB`
- blocco `Apache Solr`
- blocco `Servizio LLM`
- frecce tra i blocchi

Formato consigliato:

- diagramma orizzontale pulito
- sfondo bianco
- colori sobri: blu/grigio

### Figura 2 - Modello dati

Posizione:

- dopo il capitolo `5. Modello dati`

Contenuto:

- tabella collection `documents`, `users`, `audit_log`
- tabella campi Solr

Formato consigliato:

- tabella o diagramma a colonne

### Figura 3 - Flusso AI

Posizione:

- dopo il capitolo `6. Tre proposte di utilizzo dell'AI`

Contenuto:

- upload
- estrazione testo
- classificazione AI
- fallback locale
- salvataggio e indicizzazione

Formato consigliato:

- flowchart verticale o orizzontale

### Figura 4 - Gestione errori / health

Posizione:

- dopo il capitolo `8. Gestione errori`

Contenuto:

- screenshot Swagger o terminale con risposta `/health`
- oppure risposta `503` MongoDB non raggiungibile

Formato consigliato:

- screenshot ritagliato, leggibile, non troppo grande

## Presentazione finale

### Slide 2 - Problema aziendale

Immagine da inserire:

- cartella documenti disordinata oppure schema con file dispersi tra cartelle, email e desktop

Obiettivo:

- far vedere subito il problema iniziale

### Slide 4 - Architettura

Immagine da inserire:

- lo stesso diagramma architetturale del documento, semplificato

Obiettivo:

- spiegare l'architettura in 20 secondi

### Slide 5 - Modello dati

Immagine da inserire:

- tabella ridotta con `documents`, `users`, `audit_log`

Obiettivo:

- mostrare che il dato e' strutturato

### Slide 6 - Funzionalita' AI

Immagine da inserire:

- mini flusso AI oppure screenshot JSON con `category` e `summary`

Obiettivo:

- rendere concreta la funzione AI

### Slide 7 - Demo operativa

Immagini da inserire:

- screenshot login
- screenshot upload
- screenshot ricerca
- screenshot dettaglio documento

Obiettivo:

- accompagnare la demo anche se l'ambiente fosse lento

### Slide 8 - Qualita' e test

Immagine da inserire:

- output dei test `pytest`
- output dello smoke test

Obiettivo:

- dare credibilita' tecnica al progetto

### Slide 9 - Stato del collaudo

Immagine da inserire:

- screenshot `/health`
- eventualmente test di rete fallito verso MongoDB

Obiettivo:

- spiegare che il blocco finale e' infrastrutturale, non di codice

## Come produrre velocemente le immagini

- per i diagrammi: PowerPoint, Draw.io o Canva
- per gli screenshot: Swagger UI, terminale PowerShell, browser
- per le tabelle: copiare una tabella pulita da Word o PowerPoint

## Regola pratica

Ogni immagine deve rispondere a una sola domanda:

- come e' fatto il sistema?
- come sono salvati i dati?
- come funziona l'AI?
- cosa succede in demo?
- come dimostriamo la qualita'?
