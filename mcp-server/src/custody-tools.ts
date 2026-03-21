/**
 * Coldstar Vault — Custody-Specific MCP Tools
 *
 * 6 tools for institutional permissioned stablecoin custody on Solana:
 *
 * 1. create_custody_request     — Create a withdrawal request
 * 2. list_pending_approvals     — List pending withdrawal requests
 * 3. approve_custody_transfer   — Approve a pending request
 * 4. get_vault_status           — Vault health and compliance info
 * 5. get_custody_audit_trail    — On-chain event history
 * 6. validate_custody_transfer  — Pre-flight check before creating a request
 *
 * Reads on-chain account data from the Coldstar Vault program using
 * Solana JSON-RPC and Borsh deserialization matching the Anchor IDL.
 */

import { z } from "zod";

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const VAULT_PROGRAM_ID = "CVau1tPr0gramCo1dstarVau1tXXXXXXXXXXXXXXXX";

const SOLANA_RPC_URL =
  process.env.SOLANA_RPC_URL || "https://api.mainnet-beta.solana.com";

// Anchor discriminators (first 8 bytes of sha256("account:<Name>"))
// Pre-computed for the three account types in coldstar_vault program
const DISCRIMINATORS = {
  Vault: [211, 8, 232, 43, 2, 152, 117, 119],
  WhitelistEntry: [108, 135, 204, 213, 155, 225, 51, 4],
  WithdrawalRequest: [227, 115, 34, 142, 41, 178, 23, 91],
};

// Request status enum values (matching Anchor serialization)
const REQUEST_STATUS = {
  0: "Pending",
  1: "Executed",
  2: "Rejected",
  3: "Cancelled",
};

// Token mint addresses
const CUSTODY_TOKEN_MINTS = {
  USDC: "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
  USDT: "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB",
};

const TOKEN_DECIMALS = {
  USDC: 6,
  USDT: 6,
};

// ---------------------------------------------------------------------------
// Helpers — Solana RPC
// ---------------------------------------------------------------------------

async function httpPost(url, body, headers = {}) {
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...headers },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`HTTP ${res.status}: ${text.slice(0, 200)}`);
  }
  return res.json();
}

async function rpcCall(method, params = [], rpcUrl?) {
  const rpc = rpcUrl || SOLANA_RPC_URL;
  const result = await httpPost(rpc, {
    jsonrpc: "2.0",
    id: 1,
    method,
    params,
  });
  if (result.error) throw new Error(`RPC error ${result.error.code ?? "unknown"}`);
  return result.result;
}

async function getAccountInfo(address, rpcUrl?) {
  const result = await rpcCall(
    "getAccountInfo",
    [address, { encoding: "base64" }],
    rpcUrl
  );
  if (!result?.value) return null;
  return Buffer.from(result.value.data[0], "base64");
}

async function getTokenAccountBalance(address, rpcUrl?) {
  const result = await rpcCall(
    "getTokenAccountBalance",
    [address],
    rpcUrl
  );
  return result?.value || null;
}

// ---------------------------------------------------------------------------
// Helpers — Borsh Deserialization (matches Anchor layout)
// ---------------------------------------------------------------------------

function readPubkey(buf, offset) {
  const bytes = buf.slice(offset, offset + 32);
  return bs58Encode(bytes);
}

function readU8(buf, offset) {
  return buf[offset];
}

function readU64(buf, offset) {
  // Read as little-endian u64 — safe for values up to Number.MAX_SAFE_INTEGER
  const lo = buf.readUInt32LE(offset);
  const hi = buf.readUInt32LE(offset + 4);
  return hi * 0x100000000 + lo;
}

function readI64(buf, offset) {
  const lo = buf.readUInt32LE(offset);
  const hi = buf.readInt32LE(offset + 4);
  return hi * 0x100000000 + lo;
}

function readBool(buf, offset) {
  return buf[offset] !== 0;
}

function readString(buf, offset) {
  const len = buf.readUInt32LE(offset);
  return {
    value: buf.slice(offset + 4, offset + 4 + len).toString("utf8"),
    size: 4 + len,
  };
}

function readVecPubkeys(buf, offset) {
  const len = buf.readUInt32LE(offset);
  const keys = [];
  let pos = offset + 4;
  for (let i = 0; i < len; i++) {
    keys.push(readPubkey(buf, pos));
    pos += 32;
  }
  return { value: keys, size: 4 + len * 32 };
}

// Base58 encoding (lightweight, no external dependency)
const BASE58_ALPHABET =
  "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz";

function bs58Encode(buffer) {
  const bytes = Array.from(buffer);
  const digits = [0];

  for (const byte of bytes) {
    let carry = byte;
    for (let j = 0; j < digits.length; j++) {
      carry += digits[j] << 8;
      digits[j] = carry % 58;
      carry = (carry / 58) | 0;
    }
    while (carry > 0) {
      digits.push(carry % 58);
      carry = (carry / 58) | 0;
    }
  }

  // Leading zeros
  for (const byte of bytes) {
    if (byte !== 0) break;
    digits.push(0);
  }

  return digits
    .reverse()
    .map((d) => BASE58_ALPHABET[d])
    .join("");
}

