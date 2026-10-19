# PayGuard AI

PayGuard AI is an educational payment-risk dashboard built with Python, Streamlit, Pandas, and Plotly. This repository preserves the existing rules-based demo and CSV while packaging it for the managed public website runtime.

## Run locally

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Open <http://localhost:8501>.

## Dashboard behavior

The app calculates its metrics from `sample_transactions.csv`, ignoring repeated CSV header rows and exact duplicate records. The supplied file resolves to 10 distinct fictional transactions. The original rules are preserved: amount >= $1,000 adds 40 points; a country mismatch marked Yes adds 35; failed attempts >= 3 adds 25; scores are capped at 100; High >= 60, Medium >= 30, otherwise Low. Missing and invalid values are handled safely and do not trigger their associated rules.

The app includes Dashboard, Transactions, Risk Analysis, Check Transaction, Reports, and About pages, interactive Plotly charts, transaction filters, data-derived alerts, and scored CSV downloads. It only displays a status if a status field exists in the source data.

## Managed public website

The `Dockerfile` installs the declared Python packages and Nginx. `start.sh` runs Streamlit on an internal port and Nginx on the platform-provided `PORT` (default 3000); Nginx forwards HTTP and WebSocket traffic and serves `public/manus-routes.json` at the website root. The health endpoint `/healthz` checks Streamlit's own health endpoint through the proxy.

The managed website configuration uses a server container, no database, `Dockerfile`, and `/healthz`. Save a checkpoint to the managed project's canonical `main` branch, then use the project's Publish action to create/update the public deployment. Preview and a saved checkpoint are not themselves proof of a live public deployment; use the URL returned after a successful Publish.

The Streamlit CORS allowlist in `.streamlit/config.toml` trusts only the published origin, `https://payguard-dps6tdyk.manus.space`, and this project's stable Preview origin, `https://8328-ihvsaymu5j8ztae6ox2l8-3c66f6d1.sg2.manus.computer`. This lets browser WebSockets connect through the managed gateway while retaining XSRF protection. If you add a custom domain or the platform changes the Preview origin, update the allowlist before publishing.

The website's published address is persistent. The platform may use an on-demand hosting mode, in which idle traffic can let the container sleep and a later visit may have a cold-start delay. This app has no user accounts, payment-provider connections, persistent user data, or real-time fraud monitoring. The filesystem inside the published container is ephemeral; the dashboard reads the committed sample CSV.

## Limitations

This is a transparent hand-written rules demo, not a trained or validated fraud model. It does not connect to PayPal, a bank, or any payment processor and must not be used to approve or decline real payments.
