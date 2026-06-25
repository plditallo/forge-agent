/**
 * server.js
 *
 * Thin HTTP wrapper around call_contract.js's record_certification logic,
 * so the Python backend (running on a separate Azure App Service, or
 * locally) can call this over HTTP instead of via subprocess.
 *
 * This is the Azure-deployable version of the local subprocess bridge.
 * The contract-calling logic itself is unchanged from call_contract.js --
 * this just exposes it as a single POST endpoint.
 *
 * Endpoint:
 *   POST /record-certification
 *   Body: { "datasetHash": "...", "score": 88, "tier": "Gold" }
 *
 * Response (success):
 *   { "success": true, "txHash": "...", "explorerUrl": "..." }
 *
 * Response (failure):
 *   { "success": false, "error": "...", "errorCategory": "..." }
 */

const express = require("express");
const fs = require("fs");
const path = require("path");
require("dotenv").config();

const {
  PrivateKey,
  KeyAlgorithm,
  ContractCallBuilder,
  Args,
  CLValue,
  HttpHandler,
  RpcClient,
  PurseIdentifier,
} = require("casper-js-sdk");

const app = express();
app.use(express.json());

// ---- Configuration ----
const PORT = process.env.PORT || 3000;
const NODE_RPC_URL = process.env.CASPER_TESTNET_RPC || "https://node.testnet.casper.network/rpc";
const CHAIN_NAME = process.env.CASPER_CHAIN_NAME || "casper-test";

// On Azure, the secret key arrives via an App Setting (environment variable)
// holding the PEM content directly, rather than a file path -- file paths
// are awkward to manage in App Service's deployment model, and the key
// should not be committed to the repo regardless of deployment target.
// CASPER_SECRET_KEY_PEM takes priority; CASPER_SECRET_KEY_PATH remains
// supported for local development continuity.
const SECRET_KEY_PEM_ENV = process.env.CASPER_SECRET_KEY_PEM;
const SECRET_KEY_PATH = process.env.CASPER_SECRET_KEY_PATH
  ? path.resolve(process.env.CASPER_SECRET_KEY_PATH)
  : path.join(__dirname, "keys", "secret_key.pem");

const CONTRACT_PACKAGE_HASH =
  process.env.CASPER_CONTRACT_PACKAGE_HASH ||
  "160ad02bc56d6ec6b034139281bce4dee1757d69fdfdf69b81706fef66ccc260";

const PAYMENT_AMOUNT = 50_000_000_000; // 50 CSPR
const PAYMENT_AMOUNT_CSPR = PAYMENT_AMOUNT / 1_000_000_000;
const MIN_BALANCE_BUFFER_CSPR = PAYMENT_AMOUNT_CSPR * 2;

// Shared API key for simple auth between the Python backend and this
// service, since this endpoint signs and spends real (testnet) funds and
// should not be left open to the public internet.
const BRIDGE_API_KEY = process.env.CASPER_BRIDGE_API_KEY;

function loadPrivateKey() {
  const pemContent = SECRET_KEY_PEM_ENV
    ? SECRET_KEY_PEM_ENV.replace(/\\n/g, "\n") // App Settings often escape newlines
    : fs.readFileSync(SECRET_KEY_PATH, "utf8");
  return PrivateKey.fromPem(pemContent, KeyAlgorithm.SECP256K1);
}

function categorizeError(err) {
  const message = err.message || String(err);
  if (
    message.includes("ECONNREFUSED") ||
    message.includes("ETIMEDOUT") ||
    message.includes("ENOTFOUND") ||
    message.includes("fetch failed") ||
    message.includes("network")
  ) {
    return "network_unreachable";
  }
  if (message.toLowerCase().includes("out of gas")) return "out_of_gas";
  if (message.toLowerCase().includes("insufficient")) return "insufficient_balance";
  return "unknown";
}

app.get("/health", (req, res) => {
  res.json({ status: "ok", service: "forge-casper-bridge" });
});

app.post("/record-certification", async (req, res) => {
  // Simple shared-secret auth check
  if (BRIDGE_API_KEY) {
    const providedKey = req.headers["x-bridge-api-key"];
    if (providedKey !== BRIDGE_API_KEY) {
      return res.status(401).json({ success: false, error: "Invalid or missing bridge API key" });
    }
  }

  const { datasetHash, score, tier } = req.body || {};
  if (!datasetHash || score === undefined || !tier) {
    return res.status(400).json({
      success: false,
      error: "Request body must include datasetHash, score, and tier",
    });
  }

  const timestamp = Math.floor(Date.now() / 1000);

  try {
    const privateKey = loadPrivateKey();

    // Pre-flight balance check, same logic as the local subprocess version.
    const rpcClientForBalance = new RpcClient(new HttpHandler(NODE_RPC_URL));
    try {
      const balanceResult = await rpcClientForBalance.queryLatestBalance(
        PurseIdentifier.fromPublicKey(privateKey.publicKey)
      );
      const balanceCspr = Number(BigInt(balanceResult.balance.toString())) / 1_000_000_000;

      if (balanceCspr < MIN_BALANCE_BUFFER_CSPR) {
        const msg =
          `Insufficient testnet CSPR balance (${balanceCspr.toFixed(2)} CSPR) to safely complete this ` +
          `on-chain call. Testnet CSPR cannot be re-requested from the faucet for this account.`;
        return res.json({ success: false, error: msg, errorCategory: "insufficient_balance", lowBalance: true });
      }
    } catch (balanceErr) {
      // Non-fatal -- log and continue, same as the subprocess version.
      console.error("Balance pre-check failed (continuing anyway):", balanceErr.message || balanceErr);
    }

    const runtimeArgs = Args.fromMap({
      dataset_hash: CLValue.newCLString(String(datasetHash)),
      score: CLValue.newCLUInt32(parseInt(score, 10)),
      tier: CLValue.newCLString(String(tier)),
      timestamp: CLValue.newCLUint64(timestamp),
    });

    const transaction = new ContractCallBuilder()
      .byPackageHash(CONTRACT_PACKAGE_HASH)
      .entryPoint("record_certification")
      .runtimeArgs(runtimeArgs)
      .from(privateKey.publicKey)
      .chainName(CHAIN_NAME)
      .payment(PAYMENT_AMOUNT)
      .build();

    transaction.sign(privateKey);

    const rpcClient = new RpcClient(new HttpHandler(NODE_RPC_URL));
    await rpcClient.putTransaction(transaction);

    const txHash = transaction.hash.toHex();
    const confirmed = await rpcClient.waitForTransaction(transaction, 180_000);

    const execResult =
      confirmed?.executionInfo?.executionResult?.Version2 ||
      confirmed?.execution_info?.execution_result?.Version2;
    const errorMessage = execResult?.error_message ?? execResult?.errorMessage ?? null;

    if (errorMessage) {
      return res.json({ success: false, error: errorMessage, txHash });
    }

    return res.json({
      success: true,
      txHash: txHash,
      explorerUrl: `https://testnet.cspr.live/transaction/${txHash}`,
    });
  } catch (err) {
    console.error("=== record-certification FAILED ===", err);
    return res.json({
      success: false,
      error: err.message || String(err),
      errorCategory: categorizeError(err),
    });
  }
});

app.listen(PORT, () => {
  console.log(`FORGE Casper bridge listening on port ${PORT}`);
});