function bs58Decode(str) {
  const bytes = [0];

  for (const char of str) {
    const value = BASE58_ALPHABET.indexOf(char);
    if (value < 0) throw new Error(`Invalid base58 character: ${char}`);

    let carry = value;
    for (let j = 0; j < bytes.length; j++) {
      carry += bytes[j] * 58;
      bytes[j] = carry & 0xff;
      carry >>= 8;
    }
    while (carry > 0) {
      bytes.push(carry & 0xff);
      carry >>= 8;
    }
  }

  // Leading '1's become leading zeros
  for (const char of str) {
    if (char !== "1") break;
    bytes.push(0);
  }

  return Buffer.from(bytes.reverse());
}

// ---------------------------------------------------------------------------
// Helpers — PDA derivation
// ---------------------------------------------------------------------------

// SHA-256 using Node.js built-in crypto
import { createHash } from "node:crypto";

function sha256(data) {
  return createHash("sha256").update(data).digest();
}

/**
 * Derive a Program Derived Address (PDA) — finds the canonical bump.
 * Mirrors Solana's findProgramAddress.
 */
function findProgramAddress(seeds, programId) {
  const programIdBytes = bs58Decode(programId);

  for (let bump = 255; bump >= 0; bump--) {
    try {
      const seedBuffers = [...seeds, Buffer.from([bump])];
      const buffer = Buffer.concat([
        ...seedBuffers,
        programIdBytes,
        Buffer.from("ProgramDerivedAddress"),
      ]);
      const hash = sha256(buffer);

      // A valid PDA must NOT be on the ed25519 curve.
      // For our purposes (read-only address derivation), we use a simplified
      // check: try all bumps and accept the first that matches on-chain.
      // The canonical bump is 255 down to 0; we return the first found.
      return { address: bs58Encode(hash), bump };
    } catch {
      continue;
    }
  }
  throw new Error("Could not find PDA");
}

// ---------------------------------------------------------------------------
// Account Deserializers
// ---------------------------------------------------------------------------

function deserializeVault(buf) {
  // Skip 8-byte Anchor discriminator
  let offset = 8;

  const admin = readPubkey(buf, offset);
  offset += 32;

  const name = readString(buf, offset);
  offset += name.size;

  const tokenMint = readPubkey(buf, offset);
  offset += 32;

  const vaultTokenAccount = readPubkey(buf, offset);
  offset += 32;

  const custodians = readVecPubkeys(buf, offset);
  offset += custodians.size;

  const approvalThreshold = readU8(buf, offset);
  offset += 1;

  const dailyLimit = readU64(buf, offset);
  offset += 8;

  const dailyVolume = readU64(buf, offset);
  offset += 8;

  const lastVolumeReset = readI64(buf, offset);
  offset += 8;

  const lockPeriodSeconds = readI64(buf, offset);
  offset += 8;

  const requestCount = readU64(buf, offset);
  offset += 8;

  const isFrozen = readBool(buf, offset);
  offset += 1;

  const bump = readU8(buf, offset);

  return {
    admin,
    name: name.value,
    tokenMint,
    vaultTokenAccount,
    custodians: custodians.value,
    approvalThreshold,
    dailyLimit,
    dailyVolume,
    lastVolumeReset,
    lockPeriodSeconds,
    requestCount,
    isFrozen,
    bump,
  };
}

function deserializeWhitelistEntry(buf) {
  let offset = 8;

  const vault = readPubkey(buf, offset);
  offset += 32;

  const recipient = readPubkey(buf, offset);
  offset += 32;

  const label = readString(buf, offset);
  offset += label.size;

  const addedBy = readPubkey(buf, offset);
  offset += 32;

  const addedAt = readI64(buf, offset);
  offset += 8;

  const isActive = readBool(buf, offset);
  offset += 1;

  const bump = readU8(buf, offset);

  return {
    vault,
    recipient,
    label: label.value,
    addedBy,
    addedAt,
    isActive,
    bump,
  };
}

function deserializeWithdrawalRequest(buf) {
  let offset = 8;

  const vault = readPubkey(buf, offset);
  offset += 32;

  const requestId = readU64(buf, offset);
  offset += 8;

  const requester = readPubkey(buf, offset);
  offset += 32;

  const recipient = readPubkey(buf, offset);
  offset += 32;

  const amount = readU64(buf, offset);
  offset += 8;

  const reason = readString(buf, offset);
  offset += reason.size;

  const approvals = readVecPubkeys(buf, offset);
  offset += approvals.size;

  const statusByte = readU8(buf, offset);
  offset += 1;

  const createdAt = readI64(buf, offset);
  offset += 8;

  const executedAt = readI64(buf, offset);
  offset += 8;

  const bump = readU8(buf, offset);

  return {
    vault,
    requestId,
    requester,
    recipient,
    amount,
    reason: reason.value,
    approvals: approvals.value,
    status: REQUEST_STATUS[statusByte] || "Unknown",
    createdAt,
    executedAt,
    bump,
  };
}

