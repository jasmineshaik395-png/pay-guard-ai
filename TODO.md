# PayGuard AI — Delivery outcomes

- [x] **Permanent hosted Streamlit application.** Preserve the existing Python/Streamlit architecture, current working behavior, educational/demo scope, and understandable beginner-friendly code; update documentation and dependency declarations only where required. Prepare a stable public deployment and clearly explain any platform limitation or manual deployment step that cannot be completed automatically.

- [x] **Responsive security dashboard shell.** Implement PayGuard AI branding, a dark navy/purple left sidebar, functional Dashboard, Transactions, Risk Analysis, Check Transaction, Reports, and About navigation, plus the specified light-lavender “Welcome to PayGuard AI” banner, short description, and polished rounded card layout. Keep the site responsive on desktop and mobile and inspired by the supplied reference while adapting it to payment security.

- [x] **Defensive CSV preparation and data-derived metrics.** Load the project CSV defensively; ignore repeated CSV header rows and exact duplicate records, handle missing fields and malformed values safely, and ensure the copied sample resolves to its 10 distinct fictional transactions. Calculate Total, High-Risk, Medium-Risk, and Low-Risk cards exclusively from the cleaned CSV; do not hardcode fake statistics.

- [x] **Interactive charts and transaction explorer.** Provide interactive Plotly transaction risk distribution and risk summary charts derived from the cleaned dataset. Show transaction ID, amount, risk score, risk level, and status only if the status field actually exists. Make table filters work.

- [x] **Dataset-derived risk alerts.** Generate useful risk alerts from actual CSV contents and distinguish data-derived findings from general educational guidance.

- [x] **Working demo transaction check.** Validate the form inputs and preserve the existing rule behavior exactly: amount >= 1000 adds 40 points; country_mismatch == Yes adds 35; failed_attempts >= 3 adds 25; score is capped at 100; High >= 60, Medium >= 30, otherwise Low. Show the score and triggered-rule explanation.

- [x] **Honest demo limitations.** Keep an explicit educational/demo disclaimer on appropriate views. Do not claim real-time fraud detection, bank integration, validated AI predictions, or any capability not present in the project.

- [x] **Managed production runtime and deployment contract.** Package and serve the Python/Streamlit app through the managed website’s container runtime, provide the required unauthenticated health endpoint and route manifest, and configure the container deployment contract without adding an unnecessary database. Keep application paths relative to the public origin and explain residency/cold-start behavior honestly.

- [x] **Documentation and source continuity.** Preserve the sample data and existing project functionality; update the README with local run, managed publishing, and redeployment guidance. Keep dependency changes limited to those required for the hosted runtime.

- [x] **Public dashboard WebSocket connection.** Ensure the published Streamlit page establishes its interactive session from the exact public origin `https://payguard-dps6tdyk.manus.space` and the current managed Preview origin `https://8328-ihvsaymu5j8ztae6ox2l8-3c66f6d1.sg2.manus.computer`, despite the platform's internal proxy Host, so it renders instead of remaining on a loading skeleton. Keep the allowlist restricted to those origins and retain XSRF protection.
