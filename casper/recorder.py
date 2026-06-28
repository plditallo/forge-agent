import hashlib
import json
import os
import requests
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

TESTNET_RPC = os.getenv("CASPER_TESTNET_RPC", "https://node.testnet.casper.network/rpc")
TESTNET_FAUCET = os.getenv("CASPER_TESTNET_FAUCET", "https://testnet.cspr.live/tools/faucet")

# The Casper bridge service (Node.js + casper-js-sdk) that actually signs and
# submits transactions to the Casper testnet. Calling it over HTTP rather than
# via local subprocess means this works identically whether forge-agent is
# running locally or deployed to Azure -- the bridge itself is the only thing
# that needs Node.js / the Casper toolchain, not wherever this Python code runs.
CASPER_BRIDGE_URL = os.getenv("CASPER_BRIDGE_URL", "http://localhost:3000")
CASPER_BRIDGE_API_KEY = os.getenv("CASPER_BRIDGE_API_KEY", "")

# The ForgeRegistry contract package hash, deployed 2026-06-21 to Casper testnet.
# https://testnet.cspr.live/contract/160ad02bc56d6ec6b034139281bce4dee1757d69fdfdf69b81706fef66ccc260
FORGE_REGISTRY_PACKAGE_HASH = "160ad02bc56d6ec6b034139281bce4dee1757d69fdfdf69b81706fef66ccc260"

ERROR_CATEGORY_MESSAGES = {
    "missing_key_file": "Casper testnet wallet key is not configured on the bridge service. Contact the administrator.",
    "network_unreachable": "Could not reach the Casper testnet node. This is usually temporary — please try again in a moment.",
    "bridge_unreachable": "Could not reach the Casper bridge service. This is usually temporary — please try again in a moment.",
    "out_of_gas": "The on-chain transaction ran out of gas. This has been logged for review.",
    "insufficient_balance": "The Casper testnet wallet balance is too low to complete this on-chain transaction.",
    "unknown": "An unexpected error occurred while anchoring this assessment to the Casper testnet."
}


def get_friendly_error_message(error_category: str) -> str:
    return ERROR_CATEGORY_MESSAGES.get(error_category, ERROR_CATEGORY_MESSAGES["unknown"])


def hash_assessment(assessment_data: dict) -> str:
    canonical = json.dumps(assessment_data, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode()).hexdigest()


def build_assessment_record(assessment_id: int, dataset_name: str,
                             weighted_score: float, metal_rating: str,
                             scores: dict) -> dict:
    return {
        "forge_version": "0.1.0",
        "assessment_id": assessment_id,
        "dataset_name": dataset_name,
        "weighted_score": weighted_score,
        "metal_rating": metal_rating,
        "scores": scores,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


def call_forge_registry_contract(dataset_hash: str, score: int, tier: str, timeout: int = 60) -> dict:
    """
    Calls record_certification on the deployed ForgeRegistry contract on Casper
    testnet by calling the Casper bridge service (Node.js + casper-js-sdk) over
    HTTP. The bridge handles all key management and chain interaction -- this
    function just makes the request and normalizes the response shape.
    """
    try:
        response = requests.post(
            f"{CASPER_BRIDGE_URL}/record-certification",
            json={"datasetHash": dataset_hash, "score": score, "tier": tier},
            headers={
                "Content-Type": "application/json",
                "x-bridge-api-key": CASPER_BRIDGE_API_KEY
            },
            timeout=timeout
        )
    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "error": f"Could not connect to Casper bridge service at {CASPER_BRIDGE_URL}",
            "errorCategory": "bridge_unreachable"
        }
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error": f"Casper bridge service did not respond within {timeout} seconds",
            "errorCategory": "bridge_unreachable"
        }
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": f"Error calling Casper bridge service: {str(e)}",
            "errorCategory": "unknown"
        }

    try:
        return response.json()
    except json.JSONDecodeError:
        return {
            "success": False,
            "error": "Casper bridge service returned a non-JSON response",
            "errorCategory": "unknown",
            "raw_response": response.text[:500]
        }


def call_forge_purchase_transfer(amount_motes: int = None) -> dict:
    """
    Records a marketplace purchase as a real CSPR transfer on Casper testnet
    by calling the bridge's /record-purchase endpoint. This is intentionally
    a plain transfer rather than a contract call -- it doesn't try to encode
    "this was a purchase" into the certification contract's score/tier
    fields, which would be misleading since a purchase isn't a certification.
    """
    body = {}
    if amount_motes:
        body["amountMotes"] = str(amount_motes)

    try:
        response = requests.post(
            f"{CASPER_BRIDGE_URL}/record-purchase",
            json=body,
            headers={
                "Content-Type": "application/json",
                "x-bridge-api-key": CASPER_BRIDGE_API_KEY
            },
            timeout=60
        )
    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "error": f"Could not connect to Casper bridge service at {CASPER_BRIDGE_URL}",
            "errorCategory": "bridge_unreachable"
        }
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error": "Casper bridge service did not respond in time",
            "errorCategory": "bridge_unreachable"
        }
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": f"Error calling Casper bridge service: {str(e)}",
            "errorCategory": "unknown"
        }

    try:
        return response.json()
    except json.JSONDecodeError:
        return {
            "success": False,
            "error": "Casper bridge service returned a non-JSON response",
            "errorCategory": "unknown",
            "raw_response": response.text[:500]
        }


