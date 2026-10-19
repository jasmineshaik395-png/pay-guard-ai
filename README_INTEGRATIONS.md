PayGuard AI: PayPal Sandbox and AI integration files
These are supplementary integration modules for the existing Streamlit prototype. They do not automatically change or wire themselves into app.py; you or your developer must call these functions from the app UI before claiming the integrations are fully connected.
Included files
- paypal_sandbox.py: creates and captures PayPal Sandbox Orders API orders.
- fraud_detection.py: demonstrates unsupervised anomaly scoring with scikit-learn Isolation Forest.
- .env.example: names the PayPal Sandbox environment variables without including secrets.
- requirements-additions.txt: extra Python packages required by these modules.
PayPal Sandbox setup
1. Create a developer account at https://developer.paypal.com/.
2. Open Apps & Credentials, select Sandbox, and create or select a REST app.
3. Copy the Sandbox Client ID and Secret.
4. Set these as environment variables PAYPAL_CLIENT_ID and PAYPAL_CLIENT_SECRET. For local development, you may copy .env.example to .env and load it with python-dotenv.
5. Install the added packages:
   pip install -r requirements-additions.txt
6. Use only Sandbox buyer/seller accounts and sandbox credentials. The API base URL in paypal_sandbox.py is https://api-m.sandbox.paypal.com.
Example:
from paypal_sandbox import create_sandbox_order

order = create_sandbox_order("10.00", "USD")
print(order["id"])
# Open the approval URL from order["links"] in a browser to approve the sandbox order.
After the buyer approves the order, capture it using:
from paypal_sandbox import capture_sandbox_order

capture = capture_sandbox_order("PASTE_APPROVED_ORDER_ID_HERE")
print(capture["status"])
Do not automatically capture an order before the buyer approves it. For a complete checkout experience, your app must present the approval link and handle the approval/capture flow.
AI anomaly-detection setup
Example using a Pandas DataFrame:
import pandas as pd
from fraud_detection import score_transactions

transactions = pd.read_csv("sample_transactions.csv")
scored = score_transactions(transactions)
print(scored[["transaction_id", "anomaly_label", "anomaly_score"]])
The example uses scikit-learn Isolation Forest, an unsupervised anomaly-detection model. It labels patterns that differ from the data it is fitted on. It is a demonstration, not proof that a transaction is fraudulent. Results depend on the sample data and must be evaluated on representative, labelled data before any real-world use.
Important implementation note
The original PayGuard AI dashboard uses transparent hand-written rules. Adding these files alone does not integrate them into the existing dashboard. To complete the integration, modify app.py to call score_transactions() and add a user-approved PayPal Sandbox checkout flow that calls create_sandbox_order() and capture_sandbox_order().
Security
- Never commit .env, API secrets, access tokens, or buyer information.
- Keep .env in .gitignore.
- Do not use production PayPal credentials for this demo.
- Do not use this prototype to approve or decline real payments.
