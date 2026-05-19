# Documento di analisi - Sistema Documentale Aziendale in Python

## 1. Introduzione, scenario e contesto applicativo

Il presente documento descrive l'analisi e le scelte progettuali relative allo sviluppo di un sistema documentale aziendale realizzato in Python, conforme alla traccia laboratoriale proposta. Il contesto di riferimento e' quello di una media impresa italiana caratterizzata da una gestione eterogenea e distribuita dei documenti interni, con conseguenti difficolta' nella reperibilita' delle informazioni, duplicazione dei contenuti, assenza di tracciabilita' delle operazioni e limitato controllo sugli accessi.

L'obiettivo del progetto e' la definizione di un backend applicativo in grado di:

- acquisire documenti nei formati `PDF`, `DOCX` e `TXT`;
- estrarre automaticamente il contenuto testuale dai file caricati;
- memorizzare metadati e testo estratto in MongoDB;
- indicizzare i contenuti in Apache Solr per supportare la ricerca full-text;
- esporre API HTTP per autenticazione, upload, ricerca, consultazione e download;
- integrare almeno una funzionalita' basata su intelligenza artificiale;
- registrare le principali operazioni utente a fini di audit.

La soluzione implementata adotta FastAPI come framework per il backend REST, MongoDB come database documentale, Apache Solr come motore di ricerca e un servizio LLM esterno, opzionale, per la classificazione automatica dei documenti.

## 2. Attori del sistema

### 2.1 Amministratore

L'amministratore rappresenta il soggetto incaricato della configurazione iniziale del sistema e del supporto operativo durante le fasi di collaudo e dimostrazione. Nell'implementazione corrente, tale ruolo coincide con l'utente predefinito creato in fase di startup, qualora MongoDB sia raggiungibile. Le sue responsabilita' sono:

- autenticarsi al sistema tramite username e password;
- caricare e consultare documenti;
- avviare la classificazione AI durante l'upload o su documenti gia' presenti;
- verificare il comportamento generale del sistema;
- disporre di un accesso completo agli endpoint disponibili.

### 2.2 Utente aziendale autenticato

L'utente aziendale autenticato utilizza il sistema per finalita' operative ordinarie. In particolare, puo':

- effettuare il login;
- caricare uno o piu' documenti;
- associare metadati descrittivi ai file;
- eseguire ricerche full-text e filtri;
- visualizzare il dettaglio di un documento;
- scaricare il file originale.

Per ragioni di perimetro progettuale e di tempo, non sono stati implementati profili autorizzativi granulari per reparto, documento o singolo insieme di permessi. L'autenticazione e' quindi di base, ma sufficiente a soddisfare la richiesta dell'esercitazione.

## 3. Casi d'uso principali

### UC-01 - Autenticazione dell'utente

L'utente invia le proprie credenziali all'endpoint `POST /auth/login`. Il sistema verifica la corrispondenza tra username e password hashata memorizzata nella collection `users`. In caso di esito positivo, viene generato e restituito un token Bearer JWT da utilizzare nelle successive richieste protette. In caso contrario, viene restituito un errore di autenticazione.

### UC-02 - Caricamento e acquisizione del documento

L'utente autenticato invoca l'endpoint `POST /documents/upload`, allegando uno o piu' file e i metadati associati. Il backend valida il formato, salva il file su filesystem, estrae il testo e costruisce il record documentale. Se richiesto, viene eseguita anche la classificazione AI. Il documento viene quindi salvato in MongoDB e indicizzato in Solr.

### UC-03 - Ricerca full-text con filtri

Attraverso l'endpoint `GET /search`, l'utente inserisce una query testuale e puo' opzionalmente restringere i risultati per tipologia documentale, autore e intervallo temporale. Solr elabora la richiesta, ordina i risultati per rilevanza, restituisce eventuali snippet evidenziati e consente la paginazione.

### UC-04 - Consultazione del dettaglio documento

L'utente richiede il contenuto di un documento specifico tramite `GET /documents/{document_id}`. Il sistema recupera da MongoDB i metadati e il testo estratto e restituisce anche l'URL logico per il download del file originale.

### UC-05 - Download del file originale