def record_purchase_on_chain(buyer_id: str, listing_id: int, payment_proof: str,
                              amount_motes: int = None) -> dict:
    """
    Anchors a marketplace purchase on Casper testnet as a real CSPR transfer.
    Falls back to a local-only SHA-256 audit hash if the on-chain call cannot
    complete, so a purchase is never blocked by a chain/bridge issue.
    """
    audit_hash_input = f"{buyer_id}:{listing_id}:{payment_proof}:{datetime.now(timezone.utc).isoformat()}"
    audit_hash = hashlib.sha256(audit_hash_input.encode()).hexdigest()

    chain_result = call_forge_purchase_transfer(amount_motes=amount_motes)

    if chain_result.get("success"):
        tx_hash = chain_result.get("txHash")
        print(f"FORGE purchase (listing #{listing_id}, buyer {buyer_id}) recorded on-chain: {tx_hash}")
        return {
            "success": True,
            "audit_hash": audit_hash,
            "casper_tx_hash": tx_hash,
            "explorer_url": chain_result.get(
                "explorerUrl",
                f"https://testnet.cspr.live/transaction/{tx_hash}" if tx_hash else None
            ),
            "recorded_at": datetime.now(timezone.utc).isoformat(),
            "note": "Recorded as a real CSPR transfer on Casper testnet"
        }

    error = chain_result.get("error", "Unknown error calling Casper bridge service")
    error_category = chain_result.get("errorCategory", "unknown")
    is_low_balance = chain_result.get("lowBalance", False)

    print(f"WARNING: purchase on-chain recording failed [{error_category}]: {error}")

    return {
        "success": False,
        "audit_hash": audit_hash,
        "casper_tx_hash": None,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "error": error,
        "error_category": error_category,
        "friendly_message": get_friendly_error_message(error_category),
        "low_balance": is_low_balance,
        "note": "On-chain recording failed; local audit hash computed but not anchored to Casper testnet"
    }


def record_assessment_on_chain(assessment_id: int, dataset_name: str,
                                weighted_score: float, metal_rating: str,
                                scores: dict) -> dict:
    """
    Records a FORGE assessment by calling record_certification on the live
    ForgeRegistry smart contract deployed on Casper testnet, via the Casper
    bridge service. Falls back to a local-only SHA-256 hash (with an explicit
    failure note) if the on-chain call cannot complete, so the assessment
    flow never blocks on chain or bridge issues.
    """
    record = build_assessment_record(
        assessment_id, dataset_name, weighted_score, metal_rating, scores
    )

    assessment_hash = hash_assessment(record)
    score_int = int(round(weighted_score))

    chain_result = call_forge_registry_contract(
        dataset_hash=assessment_hash,
        score=score_int,
        tier=metal_rating
    )

    if chain_result.get("success"):
        tx_hash = chain_result.get("txHash")
        print(f"FORGE Assessment #{assessment_id} recorded on-chain: {tx_hash}")
        return {
            "success": True,
            "assessment_hash": assessment_hash,
            "casper_tx_hash": tx_hash,
            "explorer_url": chain_result.get(
                "explorerUrl",
                f"https://testnet.cspr.live/transaction/{tx_hash}" if tx_hash else None
            ),
            "contract_package_hash": FORGE_REGISTRY_PACKAGE_HASH,
            "record": record,
            "recorded_at": datetime.now(timezone.utc).isoformat(),
            "note": "Recorded via record_certification on the live ForgeRegistry contract (Casper testnet)"
        }

    error = chain_result.get("error", "Unknown error calling Casper bridge service")
    error_category = chain_result.get("errorCategory", "unknown")
    is_low_balance = chain_result.get("lowBalance", False)

    print(f"WARNING: FORGE Assessment #{assessment_id} on-chain recording failed "
          f"[{error_category}]: {error}")

    return {
        "success": False,
        "assessment_hash": assessment_hash,
        "casper_tx_hash": None,
        "contract_package_hash": FORGE_REGISTRY_PACKAGE_HASH,
        "record": record,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "error": error,
        "error_category": error_category,
        "friendly_message": get_friendly_error_message(error_category),
        "low_balance": is_low_balance,
        "note": "On-chain recording failed; local hash computed but not anchored to Casper testnet"
    }


if __name__ == "__main__":
    # Quick test — this performs a REAL on-chain call and costs real testnet CSPR.
    result = record_assessment_on_chain(
        assessment_id=999,
        dataset_name="Test Dataset — recorder.py HTTP bridge test",
        weighted_score=72.5,
        metal_rating="Silver",
        scores={"data_quality": 4, "reliability": 3}
    )
    print(json.dumps(result, indent=2))
