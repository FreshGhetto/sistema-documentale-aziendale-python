# Configurazione Apache Solr

Questa esercitazione assume Solr in locale sulla porta `8983`.

## 1. Avvio di Solr

```bash
solr start -p 8983
```

## 2. Creazione del core dedicato

```bash
solr create -c documents
```

## 3. Campi richiesti

Aprire l'admin panel di Solr oppure usare le API Schema per creare i campi definiti in [schema_fields.json](schema_fields.json).

Esempio con `curl`:

```bash
curl -X POST -H "Content-type:application/json" --data-binary @solr/schema_fields.json http://localhost:8983/solr/documents/schema
```

## 4. Analyzer italiano

Per i campi `title_txt_it`, `content_txt_it` e `ai_summary_txt_it` usare il tipo `text_it` definito in [text_it_fieldtype.json](text_it_fieldtype.json):

```bash
curl -X POST -H "Content-type:application/json" --data-binary @solr/text_it_fieldtype.json http://localhost:8983/solr/documents/schema
```

Se il core contiene già un `managed-schema`, applicare prima il field type e poi i campi.

## 5. Verifica

Controllare la risposta di health dell'applicazione:

```bash
curl http://127.0.0.1:8000/health
```

Atteso:

```json
{"app":"ok","mongo":"ok","solr":"ok"}
```