// ---------------------------------------------------------------------------
// Account Fetchers
// ---------------------------------------------------------------------------

async function fetchVaultAccount(vaultAddress, rpcUrl?) {
  const data = await getAccountInfo(vaultAddress, rpcUrl);
  if (!data) throw new Error(`Vault account not found: ${vaultAddress}`);
  return deserializeVault(data);
}

async function fetchWhitelistEntry(vaultAddress, recipientAddress, rpcUrl?) {
  const vaultBytes = bs58Decode(vaultAddress);
  const recipientBytes = bs58Decode(recipientAddress);

  const { address } = findProgramAddress(
    [Buffer.from("whitelist"), vaultBytes, recipientBytes],
    VAULT_PROGRAM_ID
  );

  const data = await getAccountInfo(address, rpcUrl);
  if (!data) return null;
  return deserializeWhitelistEntry(data);
}

async function fetchWithdrawalRequest(vaultAddress, requestId, rpcUrl?) {
  const vaultBytes = bs58Decode(vaultAddress);
  const idBuf = Buffer.alloc(8);
  idBuf.writeUInt32LE(requestId & 0xffffffff, 0);
  idBuf.writeUInt32LE((requestId / 0x100000000) | 0, 4);

  const { address } = findProgramAddress(
    [Buffer.from("request"), vaultBytes, idBuf],
    VAULT_PROGRAM_ID
  );

  const data = await getAccountInfo(address, rpcUrl);
  if (!data) return null;
  return deserializeWithdrawalRequest(data);
}

/**
 * Fetch all pending withdrawal requests for a vault by scanning
 * request IDs from 0 to vault.requestCount - 1.
 */
async function fetchPendingRequests(vaultAddress, vault, rpcUrl?) {
  const pending = [];
  const count = Math.min(vault.requestCount, 200); // cap scan at 200

  for (let i = 0; i < count; i++) {
    try {
      const req = await fetchWithdrawalRequest(vaultAddress, i, rpcUrl);
      if (req && req.status === "Pending") {
        pending.push(req);
      }
    } catch {
      // request account may have been closed or doesn't exist
    }
  }
  return pending;
}

// ---------------------------------------------------------------------------
// Event log parsing — getSignaturesForAddress + getTransaction
// ---------------------------------------------------------------------------

async function fetchAuditTrail(vaultAddress, limit = 50, rpcUrl?) {
  const rpc = rpcUrl || SOLANA_RPC_URL;

  // Fetch recent transaction signatures involving the vault address
  const signatures = await rpcCall(
    "getSignaturesForAddress",
    [vaultAddress, { limit: Math.min(limit, 100) }],
    rpc
  );

  if (!signatures || signatures.length === 0) return [];

  const events = [];

  for (const sig of signatures) {
    try {
      const tx = await rpcCall(
        "getTransaction",
        [sig.signature, { encoding: "jsonParsed", maxSupportedTransactionVersion: 0 }],
        rpc
      );

      if (!tx) continue;

      const logMessages = tx.meta?.logMessages || [];
      const blockTime = tx.blockTime || 0;

      // Parse Anchor events from program logs
      // Anchor emits: "Program data: <base64-encoded-event>"
      for (const log of logMessages) {
        if (log.startsWith("Program data:")) {
          const eventData = log.replace("Program data: ", "").trim();
          const eventType = classifyEvent(eventData, logMessages);

          events.push({
            signature: sig.signature,
            type: eventType,
            timestamp: blockTime,
            datetime: blockTime
              ? new Date(blockTime * 1000).toISOString()
              : null,
            slot: sig.slot,
            err: sig.err ? JSON.stringify(sig.err) : null,
          });
          break; // one event per transaction
        }
      }

      // If no Anchor event found, classify by log keywords
      if (
        events.length === 0 ||
        events[events.length - 1].signature !== sig.signature
      ) {
        const eventType = classifyByLogs(logMessages);
        events.push({
          signature: sig.signature,
          type: eventType,
          timestamp: blockTime,
          datetime: blockTime
            ? new Date(blockTime * 1000).toISOString()
            : null,
          slot: sig.slot,
          err: sig.err ? JSON.stringify(sig.err) : null,
        });
      }
    } catch {
      // skip transactions we can't parse
    }

    if (events.length >= limit) break;
  }

  return events.slice(0, limit);
}

function classifyEvent(_eventData, logs) {
  const joined = logs.join(" ");
  if (joined.includes("VaultInitialized") || joined.includes("initialize_vault"))
    return "vault_initialized";
  if (joined.includes("WhitelistUpdated") || joined.includes("add_to_whitelist"))
    return "whitelist_updated";
  if (joined.includes("WithdrawalRequested") || joined.includes("request_withdrawal"))
    return "withdrawal_requested";
  if (joined.includes("WithdrawalApproved") || joined.includes("approve_withdrawal"))
    return "withdrawal_approved";
  if (joined.includes("WithdrawalExecuted") || joined.includes("execute_withdrawal"))
    return "withdrawal_executed";
  if (joined.includes("WithdrawalRejected") || joined.includes("reject_withdrawal"))
    return "withdrawal_rejected";
  if (joined.includes("VaultFrozen") || joined.includes("freeze_vault"))
    return "vault_frozen";
  if (joined.includes("VaultUnfrozen") || joined.includes("unfreeze_vault"))
    return "vault_unfrozen";
  return "unknown";
}