L'utente puo' scaricare il file sorgente associato al documento tramite `GET /documents/{document_id}/download`. Il backend verifica l'identita' dell'utente, recupera il percorso del file dal record salvato e restituisce il contenuto come `FileResponse`.

### UC-06 - Classificazione AI di un documento esistente

L'utente puo' richiamare `POST /documents/{document_id}/classify` per ottenere una categorizzazione automatica e una breve sintesi del contenuto. L'operazione viene registrata nell'audit log e puo' essere eseguita anche successivamente all'upload.

## 4. Architettura del sistema

L'architettura proposta si basa su una separazione funzionale tra livello applicativo, persistenza documentale, indicizzazione semantica e servizio AI.

I componenti principali sono:

1. client HTTP / Swagger UI;
2. backend REST FastAPI;
3. MongoDB;
4. Apache Solr;
5. servizio LLM esterno.

### 4.1 Backend FastAPI

Il backend costituisce il nucleo applicativo del sistema. Esso espone gli endpoint necessari al soddisfacimento dei requisiti funzionali e organizza la logica in moduli distinti:

- `app/routers/` per gli endpoint HTTP;
- `app/services/` per la logica applicativa;
- `app/database.py` per l'accesso a MongoDB;
- `app/security.py` per hashing password e token JWT;
- `app/config.py` per la configurazione tramite variabili d'ambiente.

FastAPI e' stato selezionato per la sua capacita' di fornire validazione automatica dei payload, tipizzazione nativa, documentazione Swagger integrata e un modello di sviluppo adatto a un backend di laboratorio ma strutturato.

### 4.2 MongoDB

MongoDB e' impiegato come database documentale per la memorizzazione di:

- documenti e relativi metadati;
- utenti autenticabili;
- log di audit.

La scelta e' coerente con la natura semi-strutturata del dominio, che prevede campi obbligatori, facoltativi e arricchimenti successivi, come quelli generati dall'AI.

### 4.3 Apache Solr

Solr e' utilizzato come motore dedicato alla ricerca. Il sistema non delega a MongoDB la full-text search principale, ma adotta un indice separato e ottimizzato. Ogni documento, una volta acquisito, viene trasformato in un record indicizzabile contenente campi descrittivi, contenuto testuale e arricchimenti AI. La ricerca impiega query `edismax`, filtri strutturati, paginazione e highlighting.

### 4.4 Servizio LLM esterno

La funzionalita' AI implementata si basa su un modello GPT accessibile via API. Il backend invia al modello un estratto del contenuto del documento e riceve in risposta una categoria documentale e una sintesi breve. In assenza di API key o in caso di risposta non parsabile, il sistema adotta un fallback locale basato su regole e parole chiave.

### 4.5 Considerazioni architetturali

Dal punto di vista progettuale, l'architettura realizza una chiara separazione dei ruoli:

- FastAPI governa il flusso applicativo;
- MongoDB garantisce persistenza e auditabilita';
- Solr ottimizza la fase di reperimento delle informazioni;
- il servizio LLM aggiunge una componente di supporto semantico.

Tale separazione migliora la manutenibilita' del progetto e consente di isolare le responsabilita' tecniche.

### 4.6 Immagine da inserire nel documento

Inserire subito dopo questa sezione un diagramma architetturale semplice, con i seguenti blocchi:

- client / Swagger UI;
- backend FastAPI;
- MongoDB;
- Apache Solr;
- servizio LLM esterno.

Collegamenti da rappresentare:

- il client invia richieste HTTP al backend;
- il backend salva metadati e testo in MongoDB;
- il backend indicizza e interroga Solr;
- il backend invia il testo al modello LLM per la classificazione.

Didascalia consigliata:

`Figura 1 - Architettura logica del sistema documentale`

## 5. Modello dati

### 5.1 Collection MongoDB `documents`

La collection `documents` rappresenta il fulcro informativo del sistema. I campi principali sono:

- `_id`: identificativo univoco del documento;
- `filename`: nome originale del file caricato;
- `stored_filename`: nome del file memorizzato su filesystem;
- `title`: titolo del documento;
- `document_type`: tipologia documentale;
- `author`: autore o ufficio di riferimento;
- `tags`: lista di tag liberi;
- `uploaded_at`: timestamp del caricamento;
- `uploaded_by`: username dell'utente che ha eseguito l'upload;
- `extracted_text`: testo estratto dal file;
- `ai_category`: categoria suggerita dalla classificazione AI;
- `ai_summary`: sintesi breve del documento.

### 5.2 Collection MongoDB `users`

La collection `users` contiene i dati necessari all'autenticazione:

- `_id`;
- `username`;
- `password_hash`;
- `role`.

### 5.3 Collection MongoDB `audit_log`

La collection `audit_log` memorizza la tracciatura delle operazioni rilevanti:

- `_id`;
- `username`;
- `action`;
- `payload`;
- `created_at`.

Le azioni registrate includono, ad esempio, upload, consultazione, download, classificazione e ricerca.

### 5.4 Core Solr `documents`

Il core Solr `documents` contiene i campi necessari alla ricerca full-text e al filtering:

- `id`;
- `title_txt_it`;
- `document_type_s`;
- `author_s`;
- `tags_ss`;
- `uploaded_at_dt`;
- `content_txt_it`;
- `ai_category_s`;
- `ai_summary_txt_it`.

I campi testuali principali fanno riferimento a un field type dedicato alla lingua italiana, con tokenizzazione standard, normalizzazione in lowercase, stopwords italiane e stemming leggero.

### 5.5 Immagine da inserire nel documento

Inserire dopo questa sezione una tabella o uno schema sintetico che rappresenti:

- le tre collection MongoDB (`documents`, `users`, `audit_log`);
- i campi principali del core Solr `documents`.

Didascalia consigliata:

`Figura 2 - Modello dati MongoDB e campi indicizzati in Solr`

## 6. Proposte di utilizzo dell'intelligenza artificiale

La traccia richiede l'individuazione di tre possibili modalita' di impiego dell'AI all'interno del sistema documentale. Nel presente progetto sono state elaborate tre proposte, di cui una effettivamente implementata e due mantenute a livello progettuale.

Questa e' una delle parti centrali dell'analisi, perche' non si limita a dichiarare genericamente l'uso di un modello linguistico, ma descrive tre applicazioni concrete nel flusso operativo del sistema: una sul caricamento, una sulla ricerca e una sulla consultazione.

### 6.1 Proposta 1 - Classificazione automatica del documento (implementata)

#### Punto del flusso operativo

La classificazione puo' essere attivata durante l'upload oppure successivamente su un documento gia' memorizzato.

#### Problema affrontato

La categorizzazione manuale dei documenti e' soggetta a errori, inconsistenze terminologiche e omissioni. Un supporto automatico consente di ridurre l'eterogeneita' dei metadati e di migliorare la qualita' delle ricerche filtrate.

#### Input e output

- input: testo estratto dal documento;
- output: categoria tra `contratto`, `ordine`, `fattura`, `cv`, `comunicazione`, `altro`, accompagnata da una sintesi breve.

#### Salvataggio o visualizzazione

L'output viene restituito all'utente e puo' essere memorizzato nei campi `ai_category` e `ai_summary`. Questi valori sono inoltre indicizzati in Solr.

#### Gestione degli errori e fallback

In assenza della chiave API, in caso di timeout o in presenza di una risposta non conforme al formato previsto, il sistema utilizza un fallback locale basato su parole chiave. In tal modo, la procedura resta deterministica e il flusso applicativo non si interrompe.

### 6.2 Proposta 2 - Espansione semantica della query di ricerca

#### Punto del flusso operativo

La funzionalita' si collocherebbe nella fase di ricerca full-text.

#### Problema affrontato

Le query formulate dagli utenti possono risultare vaghe, incomplete o lessicalmente distanti dai termini effettivamente presenti nei documenti. Un modello linguistico potrebbe generare una query piu' ricca e coerente con il dominio documentale aziendale.

#### Input e output

- input: query originale dell'utente;
- output: query espansa, elenco di sinonimi o riformulazione adatta a Solr.

#### Salvataggio o visualizzazione

