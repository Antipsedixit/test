# Piano per agente di repost (Instagram, Facebook, X)

## 1) Obiettivo e perimetro
- Repost automatico dei contenuti pubblicati da profili specifici (es. profilo ufficiale di Fratelli d’Italia e Giorgia Meloni) verso i tuoi canali.
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
1. **Collector**: processo pianificato (cron) o webhook (se disponibile) che rileva nuovi post.
2. **Deduplicazione**: memorizzare gli ID dei post già ripostati in un database leggero.
3. **Transform**: normalizzare contenuti (testo, media, link) per ogni piattaforma di destinazione.
4. **Publisher**: pubblicare sui tuoi profili via API ufficiali o strumenti consentiti.
5. **Log/Monitoraggio**: tracciare successi/fallimenti e gestire rate limit.

## 5) Stack suggerito (codice)
- **Backend**: Node.js o Python.
- **DB**: SQLite / PostgreSQL / DynamoDB.
- **Scheduler**: cron, serverless (AWS Lambda/Cloud Functions) o un job manager.
- **Secrets**: vault o secret manager per token/API keys.

## 6) Limiti e rischi tipici
- Restrizioni API sui contenuti di terzi (specialmente Instagram).
- Rate limit e sospensione account se i repost non rispettano policy.
- Possibili limitazioni alla pubblicazione di media (immagini/video) via API.

## 7) Checklist operativa
- [ ] Identificare gli URL dei profili sorgente.
- [ ] Verificare policy e requisiti di accesso API per Instagram, Facebook, X.
- [ ] Definire modalità di repost (nativo vs API).
- [ ] Implementare log e deduplica.
- [ ] Aggiungere attribuzione e controlli anti-spam.
- [ ] Testare con un ambiente staging.

## 8) Prossimi passi consigliati
- Conferma i profili esatti (URL) e l’ambito (solo testi, immagini, video?).
- Decidi se vuoi soluzione **no-code** (Zapier/Make) o **codice personalizzato**.
- In base alle API disponibili, progettare un MVP con un singolo canale di destinazione.

## 9) Come si procede, in pratica (checklist breve)
1. **Conferma i profili**: inviami gli URL ufficiali dei profili sorgente e dei tuoi canali di destinazione.
2. **Definisci il contenuto da ripostare**: solo testo? immagini? video? storie/reel?
3. **Scegli modalità di automazione**:
   - **No-code**: se vuoi rapidità e limiti accettabili.
   - **Codice**: se servono logiche personalizzate, deduplica avanzata e controllo completo.
4. **Verifica accessi API**:
   - Meta (Instagram/Facebook) + X: token, permessi, limiti.
5. **Decidi la frequenza**: ogni nuovo post (webhook/polling) o batch periodico.
6. **Regole di ripubblicazione**: attribuzione, formati, filtri (escludi post sponsorizzati?).