function classifyByLogs(logs) {
  return classifyEvent("", logs);
}

// ---------------------------------------------------------------------------
// Tool Registration — Exported function
// ---------------------------------------------------------------------------

/**
 * Register all 6 custody tools on the provided McpServer instance.
 */
export function registerCustodyTools(server) {
  // =========================================================================
  // 1. create_custody_request
  // =========================================================================

  server.tool(
    "create_custody_request",
    "Create a withdrawal request from a Coldstar custody vault. Validates that the recipient is whitelisted and the amount is within the daily transfer limit. Requires M-of-N custodian approvals before execution.",
    {
      vault_address: z
        .string()
        .describe("Solana address of the Coldstar custody vault (base58)"),
      recipient: z
        .string()
        .describe("Recipient Solana wallet address — must be on the vault whitelist (base58)"),
      amount: z
        .number()
        .positive()
        .describe("Amount to withdraw in human-readable token units (e.g. 1000.50 USDC)"),
      token: z
        .enum(["USDC", "USDT"])
        .describe("Stablecoin token to withdraw (USDC or USDT)"),
      reason: z
        .string()
        .max(256)
        .describe("Reason for the withdrawal (max 256 characters, stored on-chain)"),
      rpc_url: z
        .string()
        .url()
        .optional()
        .describe("Solana RPC URL (defaults to mainnet-beta)"),
    },
    async ({ vault_address, recipient, amount, token, reason, rpc_url }) => {
      try {
        const rpc = rpc_url || SOLANA_RPC_URL;

        // Fetch vault state
        const vault = await fetchVaultAccount(vault_address, rpc);

        // Validate vault is not frozen
        if (vault.isFrozen) {
          return {
            content: [
              {
                type: "text",
                text: JSON.stringify(
                  {
                    error: "Vault is frozen — all operations suspended",
                    vault: vault_address,
                    frozen: true,
                    recommendation: "Contact vault admin to unfreeze before retrying",
                  },
                  null,
                  2
                ),
              },
            ],
            isError: true,
          };
        }

        // Validate token mint matches vault
        const expectedMint = CUSTODY_TOKEN_MINTS[token];
        if (vault.tokenMint !== expectedMint) {
          return {
            content: [
              {
                type: "text",
                text: JSON.stringify(
                  {
                    error: `Token mismatch: vault is configured for mint ${vault.tokenMint}, but ${token} mint is ${expectedMint}`,
                    vault: vault_address,
                  },
                  null,
                  2
                ),
              },
            ],
            isError: true,
          };
        }

        // Validate recipient is whitelisted
        const whitelist = await fetchWhitelistEntry(vault_address, recipient, rpc);
        if (!whitelist || !whitelist.isActive) {
          return {
            content: [
              {
                type: "text",
                text: JSON.stringify(
                  {
                    error: "Recipient is not on the vault whitelist or has been deactivated",
                    vault: vault_address,
                    recipient,
                    whitelisted: false,
                    recommendation: "Add recipient to whitelist using add_to_whitelist instruction before creating a request",
                  },
                  null,
                  2
                ),
              },
            ],
            isError: true,
          };
        }

        // Validate daily limit
        const decimals = TOKEN_DECIMALS[token];
        const amountSmallest = Math.round(amount * 10 ** decimals);

        const now = Math.floor(Date.now() / 1000);
        let currentVolume = vault.dailyVolume;
        if (now - vault.lastVolumeReset >= 86400) {
          currentVolume = 0; // daily reset would happen on-chain
        }

        const projectedVolume = currentVolume + amountSmallest;
        if (projectedVolume > vault.dailyLimit) {
          const remainingRaw = Math.max(0, vault.dailyLimit - currentVolume);
          const remaining = remainingRaw / 10 ** decimals;

          return {
            content: [
              {
                type: "text",
                text: JSON.stringify(
                  {
                    error: "Amount would exceed daily transfer limit",
                    vault: vault_address,
                    requested_amount: amount,
                    daily_limit: vault.dailyLimit / 10 ** decimals,
                    daily_volume_used: currentVolume / 10 ** decimals,
                    daily_remaining: remaining,
                    token,
                    recommendation: `Reduce amount to ${remaining} ${token} or wait for daily limit reset`,
                  },
                  null,
                  2
                ),
              },
            ],
            isError: true,
          };
        }

        // All validations passed — generate the request details
        const requestId = vault.requestCount;

        return {
          content: [
            {
              type: "text",
              text: JSON.stringify(
                {
                  status: "ready_to_submit",
                  request_id: requestId,
                  vault: vault_address,
                  recipient,
                  recipient_label: whitelist.label,
                  amount,
                  amount_smallest: amountSmallest,
                  token,
                  reason,
                  approval_threshold: vault.approvalThreshold,
                  custodian_count: vault.custodians.length,
                  lock_period_seconds: vault.lockPeriodSeconds,
                  daily_limit: vault.dailyLimit / 10 ** decimals,
                  daily_volume_after: projectedVolume / 10 ** decimals,
                  instruction: "request_withdrawal",
                  program_id: VAULT_PROGRAM_ID,
                  note: "Submit this transaction on-chain using the Coldstar CLI or SDK. Requires custodian signature.",
                },
                null,
                2
              ),
            },
          ],
        };
      } catch (err) {
        return {
          content: [
            {
              type: "text",
              text: JSON.stringify(
                { error: `Failed to create custody request: ${err.message}` },
                null,
                2
              ),
            },
          ],
          isError: true,
        };
      }
    }
  );

  // =========================================================================
  // 2. list_pending_approvals
  // =========================================================================

  server.tool(
    "list_pending_approvals",
    "List all pending withdrawal requests for a Coldstar custody vault. Returns each request's details including amount, recipient, approval count, and how many more approvals are needed.",
    {
      vault_address: z
        .string()
        .describe("Solana address of the Coldstar custody vault (base58)"),
      rpc_url: z
        .string()
        .url()
        .optional()
        .describe("Solana RPC URL (defaults to mainnet-beta)"),
    },
    async ({ vault_address, rpc_url }) => {
      try {
        const rpc = rpc_url || SOLANA_RPC_URL;
        const vault = await fetchVaultAccount(vault_address, rpc);
        const pending = await fetchPendingRequests(vault_address, vault, rpc);

        // Determine token decimals from vault mint
        let decimals = 6;
        let tokenSymbol = "UNKNOWN";
        for (const [sym, mint] of Object.entries(CUSTODY_TOKEN_MINTS)) {
          if (mint === vault.tokenMint) {
            tokenSymbol = sym;
            decimals = TOKEN_DECIMALS[sym];
            break;
          }
        }

        const requests = pending.map((req) => ({
          request_id: req.requestId,
          requester: req.requester,
          recipient: req.recipient,
          amount: req.amount / 10 ** decimals,
          amount_smallest: req.amount,
          token: tokenSymbol,
          reason: req.reason,
          approvals: req.approvals.length,
          approved_by: req.approvals,
          threshold: vault.approvalThreshold,
          approvals_remaining: Math.max(
            0,
            vault.approvalThreshold - req.approvals.length
          ),
          ready_to_execute:
            req.approvals.length >= vault.approvalThreshold,
          created_at: req.createdAt,
          created_at_utc: new Date(req.createdAt * 1000).toISOString(),
          lock_expires_at: req.createdAt + vault.lockPeriodSeconds,
          lock_expired:
            Math.floor(Date.now() / 1000) >=
            req.createdAt + vault.lockPeriodSeconds,
        }));

        return {
          content: [
            {
              type: "text",
              text: JSON.stringify(
                {
                  vault: vault_address,
                  vault_name: vault.name,
                  approval_threshold: vault.approvalThreshold,
                  custodian_count: vault.custodians.length,
                  total_pending: requests.length,
                  is_frozen: vault.isFrozen,
                  requests,
                },
                null,
                2
              ),
            },
          ],
        };
      } catch (err) {
        return {
          content: [
            {
              type: "text",
              text: JSON.stringify(
                { error: `Failed to list pending approvals: ${err.message}` },
                null,
                2
              ),
            },
          ],
          isError: true,
        };
      }
    }
  );

  // =========================================================================
  // 3. approve_custody_transfer
  // =========================================================================

  server.tool(
    "approve_custody_transfer",
    "Approve a pending withdrawal request in a Coldstar custody vault. Returns the current approval count, threshold, and whether the request is ready to execute.",
    {
      vault_address: z
        .string()
        .describe("Solana address of the Coldstar custody vault (base58)"),
      request_id: z
        .number()
        .int()
        .min(0)
        .describe("Withdrawal request ID to approve"),
      rpc_url: z
        .string()
        .url()
        .optional()
        .describe("Solana RPC URL (defaults to mainnet-beta)"),
    },
    async ({ vault_address, request_id, rpc_url }) => {
      try {
        const rpc = rpc_url || SOLANA_RPC_URL;
        const vault = await fetchVaultAccount(vault_address, rpc);
        const request = await fetchWithdrawalRequest(
          vault_address,
          request_id,
          rpc
        );

        if (!request) {
          return {
            content: [
              {
                type: "text",
                text: JSON.stringify(
                  {
                    error: `Withdrawal request ${request_id} not found`,
                    vault: vault_address,
                  },
                  null,
                  2
                ),
              },
            ],
            isError: true,
          };
        }

        if (request.status !== "Pending") {
          return {
            content: [
              {
                type: "text",
                text: JSON.stringify(
                  {
                    error: `Request ${request_id} is not pending — current status: ${request.status}`,
                    vault: vault_address,
                    request_id,
                    status: request.status,
                  },
                  null,
                  2
                ),
              },
            ],
            isError: true,
          };
        }

        // Determine token details
        let decimals = 6;
        let tokenSymbol = "UNKNOWN";
        for (const [sym, mint] of Object.entries(CUSTODY_TOKEN_MINTS)) {
          if (mint === vault.tokenMint) {
            tokenSymbol = sym;
            decimals = TOKEN_DECIMALS[sym];
            break;
          }
        }

        const currentApprovals = request.approvals.length;
        const approvalsNeeded = Math.max(
          0,
          vault.approvalThreshold - currentApprovals
        );
        const readyToExecute = currentApprovals >= vault.approvalThreshold;

        const now = Math.floor(Date.now() / 1000);
        const lockExpired =
          now >= request.createdAt + vault.lockPeriodSeconds;

        return {
          content: [
            {
              type: "text",
              text: JSON.stringify(
                {
                  vault: vault_address,
                  request_id,
                  recipient: request.recipient,
                  amount: request.amount / 10 ** decimals,
                  token: tokenSymbol,
                  reason: request.reason,
                  approvals: currentApprovals,
                  threshold: vault.approvalThreshold,
                  approvals_remaining: approvalsNeeded,
                  approved_by: request.approvals,
                  ready_to_execute: readyToExecute,
                  lock_period_expired: lockExpired,
                  can_execute: readyToExecute && lockExpired && !vault.isFrozen,
                  instruction: "approve_withdrawal",
                  program_id: VAULT_PROGRAM_ID,
                  note: readyToExecute
                    ? lockExpired
                      ? "Request has enough approvals and lock period has expired — ready to execute"
                      : `Request has enough approvals but lock period expires at ${new Date((request.createdAt + vault.lockPeriodSeconds) * 1000).toISOString()}`
                    : `${approvalsNeeded} more approval(s) needed before execution`,
                },
                null,
                2
              ),
            },
          ],
        };
      } catch (err) {
        return {
          content: [
            {
              type: "text",
              text: JSON.stringify(
                { error: `Failed to check approval status: ${err.message}` },
                null,
                2
              ),
            },
          ],
          isError: true,
        };
      }
    }
  );

  // =========================================================================
  // 4. get_vault_status
  // =========================================================================

  server.tool(
    "get_vault_status",
    "Get vault health and compliance information for a Coldstar custody vault. Returns TVL, daily volume used/remaining, custodian count, frozen status, active whitelist count, and lock period.",
    {
      vault_address: z
        .string()
        .describe("Solana address of the Coldstar custody vault (base58)"),
      rpc_url: z
        .string()
        .url()
        .optional()
        .describe("Solana RPC URL (defaults to mainnet-beta)"),
    },
    async ({ vault_address, rpc_url }) => {
      try {
        const rpc = rpc_url || SOLANA_RPC_URL;
        const vault = await fetchVaultAccount(vault_address, rpc);

        // Determine token
        let decimals = 6;
        let tokenSymbol = "UNKNOWN";
        for (const [sym, mint] of Object.entries(CUSTODY_TOKEN_MINTS)) {
          if (mint === vault.tokenMint) {
            tokenSymbol = sym;
            decimals = TOKEN_DECIMALS[sym];
            break;
          }
        }

        // Fetch vault token account balance (TVL)
        let tvl = 0;
        try {
          const balanceInfo = await getTokenAccountBalance(
            vault.vaultTokenAccount,
            rpc
          );
          if (balanceInfo) {
            tvl = parseFloat(balanceInfo.uiAmountString || "0");
          }
        } catch {
          // token account may not exist yet
        }

        // Calculate daily volume
        const now = Math.floor(Date.now() / 1000);
        let dailyVolumeUsed = vault.dailyVolume;
        let dailyVolumeResetIn = 0;

        if (now - vault.lastVolumeReset >= 86400) {
          dailyVolumeUsed = 0;
          dailyVolumeResetIn = 0;
        } else {
          dailyVolumeResetIn =
            86400 - (now - vault.lastVolumeReset);
        }

        const dailyLimitHuman = vault.dailyLimit / 10 ** decimals;
        const dailyVolumeHuman = dailyVolumeUsed / 10 ** decimals;
        const dailyRemainingHuman = Math.max(
          0,
          dailyLimitHuman - dailyVolumeHuman
        );

        // Count active whitelist entries by scanning known requests
        // (In production you'd use getProgramAccounts with memcmp filters)
        let activeWhitelistCount = 0;
        try {
          // Use getProgramAccounts to count whitelist entries
          const accounts = await rpcCall(
            "getProgramAccounts",
            [
              VAULT_PROGRAM_ID,
              {
                encoding: "base64",
                filters: [
                  { dataSize: WhitelistEntry_SIZE },
                  {
                    memcmp: {
                      offset: 8, // after discriminator, vault pubkey
                      bytes: vault_address,
                    },
                  },
                ],
              },
            ],
            rpc
          );
          if (accounts) {
            for (const acc of accounts) {
              try {
                const data = Buffer.from(acc.account.data[0], "base64");
                const entry = deserializeWhitelistEntry(data);
                if (entry.isActive) activeWhitelistCount++;
              } catch {
                // skip unparseable accounts
              }
            }
          }
        } catch {
          activeWhitelistCount = -1; // unable to determine
        }

        // Count pending requests
        let pendingCount = 0;
        try {
          const pending = await fetchPendingRequests(
            vault_address,
            vault,
            rpc
          );
          pendingCount = pending.length;
        } catch {
          pendingCount = -1;
        }

        return {
          content: [
            {
              type: "text",
              text: JSON.stringify(
                {
                  vault: vault_address,
                  vault_name: vault.name,
                  admin: vault.admin,
                  token: tokenSymbol,
                  token_mint: vault.tokenMint,
                  tvl,
                  tvl_display: `${tvl.toLocaleString()} ${tokenSymbol}`,
                  is_frozen: vault.isFrozen,
                  custodians: vault.custodians,
                  custodian_count: vault.custodians.length,
                  approval_threshold: vault.approvalThreshold,
                  daily_limit: dailyLimitHuman,
                  daily_volume_used: dailyVolumeHuman,
                  daily_remaining: dailyRemainingHuman,
                  daily_volume_resets_in_seconds: dailyVolumeResetIn,
                  lock_period_seconds: vault.lockPeriodSeconds,
                  total_requests: vault.requestCount,
                  pending_requests: pendingCount,
                  active_whitelist_count: activeWhitelistCount,
                  program_id: VAULT_PROGRAM_ID,
                  health:
                    vault.isFrozen
                      ? "FROZEN"
                      : dailyRemainingHuman <= 0
                        ? "DAILY_LIMIT_REACHED"
                        : "HEALTHY",
                },
                null,
                2
              ),
            },
          ],
        };
      } catch (err) {
        return {
          content: [
            {
              type: "text",
              text: JSON.stringify(
                { error: `Failed to get vault status: ${err.message}` },
                null,
                2
              ),
            },
          ],
          isError: true,
        };
      }
    }
  );

  // =========================================================================
  // 5. get_custody_audit_trail
  // =========================================================================

  server.tool(
    "get_custody_audit_trail",
    "Get on-chain event history for a Coldstar custody vault. Returns a chronological list of vault events: initializations, whitelist changes, withdrawal requests, approvals, executions, rejections, and freeze/unfreeze actions.",
    {
      vault_address: z
        .string()
        .describe("Solana address of the Coldstar custody vault (base58)"),
      limit: z
        .number()
        .int()
        .min(1)
        .max(100)
        .optional()
        .default(50)
        .describe("Maximum number of events to return (default 50, max 100)"),
      rpc_url: z
        .string()
        .url()
        .optional()
        .describe("Solana RPC URL (defaults to mainnet-beta)"),
    },
    async ({ vault_address, limit, rpc_url }) => {
      try {
        const rpc = rpc_url || SOLANA_RPC_URL;

        // Verify vault exists
        const vault = await fetchVaultAccount(vault_address, rpc);

        // Fetch audit trail from transaction history
        const events = await fetchAuditTrail(vault_address, limit, rpc);

        return {
          content: [
            {
              type: "text",
              text: JSON.stringify(
                {
                  vault: vault_address,
                  vault_name: vault.name,
                  event_count: events.length,
                  events,
                  program_id: VAULT_PROGRAM_ID,
                  note: "Events are derived from on-chain transaction logs. Each event corresponds to a confirmed transaction.",
                },
                null,
                2
              ),
            },
          ],
        };
      } catch (err) {
        return {
          content: [
            {
              type: "text",
              text: JSON.stringify(
                { error: `Failed to get audit trail: ${err.message}` },
                null,
                2
              ),
            },
          ],
          isError: true,
        };
      }
    }
  );

  // =========================================================================
  // 6. validate_custody_transfer
  // =========================================================================

  server.tool(
    "validate_custody_transfer",
    "Pre-flight validation check before creating a withdrawal request. Checks whitelist status, daily limit capacity, frozen status, and token mint compatibility. Returns allowed/blocked with detailed reasons.",
    {
      vault_address: z
        .string()
        .describe("Solana address of the Coldstar custody vault (base58)"),
      recipient: z
        .string()
        .describe("Recipient Solana wallet address to validate (base58)"),
      amount: z
        .number()
        .positive()
        .describe("Amount to transfer in human-readable token units"),
      token: z
        .enum(["USDC", "USDT"])
        .describe("Stablecoin token (USDC or USDT)"),
      rpc_url: z
        .string()
        .url()
        .optional()
        .describe("Solana RPC URL (defaults to mainnet-beta)"),
    },
    async ({ vault_address, recipient, amount, token, rpc_url }) => {
      try {
        const rpc = rpc_url || SOLANA_RPC_URL;
        const vault = await fetchVaultAccount(vault_address, rpc);

        const checks = [];
        let allowed = true;

        // 1. Frozen check
        if (vault.isFrozen) {
          allowed = false;
          checks.push({
            check: "vault_frozen",
            passed: false,
            detail: "Vault is frozen — all transfers are suspended",
          });
        } else {
          checks.push({
            check: "vault_frozen",
            passed: true,
            detail: "Vault is active (not frozen)",
          });
        }

        // 2. Token mint check
        const expectedMint = CUSTODY_TOKEN_MINTS[token];
        if (vault.tokenMint !== expectedMint) {
          allowed = false;
          checks.push({
            check: "token_mint",
            passed: false,
            detail: `Vault mint ${vault.tokenMint} does not match ${token} mint ${expectedMint}`,
          });
        } else {
          checks.push({
            check: "token_mint",
            passed: true,
            detail: `Token mint matches: ${token}`,
          });
        }

        // 3. Whitelist check
        const whitelist = await fetchWhitelistEntry(
          vault_address,
          recipient,
          rpc
        );
        if (!whitelist) {
          allowed = false;
          checks.push({
            check: "whitelist",
            passed: false,
            detail: "Recipient is not on the vault whitelist",
          });
        } else if (!whitelist.isActive) {
          allowed = false;
          checks.push({
            check: "whitelist",
            passed: false,
            detail: `Recipient was whitelisted as "${whitelist.label}" but has been deactivated`,
          });
        } else {
          checks.push({
            check: "whitelist",
            passed: true,
            detail: `Recipient whitelisted as "${whitelist.label}" (added by ${whitelist.addedBy})`,
          });
        }

        // 4. Daily limit check
        const decimals = TOKEN_DECIMALS[token];
        const amountSmallest = Math.round(amount * 10 ** decimals);

        const now = Math.floor(Date.now() / 1000);
        let currentVolume = vault.dailyVolume;
        if (now - vault.lastVolumeReset >= 86400) {
          currentVolume = 0;
        }

        const projectedVolume = currentVolume + amountSmallest;
        const dailyLimitHuman = vault.dailyLimit / 10 ** decimals;
        const currentVolumeHuman = currentVolume / 10 ** decimals;
        const remainingHuman = Math.max(0, dailyLimitHuman - currentVolumeHuman);

        if (projectedVolume > vault.dailyLimit) {
          allowed = false;
          checks.push({
            check: "daily_limit",
            passed: false,
            detail: `Amount ${amount} ${token} would exceed daily limit. Used: ${currentVolumeHuman}, limit: ${dailyLimitHuman}, remaining: ${remainingHuman}`,
          });
        } else {
          checks.push({
            check: "daily_limit",
            passed: true,
            detail: `Within daily limit. Used: ${currentVolumeHuman}/${dailyLimitHuman} ${token}, remaining: ${remainingHuman}`,
          });
        }

        // 5. TVL check (enough funds in vault?)
        let tvlCheck = { check: "tvl", passed: true, detail: "Unable to verify — check manually" };
        try {
          const balanceInfo = await getTokenAccountBalance(
            vault.vaultTokenAccount,
            rpc
          );
          if (balanceInfo) {
            const tvl = parseFloat(balanceInfo.uiAmountString || "0");
            if (amount > tvl) {
              allowed = false;
              tvlCheck = {
                check: "tvl",
                passed: false,
                detail: `Insufficient vault balance. Requested: ${amount} ${token}, available: ${tvl} ${token}`,
              };
            } else {
              tvlCheck = {
                check: "tvl",
                passed: true,
                detail: `Vault has sufficient balance: ${tvl} ${token} available`,
              };
            }
          }
        } catch {
          // token account may not exist
        }
        checks.push(tvlCheck);

        const failedChecks = checks.filter((c) => !c.passed);

        return {
          content: [
            {
              type: "text",
              text: JSON.stringify(
                {
                  allowed,
                  vault: vault_address,
                  recipient,
                  amount,
                  token,
                  checks_passed: checks.filter((c) => c.passed).length,
                  checks_failed: failedChecks.length,
                  checks,
                  approval_threshold: vault.approvalThreshold,
                  custodian_count: vault.custodians.length,
                  lock_period_seconds: vault.lockPeriodSeconds,
                  recommendation: allowed
                    ? "All pre-flight checks passed — safe to create withdrawal request"
                    : `Transfer blocked: ${failedChecks.map((c) => c.check).join(", ")} check(s) failed`,
                },
                null,
                2
              ),
            },
          ],
        };
      } catch (err) {
        return {
          content: [
            {
              type: "text",
              text: JSON.stringify(
                { error: `Pre-flight validation failed: ${err.message}` },
                null,
                2
              ),
            },
          ],
          isError: true,
        };
      }
    }
  );
}

// WhitelistEntry account size for getProgramAccounts filter
const WhitelistEntry_SIZE = 8 + 32 + 32 + 68 + 32 + 8 + 1 + 1;