La query riformulata potrebbe essere mostrata nel client oppure tracciata nell'audit log per finalita' di analisi.

#### Gestione degli errori e fallback

Se l'AI non restituisce una risposta valida, il sistema eseguirebbe la query originale senza alterare il comportamento di base.

### 6.3 Proposta 3 - Riassunto contestuale del documento

#### Punto del flusso operativo

La funzionalita' si applicherebbe durante la consultazione del dettaglio documento.

#### Problema affrontato

Documenti estesi, quali contratti o comunicazioni articolate, richiedono una lettura completa per comprenderne il contenuto essenziale. Un riassunto contestuale permetterebbe all'utente di valutare piu' rapidamente la rilevanza del documento.

#### Input e output

- input: testo completo o parzialmente selezionato del documento;
- output: sintesi testuale breve, orientata ai punti principali.

#### Salvataggio o visualizzazione

Il risultato potrebbe essere mostrato on demand nella vista di dettaglio e, in una successiva evoluzione, memorizzato in cache.

#### Gestione degli errori e fallback

In caso di fallimento del servizio AI, il sistema continuerebbe a mostrare il testo estratto originale.

### 6.4 Motivazione della scelta implementativa

Tra le tre proposte, la classificazione automatica e' stata selezionata perche' rappresenta il miglior compromesso tra utilita' pratica, coerenza con il processo di caricamento e fattibilita' nel tempo disponibile. Essa produce infatti un arricchimento immediato dei metadati e si integra naturalmente con le funzioni di ricerca e consultazione.

### 6.5 Immagine da inserire nel documento

Inserire in questa posizione un flowchart del processo AI:

1. upload del file;
2. estrazione del testo;
3. chiamata al modello LLM oppure attivazione del fallback locale;
4. produzione di categoria e sintesi;
5. salvataggio in MongoDB e indicizzazione in Solr.

Didascalia consigliata:

`Figura 3 - Flusso della classificazione automatica del documento`

## 7. Corrispondenza con i requisiti funzionali

L'implementazione attuale copre i requisiti funzionali richiesti dalla traccia:

- `RF-01`: upload di documenti `PDF`, `DOCX`, `TXT`, anche multipli;
- `RF-02`: estrazione automatica del testo dai file supportati;
- `RF-03`: gestione di titolo, tipologia, autore, data di caricamento e tag;
- `RF-04`: memorizzazione dei metadati e del testo estratto in MongoDB, con file binario su filesystem;
- `RF-05`: indicizzazione dei documenti in un core Solr dedicato;
- `RF-06`: ricerca full-text con paginazione;
- `RF-07`: filtri per tipologia, autore e intervallo di date;
- `RF-08`: visualizzazione del dettaglio documento e download del file originale;
- `RF-09`: funzionalita' AI effettivamente implementata;
- `RF-10`: autenticazione di base e log delle operazioni.

Dal punto di vista del codice, tali requisiti sono distribuiti principalmente tra gli endpoint `auth`, `documents` e `search`, con il supporto dei servizi applicativi dedicati.

## 8. Gestione degli errori, robustezza e risultati del collaudo

La robustezza operativa costituisce una componente rilevante del progetto. L'implementazione prevede:

- errori `400` per formati non supportati o metadati non validi;
- errori `401` per credenziali non valide o token assente/non corretto;
- errori `404` per documento inesistente;
- errori `503` per indisponibilita' di MongoDB o Solr;
- fallback AI locale in caso di indisponibilita' del modello esterno;
- rollback della persistenza del documento se l'indicizzazione Solr fallisce successivamente al salvataggio.

In sede di collaudo, il sistema ha mostrato i seguenti comportamenti:

- compilazione Python corretta;
- test unitari superati;
- test di integrazione live superati;
- login amministratore funzionante;
- upload e download documento funzionanti;
- persistenza MongoDB funzionante;
- indicizzazione e ricerca Solr correttamente funzionanti;
- classificazione AI con fallback funzionante.

Il collaudo finale locale e' stato eseguito con MongoDB e Apache Solr avviati tramite Docker. La stessa applicazione puo' pero' usare anche un MongoDB online, modificando solo le variabili `MONGO_URI` e `MONGO_DB_NAME` nel file `.env`.

