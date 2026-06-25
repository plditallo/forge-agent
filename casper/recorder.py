import hashlib
import json
import os
import subprocess
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

TESTNET_RPC = os.getenv("CASPER_TESTNET_RPC", "https://node.testnet.casper.network/rpc")
TESTNET_FAUCET = os.getenv("CASPER_TESTNET_FAUCET", "https://testnet.cspr.live/tools/faucet")

# Path to the Node.js project that holds the deployed contract, the keys,
# and the casper-js-sdk dependency. Adjust if your folder layout differs.
CASPER_CONTRACT_DIR = os.getenv(
    "CASPER_CONTRACT_DIR",
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "..", "forge-casper-contract")
)
CALL_CONTRACT_SCRIPT = os.path.join(CASPER_CONTRACT_DIR, "call_contract.js")

# The ForgeRegistry contract package hash, deployed 2026-06-21 to Casper testnet.
# https://testnet.cspr.live/contract/160ad02bc56d6ec6b034139281bce4dee1757d69fdfdf69b81706fef66ccc260
FORGE_REGISTRY_PACKAGE_HASH = "160ad02bc56d6ec6b034139281bce4dee1757d69fdfdf69b81706fef66ccc260"

# Human-readable messages for each error category, intended for direct
# display in the UI so a live-demo failure has a clear, specific explanation
# rather than a raw exception string.
ERROR_CATEGORY_MESSAGES = {
    "missing_key_file": "Casper testnet wallet key file is missing on the server. Contact the administrator.",
    "network_unreachable": "Could not reach the Casper testnet node. This is usually temporary — please try again in a moment.",
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


def call_forge_registry_contract(dataset_hash: str, score: int, tier: str, timeout: int = 120) -> dict:
    """
    Calls record_certification on the deployed ForgeRegistry contract on Casper
    testnet by shelling out to call_contract.js (casper-js-sdk), since the
    Rust/Python Casper toolchains have native Windows compilation issues that
    casper-js-sdk (pure JS) does not share.

    Returns a dict with at minimum a "success" boolean. On success, includes
    "txHash" and "explorerUrl". On failure, includes "error".
    """
    if not os.path.exists(CALL_CONTRACT_SCRIPT):
        return {
            "success": False,
            "error": f"call_contract.js not found at {CALL_CONTRACT_SCRIPT}"
        }

    try:
        result = subprocess.run(
            ["node", CALL_CONTRACT_SCRIPT, dataset_hash, str(score), tier],
            cwd=CASPER_CONTRACT_DIR,
            capture_output=True,
            text=True,
            timeout=timeout,
            encoding="utf-8",
            errors="replace"
        )
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": f"Casper contract call timed out after {timeout} seconds"
        }
    except FileNotFoundError:
        return {
            "success": False,
            "error": "node executable not found — is Node.js installed and on PATH?"
        }

    # The Node script writes diagnostic logs to stderr and exactly one JSON
    # line to stdout. Parse the last non-empty stdout line as JSON.
    #
    # stdout/stderr can legitimately come back as None in edge cases (e.g.
    # the subprocess was killed before producing output), so this guards
    # against an AttributeError on .strip() rather than assuming a string.
    stdout_text = result.stdout or ""
    stderr_text = result.stderr or ""
    stdout_lines = [line for line in stdout_text.strip().splitlines() if line.strip()]
    if not stdout_lines:
        return {
            "success": False,
            "error": "No output from call_contract.js",
            "stderr": stderr_text[-2000:] if stderr_text else None
        }

    try:
        parsed = json.loads(stdout_lines[-1])
    except json.JSONDecodeError:
        return {
            "success": False,
            "error": "Could not parse call_contract.js output as JSON",
            "raw_stdout": stdout_lines[-1],
            "stderr": stderr_text[-2000:] if stderr_text else None
        }

    return parsed


def record_assessment_on_chain(assessment_id: int, dataset_name: str,
                                weighted_score: float, metal_rating: str,
                                scores: dict) -> dict:
    """
    Records a FORGE assessment by calling record_certification on the live
    ForgeRegistry smart contract deployed on Casper testnet. Falls back to a
    local-only SHA-256 hash (with an explicit failure note) if the on-chain
    call cannot complete, so the assessment flow never blocks on chain issues.
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

    # On-chain call failed — log it clearly but don't block the assessment.
    error = chain_result.get("error", "Unknown error calling Casper contract")
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
        dataset_name="Test Dataset — recorder.py standalone test",
        weighted_score=72.5,
        metal_rating="Silver",
        scores={"data_quality": 4, "reliability": 3}
    )
    print(json.dumps(result, indent=2))
