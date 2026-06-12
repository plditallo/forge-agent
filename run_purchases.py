import requests

purchases = [
    ("BUYER-498FD898", 2,    "epa-health-001"),
    ("BUYER-498FD898", 2002, "health-admissions-001"),
    ("BUYER-1090CA15", 2,    "epa-realestate-001"),
    ("BUYER-1090CA15", 2003, "permits-001"),
]

for buyer_id, listing_id, proof in purchases:
    r = requests.get(
        "http://127.0.0.1:8000/marketplace/data/" + str(listing_id) +
        "?buyer_id=" + buyer_id + "&payment_proof=" + proof
    )
    data = r.json()
    print(
        "Buyer", buyer_id[:12],
        "| Listing", listing_id,
        "| Import", data.get("api_import_id"),
        "| Records", data.get("records_delivered"),
        "| Hash", str(data.get("casper_tx_hash", ""))[:16] + "..."
    )