L'ambiente locale verificato utilizza:

- MongoDB su `localhost:27017`;
- Apache Solr su `localhost:8983`;
- core Solr dedicato `documents`;
- backend FastAPI su `http://127.0.0.1:8000`;
- credenziali demo `admin` / `Admin123!`.

Per la verifica su MongoDB online, il backend non richiede modifiche al codice. E' sufficiente configurare una stringa di connessione remota, ad esempio verso MongoDB Atlas o DigitalOcean Managed MongoDB, e assicurarsi che l'IP della macchina di test sia autorizzato nella allowlist del provider. Alla prima partenza, se il database remoto e' raggiungibile, l'applicazione crea automaticamente l'utente admin predefinito.

La risposta dell'endpoint `/health` ha confermato il corretto collegamento ai servizi:

```json
{"app":"ok","mongo":"ok","solr":"ok"}
```

Sono stati inoltre eseguiti:

- test unitari e di servizio con esito `11 passed`;
- test di integrazione live con esito `3 passed`;
- smoke test end-to-end con login, upload, classificazione AI, ricerca e dettaglio documento completati correttamente.

### 8.1 Immagine da inserire nel documento

Inserire in questa sezione uno screenshot della risposta di `/health` con MongoDB e Solr in stato `ok`, oppure uno screenshot dello smoke test end-to-end completato correttamente.

Didascalia consigliata:

`Figura 4 - Collaudo finale con MongoDB e Solr in Docker`

## 9. Limiti della soluzione

Pur soddisfacendo il perimetro dell'esercitazione, il progetto presenta alcuni limiti noti:

- assenza di OCR per documenti scansionati privi di testo nativo;
- autenticazione semplificata, priva di ruoli gerarchici articolati;
- assenza di una interfaccia frontend dedicata;
- necessita' di configurare correttamente i servizi esterni MongoDB e Solr prima della demo, in particolare allowlist e credenziali nel caso di MongoDB online;
- classificazione AI limitata a un insieme chiuso di categorie documentali.

Questi limiti risultano tuttavia coerenti con l'obiettivo didattico dell'attivita' e con la finestra temporale di sviluppo prevista.

## 10. Evoluzioni future

Le principali linee di estensione del sistema possono essere organizzate per priorita' funzionale. Le proposte seguenti non sono necessarie per soddisfare il perimetro dell'esercitazione, ma rappresentano sviluppi realistici per trasformare il prototipo in un sistema documentale aziendale piu' completo.

### 10.1 OCR per documenti scansionati

L'attuale sistema estrae testo da PDF nativi, DOCX e TXT, ma non esegue OCR su immagini o scansioni. In un contesto aziendale reale molti documenti storici possono essere scansioni prive di testo selezionabile. L'integrazione di un motore OCR, ad esempio Tesseract o un servizio cloud dedicato, permetterebbe di acquisire anche questi documenti e renderli ricercabili in Solr.

Il flusso potrebbe essere esteso in questo modo: se l'estrazione standard da PDF produce poco testo o testo vuoto, il backend attiva una fase OCR sulle pagine del documento, salva il testo ottenuto in MongoDB e lo indicizza normalmente in Solr. Il beneficio principale sarebbe l'aumento della copertura documentale, soprattutto per archivi storici, contratti firmati e documenti ricevuti via scansione.

### 10.2 Permessi granulari e ruoli organizzativi

L'autenticazione attuale e' volutamente semplice: l'utente autenticato puo' usare gli endpoint principali. In una versione aziendale sarebbe opportuno introdurre ruoli e permessi piu' dettagliati, ad esempio admin, ufficio acquisti, amministrazione, risorse umane e utente in sola lettura.

Questa evoluzione richiederebbe nuovi campi sui documenti, come `department`, `visibility` o `allowed_roles`, e controlli autorizzativi negli endpoint di ricerca, dettaglio e download. In questo modo un CV potrebbe essere visibile solo alle risorse umane, mentre fatture e ordini potrebbero essere accessibili all'amministrazione e agli acquisti. Il vantaggio sarebbe un controllo degli accessi piu' coerente con la riservatezza dei documenti aziendali.

