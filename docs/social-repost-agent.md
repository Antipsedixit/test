# Piano per un agente di repost (Instagram, Facebook, X)

## 1) Obiettivo e perimetro
- Repost automatico dei contenuti pubblicati da profili specifici verso i tuoi canali.
- Canali di destinazione: **Instagram**, **Facebook**, **X**.
- Requisito chiave: usare **API ufficiali** o funzionalità native di condivisione dove disponibili, evitando scraping non autorizzato.

## 2) Compliance, policy e diritti
- Verifica le policy di automazione di Instagram/Facebook (Meta) e di X.
- Valuta i diritti d’autore e le condizioni d’uso per il riutilizzo dei contenuti.
- Quando possibile, **includi attribuzione** (es. “via @profilo_originale”) e/o usa funzioni di condivisione native.

## 3) Accesso ai contenuti sorgente
### Instagram + Facebook (Meta)
- Registrare un’app in **Meta for Developers**.
- Usare le **Graph API** per leggere contenuti pubblici **solo se consentito** (le API sono soggette a limiti e approvazioni).
- In caso di limitazioni, preferire meccanismi di condivisione nativi o integrazioni ufficiali.

### X (Twitter)
- Registrare un’app nel **Developer Portal**.
- Usare le API ufficiali per leggere i post di profili pubblici, rispettando rate limit e policy di riuso.

## 4) Flusso tecnico consigliato
1. **Collector**: processo pianificato (cron) che rileva nuovi post.
2. **Deduplicazione**: memorizzare gli ID dei post già ripostati in un database SQLite.
3. **Transform**: normalizzare contenuti (testo, media, link) per ogni piattaforma di destinazione.
4. **Publisher**: inviare i post ai canali di destinazione via webhook/API ufficiali.
5. **Log/Monitoraggio**: tracciare successi/fallimenti e gestire rate limit.

## 5) Implementazione inclusa nel repository
È stato aggiunto un agente Python funzionante in modalità:
- **live**: legge da X API (se hai token).
- **dry-run**: usa una sorgente locale JSON e stampa a terminale.

File principali:
- `agent/repost_agent.py`
- `agent/config.example.json`
- `agent/mock_source_posts.json`

## 6) Come avviarlo subito
1. Avvio test locale (senza pubblicazione reale):
   ```bash
   python3 agent/repost_agent.py --config agent/config.example.json --state-db agent/state.db --dry-run
   ```
2. Per produzione:
   - imposta token/env (`X_BEARER_TOKEN` e webhook di destinazione)
   - rimuovi `--dry-run`

## 7) Checklist operativa
- [ ] Identificare gli URL dei profili sorgente.
- [ ] Verificare policy e requisiti di accesso API per Instagram, Facebook, X.
- [ ] Configurare webhook o endpoint API reali per ogni destinazione.
- [ ] Impostare schedulazione (cron) per esecuzione periodica.
- [ ] Aggiungere attribuzione e controlli anti-spam.
- [ ] Testare in staging prima del go-live.

## 8) Come si procede, in pratica
1. **Conferma i profili**: URL ufficiali sorgente + tuoi profili destinazione.
2. **Definisci il perimetro contenuti**: solo testo/immagini/video.
3. **Scegli la frequenza**: ogni 5/10/15 minuti.
4. **Configura credenziali**: token X + webhook/API Meta.
5. **Esegui dry-run** per verificare deduplica e log.
6. **Attiva live** solo dopo validazione policy.
