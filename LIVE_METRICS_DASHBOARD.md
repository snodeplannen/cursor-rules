# Live Metrics Dashboard

Het MCP Invoice Processor dashboard toont nu **live metrics** van de draaiende MCP server via een gedeeld JSON bestand.

## 🚀 Hoe het werkt

1. **MCP Server** → Schrijft metrics naar `logs/metrics_live.json` na elke document verwerking
2. **Dashboard** → Leest metrics uit `logs/metrics_live.json` en toont live data
3. **Fallback** → Als er geen live data is, toont het dashboard demo data

## 📊 Gebruik

### Stap 1: Start de MCP Server (Cursor doet dit automatisch)

De MCP server wordt automatisch gestart door Cursor en schrijft live metrics naar het bestand.

### Stap 2: Start het Dashboard

**Met uv:**
```powershell
uv run python -m mcp_invoice_processor.monitoring.dashboard
```

**Of met Python:**
```powershell
$env:PYTHONPATH="src"
python -m mcp_invoice_processor.monitoring.dashboard
```

### Stap 3: Open Dashboard

Open je browser en ga naar: **http://localhost:8000**

Je ziet nu:
- 🔴 **LIVE DATA** badge als er live metrics zijn
- 📊 **DEMO DATA** badge als er geen live metrics zijn

## 🔍 Endpoints

| Endpoint | Beschrijving |
|----------|-------------|
| `GET /` | Dashboard homepage met visualisaties |
| `GET /metrics` | JSON metrics data |
| `GET /metrics/prometheus` | Prometheus format metrics |
| `GET /health` | Health check |
| `GET /health/detailed` | Gedetailleerde health check |
| `POST /demo/reset` | Reset demo metrics |
| `GET /demo/status` | Demo status |

## 🧪 Test Live Metrics

Test de live metrics sharing:

```powershell
uv run test_live_metrics.py
```

Dit simuleert enkele document verwerking events en toont of de metrics correct worden opgeslagen.

## 📁 Metrics Bestand

**Locatie:** `logs/metrics_live.json`

Dit bestand wordt automatisch:
- ✅ Aangemaakt door de metrics collector
- ✅ Bijgewerkt na elke document verwerking
- ✅ Gelezen door het dashboard voor live data

## 🎯 Live Data vs Demo Data

### Live Data (🔴)
- Komt van draaiende MCP server
- Real-time updates bij document verwerking
- Toont echte Ollama integratie metrics
- Opgeslagen in `logs/metrics_live.json`

### Demo Data (📊)
- Gebruikt als fallback
- Gegenereerd bij dashboard startup
- Alleen lokaal in dashboard proces
- Niet gedeeld met MCP server

## 🔄 Auto-refresh

Het dashboard vernieuwt automatisch elke 30 seconden. Je kunt ook handmatig vernieuwen met de **🔄 Vernieuwen** knop.

## 💡 Tips

1. **Parallelle processen:** Start het dashboard in een aparte terminal terwijl Cursor MCP server draait
2. **Live updates:** Verwerk documenten via de MCP tools om live updates te zien
3. **Metrics reset:** POST naar `/demo/reset` om demo data opnieuw te genereren
4. **Logs bekijken:** Check `logs/` directory voor alle log bestanden

## 🐛 Troubleshooting

### Dashboard toont DEMO DATA

**Probleem:** Je ziet "📊 DEMO DATA" in plaats van "🔴 LIVE DATA"

**Oplossingen:**
1. Controleer of `logs/metrics_live.json` bestaat
2. Verwerk een document via MCP tools om metrics te genereren
3. Check of MCP server draait in Cursor

### Metrics worden niet bijgewerkt

**Probleem:** Live data toont oude metrics

**Oplossingen:**
1. Vernieuw de pagina (F5)
2. Wacht op auto-refresh (30 sec)
3. Restart het dashboard

### Module errors bij test

**Probleem:** `ModuleNotFoundError` bij test script

**Oplossing:** Gebruik altijd `uv run`:
```powershell
uv run test_live_metrics.py
```

## 📈 Voorbeeld Output

Wanneer het dashboard live data toont zie je:

```
📊 MCP Invoice Processor Monitoring
Real-time monitoring van documentverwerking en systeem status
🔴 LIVE DATA
Laatste update: 2025-08-24T12:45:30.123456

Document Verwerking:
- Totaal Verwerkt: 15
- Succesvol: 13
- Gefaald: 2
- Succes Rate: 86.67%

Ollama Integratie:
- Totaal Requests: 15
- Succesvol: 14
- Gefaald: 1
- Succes Rate: 93.33%
```

## 🎉 Klaar!

Je dashboard toont nu live metrics van de MCP server. Verwerk documenten via de MCP tools en zie real-time updates in het dashboard!