### 10.3 Interfaccia web frontend

Il progetto espone gia' una Swagger UI sufficiente per test e demo tecnica, ma un utente aziendale non tecnico avrebbe bisogno di una interfaccia dedicata. Un frontend web potrebbe includere una pagina di login, una schermata di upload con selezione guidata dei metadati, una pagina di ricerca con filtri laterali e una vista dettaglio documento.

La realizzazione potrebbe avvenire con React, Vue o template server-side. Il backend FastAPI rimarrebbe invariato e il frontend consumerebbe gli endpoint gia' disponibili. Il beneficio principale sarebbe rendere il sistema utilizzabile da utenti operativi senza conoscenze tecniche o strumenti come curl e Swagger.

### 10.4 Espansione semantica della ricerca con AI

La query expansion e' una delle proposte AI progettuali gia' descritte. In una futura implementazione, quando l'utente cerca una parola generica o incompleta, il sistema potrebbe usare un modello AI per generare sinonimi, termini correlati o una formulazione piu' adatta a Solr.

Ad esempio, una ricerca come "computer ufficio" potrebbe essere espansa in "materiale informatico", "fornitura hardware", "postazioni di lavoro" e "stampanti". Il backend dovrebbe comunque mantenere un fallback: se il modello non risponde, viene usata la query originale. Questa funzionalita' migliorerebbe la qualita' dei risultati quando il lessico usato dall'utente non coincide con quello presente nei documenti.

### 10.5 Riassunto AI on demand

Il sistema salva gia' una sintesi breve prodotta durante la classificazione AI. Una possibile evoluzione consiste nel generare riassunti piu' dettagliati su richiesta, direttamente dalla pagina di dettaglio del documento.

Il riassunto on demand potrebbe essere utile per contratti lunghi, comunicazioni articolate o documentazione amministrativa. L'utente potrebbe richiedere una sintesi dei punti principali, delle scadenze, delle parti coinvolte o degli importi. Il risultato potrebbe essere mostrato a video e, se utile, salvato in cache per evitare chiamate ripetute al modello. In caso di errore dell'AI, il sistema continuerebbe a mostrare il testo estratto originale.

### 10.6 Dashboard amministrativa e monitoraggio

La collection `audit_log` registra gia' le operazioni principali. Una futura dashboard amministrativa potrebbe trasformare questi dati in indicatori utili: numero di documenti caricati, ricerche piu' frequenti, utenti piu' attivi, errori di indicizzazione, categorie documentali piu' presenti.

Questa evoluzione aiuterebbe l'amministratore a monitorare l'uso del sistema e a individuare problemi operativi. Ad esempio, molte ricerche senza risultati potrebbero indicare la necessita' di migliorare i metadati, aggiungere sinonimi o potenziare la ricerca semantica.

### 10.7 Versioning documentale

Nel sistema attuale ogni upload crea un nuovo documento. In un contesto reale puo' essere necessario gestire versioni successive dello stesso file, ad esempio un contratto aggiornato o una procedura interna revisionata.

Il versioning potrebbe essere implementato aggiungendo un campo `document_group_id`, un numero di versione e uno stato del documento, come `bozza`, `attivo` o `archiviato`. In questo modo sarebbe possibile mantenere lo storico delle modifiche, distinguere la versione corrente da quelle precedenti e ricostruire l'evoluzione del documento nel tempo.

## 11. Conclusioni

L'analisi e l'implementazione sviluppate dimostrano la fattibilita' di un sistema documentale aziendale costruito con una architettura modulare e tecnologie coerenti con il dominio applicativo. L'uso combinato di MongoDB e Solr consente di separare efficacemente persistenza e ricerca, mentre l'introduzione di una funzionalita' AI concreta amplia il valore del sistema senza comprometterne la controllabilita'.

Dal punto di vista accademico e progettuale, la soluzione risulta adeguata agli obiettivi dell'esercitazione poiche' traduce un caso d'uso realistico in un backend strutturato, documentato e verificabile, con una chiara relazione tra requisiti, architettura, dati e comportamento applicativo.
