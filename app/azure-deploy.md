# Deploy to Azure App Service (EU region)

## One-time setup — 20 minutes

### 1. Create the App Service (Azure portal or CLI)

```bash
# Login
az login

# Create resource group in West Europe (or Sweden Central)
az group create --name efta-ai-registry --location westeurope

# Create App Service plan (free tier to start)
az appservice plan create \
  --name efta-registry-plan \
  --resource-group efta-ai-registry \
  --sku B1 \
  --is-linux

# Create the web app (Python 3.12)
az webapp create \
  --name efta-ai-registry \
  --resource-group efta-ai-registry \
  --plan efta-registry-plan \
  --runtime "PYTHON:3.12"
```

### 2. Set environment variables

```bash
az webapp config appsettings set \
  --name efta-ai-registry \
  --resource-group efta-ai-registry \
  --settings \
    ANTHROPIC_API_KEY="your-key-here" \
    SECRET_KEY="your-long-random-string" \
    SCM_DO_BUILD_DURING_DEPLOYMENT=true
```

### 3. Deploy the app

From the `app/` folder:

```bash
# Zip deploy (simplest)
zip -r ../deploy.zip . -x "*.pyc" -x "__pycache__/*" -x "cases.db"

az webapp deployment source config-zip \
  --name efta-ai-registry \
  --resource-group efta-ai-registry \
  --src ../deploy.zip
```

App is live at: `https://efta-ai-registry.azurewebsites.net`

### 4. Add startup command

In Azure portal → App Service → Configuration → General settings:
```
gunicorn --bind=0.0.0.0 --timeout 600 app:app
```

Or add a `startup.sh`:
```bash
pip install gunicorn && gunicorn --bind=0.0.0.0 --timeout 600 app:app
```

---

## Distribute as Windows app via Intune

Once the app is live at its HTTPS URL:

1. **Intune portal** → Apps → + Add → **Web link**
2. Name: `EFTA AI Use Case Registry`
3. URL: `https://efta-ai-registry.azurewebsites.net`
4. Icon: upload `static/icons/icon-512.png`
5. Assign to: All EFTA staff group

Staff open Company Portal → click the app → it opens in Edge and prompts
"Install this site as an app" → one click install → appears in Start menu
and taskbar like a native Windows app.

---

## Persistent database

The default SQLite file lives inside the container and resets on redeploy.
For production, swap to Azure Database for PostgreSQL (Flexible Server,
West Europe) — a one-file change in `app.py`. Flag this to IT before
going live with real submissions.

---

## HTTPS / EU data residency confirmation

- Azure App Service in West Europe (Netherlands) or Sweden Central = EU jurisdiction
- All data in transit: HTTPS enforced by default on azurewebsites.net
- SQLite / PostgreSQL data at rest: Azure EU region storage
- AI calls: Anthropic API (US). For full EU residency, switch to
  Claude via AWS Bedrock eu-central-1 (Frankfurt) — one-line change in app.py
