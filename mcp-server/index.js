#!/usr/bin/env node

/**
 * Coldstar MCP Server — Multichain
 *
 * Secure signing infrastructure for AI agents on Solana and Base.
 * FairScore reputation gating prevents rogue agents from draining wallets.
 *
 * Solana tools: check_reputation, get_token_price, get_swap_quote,
 *               check_wallet_balance, validate_transaction, list_supported_tokens,
 *               get_portfolio, estimate_swap_cost, solana_get_fees
 *
 * Base tools:   base_check_balance, base_get_gas_price, base_get_token_price,
 *               base_get_portfolio, base_list_tokens
 *
 * 14 tools total across both chains.
 */

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const FAIRSCORE_API_BASE =
  process.env.FAIRSCORE_API_URL || "https://api2.fairscale.xyz";
const FAIRSCORE_API_KEY = process.env.FAIRSCORE_API_KEY || "";

const SOLANA_RPC_URL =
  process.env.SOLANA_RPC_URL || "https://api.mainnet-beta.solana.com";

const PYTH_HERMES_API = "https://hermes.pyth.network";

const JUPITER_QUOTE_API = "https://lite-api.jup.ag/swap/v1/quote";

// Pyth price feed IDs (mainnet)
const PYTH_PRICE_FEEDS = {
  "SOL/USD":
    "0xef0d8b6fda2ceba41da15d4095d1da392a0d2f8ed0c6c7bc0f4cfac8c280b56d",
  "BTC/USD":
    "0xe62df6c8b4a85fe1a67db44dc12de5db330f7ac66b72dc658afedf0f4a415b43",
  "ETH/USD":
    "0xff61491a931112ddf1bd8147cd1b641375f79f5825126d665480874634fd0ace",
  "USDC/USD":
    "0xeaa020c61cc479712813461ce153894a96a6c00b21ed0cfc2798d1f9a9e9c94a",
  "USDT/USD":
    "0x2b89b9dc8fdf9f34709a5b106b472f0f39bb6ca9ce04b0fd7f2e971688e2e53b",
  "BONK/USD":
    "0x72b021217ca3fe68922a19aaf990109cb9d84e9ad004b4d2025ad6f529314419",
  "JUP/USD":
    "0x0a0408d619e9380abad35060f9192039ed5042fa6f82301d0e48bb52be830996",
  "RAY/USD":
    "0x91568baa8beb53db23eb3fb7f22c6e8b1a9f0e489b46d6a12411b49e8b60cd1e",
};

// Token mint addresses on Solana mainnet
const TOKEN_MINTS = {
  SOL: "So11111111111111111111111111111111111111112",
  USDC: "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
  USDT: "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB",
  BONK: "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263",
  JUP: "JUPyiwrYJFskUPiHa7hkeR8VUtAeFoSYbKedZNsDvCN",
  RAY: "4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R",
};

// Token decimals
const TOKEN_DECIMALS = {
  SOL: 9,
  USDC: 6,
  USDT: 6,
  BONK: 5,
  JUP: 6,
  RAY: 6,
};

// ---------------------------------------------------------------------------
// Base (EVM) Constants
// ---------------------------------------------------------------------------

const BASE_RPC_URL =
  process.env.BASE_RPC_URL || "https://mainnet.base.org";
const BASE_CHAIN_ID = 8453;

// Common Base token addresses (checksummed)
const BASE_TOKENS = {
  ETH: { address: "native", decimals: 18, name: "Ethereum" },
  WETH: {
    address: "0x4200000000000000000000000000000000000006",
    decimals: 18,
    name: "Wrapped Ether",
  },
  USDC: {
    address: "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
    decimals: 6,
    name: "USD Coin",
  },
  USDbC: {
    address: "0xd9aAEc86B65D86f6A7B5B1b0c42FFA531710b6CA",
    decimals: 6,
    name: "USD Base Coin (bridged)",
  },
  DAI: {
    address: "0x50c5725949A6F0c72E6C4a641F24049A917DB0Cb",
    decimals: 18,
    name: "Dai Stablecoin",
  },
  cbETH: {
    address: "0x2Ae3F1Ec7F1F5012CFEab0185bfc7aa3cf0DEc22",
    decimals: 18,
    name: "Coinbase Wrapped Staked ETH",
  },
  AERO: {
    address: "0x940181a94A35A4569E4529A3CDfB74e38FD98631",
    decimals: 18,
    name: "Aerodrome",
  },
};

// Reputation tiers
const TIER_THRESHOLDS = [
  { min: 0, max: 19, tier: "Bronze", action: "BLOCK", limit: 0 },
  { min: 20, max: 39, tier: "Silver", action: "WARN", limit: 10 },
  { min: 40, max: 59, tier: "Gold", action: "ALLOW", limit: 100 },
  { min: 60, max: 79, tier: "Platinum", action: "ALLOW", limit: 500 },
  { min: 80, max: 100, tier: "Diamond", action: "ALLOW", limit: Infinity },
];

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function scoreToDef(score) {
  for (const t of TIER_THRESHOLDS) {
    if (score >= t.min && score <= t.max) return t;
  }
  return TIER_THRESHOLDS[0];
}

function resolveMint(symbol) {
  const upper = symbol.toUpperCase();
  return TOKEN_MINTS[upper] || symbol; // pass-through if already a mint
}

function resolveDecimals(symbol) {
  const upper = symbol.toUpperCase();
  return TOKEN_DECIMALS[upper] || 9;
}

function normalizePythSymbol(symbol) {
  let s = symbol.toUpperCase();
  if (!s.endsWith("/USD")) s = `${s}/USD`;
  return s;
}

async function httpGet(url, headers = {}) {
  const res = await fetch(url, { headers });
  if (!res.ok) {
    const body = await res.text().catch(() => "");
    throw new Error(`HTTP ${res.status}: ${body.slice(0, 200)}`);
  }
  return res.json();
}

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

// ---------------------------------------------------------------------------
// API wrappers
// ---------------------------------------------------------------------------

async function fetchFairScore(walletAddress) {
  const headers = {};
  if (FAIRSCORE_API_KEY) headers.fairkey = FAIRSCORE_API_KEY;

  const url = `${FAIRSCORE_API_BASE}/score?wallet=${encodeURIComponent(walletAddress)}`;
  return httpGet(url, headers);
}

async function fetchPythPrice(symbol) {
  const key = normalizePythSymbol(symbol);
  const feedId = PYTH_PRICE_FEEDS[key];
  if (!feedId) throw new Error(`No Pyth feed for ${symbol}. Supported: ${Object.keys(PYTH_PRICE_FEEDS).join(", ")}`);

  const url = `${PYTH_HERMES_API}/api/latest_price_feeds?ids[]=${feedId}`;
  const data = await httpGet(url);

  if (!data || data.length === 0) throw new Error(`No price data for ${symbol}`);

  const feed = data[0];
  const priceObj = feed.price || {};
  const priceRaw = parseInt(priceObj.price || "0", 10);
  const expo = parseInt(priceObj.expo || "0", 10);
  const conf = parseInt(priceObj.conf || "0", 10);

  return {
    symbol: key,
    price: priceRaw * 10 ** expo,
    confidence: conf * 10 ** expo,
    publish_time: priceObj.publish_time || 0,
  };
}

async function fetchJupiterQuote(inputMint, outputMint, amountSmallest, slippageBps = 50) {
  const params = new URLSearchParams({
    inputMint,
    outputMint,
    amount: String(amountSmallest),
    slippageBps: String(slippageBps),
  });

  const url = `${JUPITER_QUOTE_API}?${params}`;
  return httpGet(url);
}

async function fetchSolBalance(walletAddress, rpcUrl) {
  const body = {
    jsonrpc: "2.0",
    id: 1,
    method: "getBalance",
    params: [walletAddress],
  };
  const result = await httpPost(rpcUrl, body);
  if (result.error) throw new Error(result.error.message);
  return (result.result?.value ?? 0) / 1e9;
}

async function fetchTokenAccounts(walletAddress, rpcUrl) {
  const body = {
    jsonrpc: "2.0",
    id: 1,
    method: "getTokenAccountsByOwner",
    params: [
      walletAddress,
      { programId: "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA" },
      { encoding: "jsonParsed" },
    ],
  };
  const result = await httpPost(rpcUrl, body);
  if (result.error) throw new Error(result.error.message);
  return result.result?.value ?? [];
}

// ---------------------------------------------------------------------------
// Base (EVM) API wrappers
// ---------------------------------------------------------------------------

async function baseRpcCall(method, params = [], rpcUrl) {
  const rpc = rpcUrl || BASE_RPC_URL;
  const body = { jsonrpc: "2.0", id: 1, method, params };
  const result = await httpPost(rpc, body);
  if (result.error) throw new Error(result.error.message);
  return result.result;
}

async function fetchBaseEthBalance(address, rpcUrl) {
  const hex = await baseRpcCall("eth_getBalance", [address, "latest"], rpcUrl);
  return parseInt(hex, 16) / 1e18;
}

async function fetchBaseTokenBalance(walletAddress, tokenAddress, decimals, rpcUrl) {
  // ERC-20 balanceOf(address) = 0x70a08231 + padded address
  const paddedAddr = walletAddress.slice(2).toLowerCase().padStart(64, "0");
  const data = `0x70a08231${paddedAddr}`;
  const hex = await baseRpcCall(
    "eth_call",
    [{ to: tokenAddress, data }, "latest"],
    rpcUrl
  );
  return parseInt(hex, 16) / 10 ** decimals;
}

async function fetchBaseGasPrice(rpcUrl) {
  const hex = await baseRpcCall("eth_gasPrice", [], rpcUrl);
  return parseInt(hex, 16);
}

async function fetchBaseBlockNumber(rpcUrl) {
  const hex = await baseRpcCall("eth_blockNumber", [], rpcUrl);
  return parseInt(hex, 16);
}

// ---------------------------------------------------------------------------
// Server
// ---------------------------------------------------------------------------

const server = new McpServer({
  name: "coldstar-mcp",
  version: "0.2.0",
});

// 1. check_reputation ---------------------------------------------------------

server.tool(
  "check_reputation",
  "Check FairScore reputation of any Solana wallet. Returns score (0-100), tier, badges, and transfer limit. This is the core guardrail that prevents AI agents from sending funds to scam wallets.",
  { wallet_address: z.string().describe("Solana wallet address (base58)") },
  async ({ wallet_address }) => {
    try {
      const data = await fetchFairScore(wallet_address);
      const score = data.fairscore ?? data.score ?? 0;
      const apiTier = (data.tier || "").toLowerCase();
      const def = scoreToDef(score);
      const badges = data.badges || [];

      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(
              {
                wallet: wallet_address,
                fairscore: score,
                tier: def.tier,
                api_tier: apiTier,
                action: def.action,
                transfer_limit_sol:
                  def.limit === Infinity ? "unlimited" : def.limit,
                badges: badges.map((b) =>
                  typeof b === "string" ? b : b.label || b.name || b
                ),
                description:
                  def.action === "BLOCK"
                    ? "High-risk wallet - transactions blocked"
                    : def.action === "WARN"
                      ? "Low-trust wallet - proceed with caution"
                      : "Wallet reputation acceptable",
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
              {
                error: `FairScore lookup failed: ${err.message}`,
                wallet: wallet_address,
                fallback_action: "WARN",
                fallback_limit_sol: 10,
              },
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

// 2. get_token_price ----------------------------------------------------------

server.tool(
  "get_token_price",
  "Get real-time Solana token price via Pyth Network oracle. Returns price, confidence interval, and timestamp.",
  {
    token: z
      .string()
      .describe(
        'Token symbol (SOL, USDC, USDT, BONK, JUP, RAY, BTC, ETH) or Pyth pair like "SOL/USD"'
      ),
  },
  async ({ token }) => {
    try {
      const priceData = await fetchPythPrice(token);
      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(
              {
                symbol: priceData.symbol,
                price_usd: priceData.price,
                confidence_usd: priceData.confidence,
                confidence_pct:
                  priceData.price > 0
                    ? ((priceData.confidence / priceData.price) * 100).toFixed(
                        4
                      )
                    : "0",
                publish_time: priceData.publish_time,
                source: "Pyth Network (Hermes)",
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
          { type: "text", text: JSON.stringify({ error: err.message }, null, 2) },
        ],
        isError: true,
      };
    }
  }
);

// 3. get_swap_quote -----------------------------------------------------------

server.tool(
  "get_swap_quote",
  "Get Jupiter DEX swap quote with best routes across all Solana DEXes. Returns output amount, price impact, and route info.",
  {
    input_token: z
      .string()
      .describe("Input token symbol (SOL, USDC, etc.) or mint address"),
    output_token: z
      .string()
      .describe("Output token symbol or mint address"),
    amount: z
      .number()
      .positive()
      .describe("Amount of input token to swap (human-readable, e.g. 1.5 SOL)"),
    slippage_bps: z
      .number()
      .int()
      .min(1)
      .max(5000)
      .optional()
      .default(50)
      .describe("Slippage tolerance in basis points (default 50 = 0.5%)"),
  },
  async ({ input_token, output_token, amount, slippage_bps }) => {
    try {
      const inputMint = resolveMint(input_token);
      const outputMint = resolveMint(output_token);
      const decimals = resolveDecimals(input_token);
      const amountSmallest = Math.round(amount * 10 ** decimals);

      const quote = await fetchJupiterQuote(
        inputMint,
        outputMint,
        amountSmallest,
        slippage_bps
      );

      const outDecimals = resolveDecimals(output_token);
      const outAmount = parseInt(quote.outAmount || "0", 10) / 10 ** outDecimals;
      const inAmount = parseInt(quote.inAmount || "0", 10) / 10 ** decimals;
      const priceImpact = parseFloat(quote.priceImpactPct || "0");

      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(
              {
                input_token: input_token.toUpperCase(),
                output_token: output_token.toUpperCase(),
                input_amount: inAmount,
                output_amount: outAmount,
                price_impact_pct: priceImpact,
                slippage_bps,
                route_steps: (quote.routePlan || []).length,
                effective_price:
                  inAmount > 0 ? (outAmount / inAmount).toFixed(8) : "0",
                warning:
                  priceImpact > 1
                    ? `High price impact: ${priceImpact}%`
                    : null,
                source: "Jupiter Aggregator",
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
          { type: "text", text: JSON.stringify({ error: err.message }, null, 2) },
        ],
        isError: true,
      };
    }
  }
);

// 4. check_wallet_balance -----------------------------------------------------

server.tool(
  "check_wallet_balance",
  "Check SOL and SPL token balances for a Solana wallet. Returns native SOL balance plus all token holdings.",
  {
    wallet_address: z.string().describe("Solana wallet address (base58)"),
    rpc_url: z
      .string()
      .url()
      .optional()
      .describe("Solana RPC URL (defaults to mainnet-beta)"),
  },
  async ({ wallet_address, rpc_url }) => {
    try {
      const rpc = rpc_url || SOLANA_RPC_URL;
      const solBalance = await fetchSolBalance(wallet_address, rpc);

      // Reverse lookup: mint -> symbol
      const mintToSymbol = {};
      for (const [sym, mint] of Object.entries(TOKEN_MINTS)) {
        mintToSymbol[mint] = sym;
      }

      const tokenAccounts = await fetchTokenAccounts(wallet_address, rpc);
      const tokens = [];

      for (const account of tokenAccounts) {
        const parsed = account.account?.data?.parsed?.info;
        if (!parsed) continue;

        const mint = parsed.mint;
        const amount = parseFloat(
          parsed.tokenAmount?.uiAmountString || "0"
        );
        if (amount === 0) continue;

        tokens.push({
          symbol: mintToSymbol[mint] || null,
          mint,
          amount,
          decimals: parsed.tokenAmount?.decimals || 0,
        });
      }

      // Sort by amount descending
      tokens.sort((a, b) => b.amount - a.amount);

      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(
              {
                wallet: wallet_address,
                sol_balance: solBalance,
                token_count: tokens.length,
                tokens: tokens.slice(0, 20), // Top 20
                rpc: rpc,
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
          { type: "text", text: JSON.stringify({ error: err.message }, null, 2) },
        ],
        isError: true,
      };
    }
  }
);

// 5. validate_transaction (THE KEY TOOL) --------------------------------------

server.tool(
  "validate_transaction",
  "Pre-flight safety check before signing any transaction. Checks recipient FairScore reputation and enforces transfer limits. THIS IS THE GUARDRAIL -- it prevents AI agents from sending funds to scam or low-reputation wallets.",
  {
    recipient: z
      .string()
      .describe("Recipient Solana wallet address (base58)"),
    amount: z
      .number()
      .positive()
      .describe("Amount to send (in SOL or token units)"),
    token: z
      .string()
      .optional()
      .default("SOL")
      .describe("Token symbol (default: SOL)"),
  },
  async ({ recipient, amount, token }) => {
    try {
      let fairscoreData;
      let score = null;
      let apiTier = null;
      let badges = [];
      let fairscoreAvailable = true;

      try {
        fairscoreData = await fetchFairScore(recipient);
        score = fairscoreData.fairscore ?? fairscoreData.score ?? null;
        apiTier = (fairscoreData.tier || "").toLowerCase();
        badges = fairscoreData.badges || [];
      } catch {
        fairscoreAvailable = false;
      }

      const def = score !== null ? scoreToDef(score) : null;
      const allowed =
        def === null
          ? true // allow with warning if FairScore unavailable
          : def.action !== "BLOCK" &&
            (def.limit === Infinity || amount <= def.limit);

      const warnings = [];

      if (!fairscoreAvailable) {
        warnings.push(
          "FairScore API unavailable -- proceeding with caution. Manual verification recommended."
        );
      }

      if (def?.action === "BLOCK") {
        warnings.push(
          `BLOCKED: Recipient has ${def.tier} reputation (score: ${score}). Transaction denied to protect against scam wallets.`
        );
      } else if (def?.action === "WARN") {
        warnings.push(
          `WARNING: Recipient has ${def.tier} reputation (score: ${score}). Low-trust wallet -- verify before proceeding.`
        );
      }

      if (def && def.limit !== Infinity && amount > def.limit) {
        warnings.push(
          `AMOUNT EXCEEDS LIMIT: Tier ${def.tier} allows max ${def.limit} SOL, requested ${amount} SOL.`
        );
      }

      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(
              {
                allowed,
                recipient,
                amount,
                token: token.toUpperCase(),
                fairscore: score,
                tier: def?.tier || "Unknown",
                action: def?.action || "WARN",
                max_allowed_amount:
                  def?.limit === Infinity
                    ? "unlimited"
                    : def?.limit ?? 10,
                badges: badges.map((b) =>
                  typeof b === "string" ? b : b.label || b.name || b
                ),
                warnings,
                fairscore_available: fairscoreAvailable,
                recommendation: allowed
                  ? "Transaction may proceed"
                  : "Transaction should be rejected",
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
          { type: "text", text: JSON.stringify({ error: err.message }, null, 2) },
        ],
        isError: true,
      };
    }
  }
);

// 6. list_supported_tokens ----------------------------------------------------

server.tool(
  "list_supported_tokens",
  "List all tokens supported for swaps, price lookups, and balance checks. Returns symbol, mint address, and name.",
  {},
  async () => {
    const tokens = [
      { symbol: "SOL", mint: TOKEN_MINTS.SOL, name: "Solana", decimals: 9 },
      { symbol: "USDC", mint: TOKEN_MINTS.USDC, name: "USD Coin", decimals: 6 },
      { symbol: "USDT", mint: TOKEN_MINTS.USDT, name: "Tether USD", decimals: 6 },
      { symbol: "BONK", mint: TOKEN_MINTS.BONK, name: "Bonk", decimals: 5 },
      { symbol: "JUP", mint: TOKEN_MINTS.JUP, name: "Jupiter", decimals: 6 },
      { symbol: "RAY", mint: TOKEN_MINTS.RAY, name: "Raydium", decimals: 6 },
    ];

    const priceFeeds = Object.keys(PYTH_PRICE_FEEDS);

    return {
      content: [
        {
          type: "text",
          text: JSON.stringify(
            {
              tokens,
              pyth_price_feeds: priceFeeds,
              swap_engine: "Jupiter Aggregator (lite-api)",
              price_oracle: "Pyth Network (Hermes)",
              reputation: "FairScale FairScore API",
            },
            null,
            2
          ),
        },
      ],
    };
  }
);

// 7. get_portfolio ------------------------------------------------------------

server.tool(
  "get_portfolio",
  "Get full portfolio with USD values for a Solana wallet. Combines on-chain balances with Pyth oracle prices.",
  {
    wallet_address: z.string().describe("Solana wallet address (base58)"),
    rpc_url: z
      .string()
      .url()
      .optional()
      .describe("Solana RPC URL (defaults to mainnet-beta)"),
  },
  async ({ wallet_address, rpc_url }) => {
    try {
      const rpc = rpc_url || SOLANA_RPC_URL;

      // Fetch SOL balance
      const solBalance = await fetchSolBalance(wallet_address, rpc);

      // Fetch token accounts
      const mintToSymbol = {};
      for (const [sym, mint] of Object.entries(TOKEN_MINTS)) {
        mintToSymbol[mint] = sym;
      }

      const tokenAccounts = await fetchTokenAccounts(wallet_address, rpc);
      const holdings = { SOL: solBalance };

      for (const account of tokenAccounts) {
        const parsed = account.account?.data?.parsed?.info;
        if (!parsed) continue;
        const mint = parsed.mint;
        const amount = parseFloat(parsed.tokenAmount?.uiAmountString || "0");
        if (amount === 0) continue;
        const sym = mintToSymbol[mint];
        if (sym) holdings[sym] = amount;
      }

      // Fetch prices for all held tokens
      const portfolio = [];
      let totalUsd = 0;

      for (const [symbol, amount] of Object.entries(holdings)) {
        let priceUsd = null;
        try {
          const p = await fetchPythPrice(symbol);
          priceUsd = p.price;
        } catch {
          // price unavailable
        }

        const valueUsd = priceUsd !== null ? amount * priceUsd : null;
        if (valueUsd !== null) totalUsd += valueUsd;

        portfolio.push({
          symbol,
          amount,
          price_usd: priceUsd,
          value_usd: valueUsd,
        });
      }

      // Calculate percentages
      for (const item of portfolio) {
        item.pct_of_portfolio =
          totalUsd > 0 && item.value_usd !== null
            ? parseFloat(((item.value_usd / totalUsd) * 100).toFixed(2))
            : null;
      }

      // Sort by USD value descending
      portfolio.sort(
        (a, b) => (b.value_usd ?? 0) - (a.value_usd ?? 0)
      );

      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(
              {
                wallet: wallet_address,
                total_value_usd: parseFloat(totalUsd.toFixed(2)),
                holdings: portfolio,
                token_count: portfolio.length,
                source: "Solana RPC + Pyth Network",
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
          { type: "text", text: JSON.stringify({ error: err.message }, null, 2) },
        ],
        isError: true,
      };
    }
  }
);

// 8. estimate_swap_cost -------------------------------------------------------

server.tool(
  "estimate_swap_cost",
  "Estimate total cost of a token swap including output amount, price impact, and effective price. Useful for agents evaluating trades before execution.",
  {
    input_token: z
      .string()
      .describe("Input token symbol (SOL, USDC, etc.) or mint address"),
    output_token: z
      .string()
      .describe("Output token symbol or mint address"),
    amount: z
      .number()
      .positive()
      .describe("Amount of input token (human-readable)"),
  },
  async ({ input_token, output_token, amount }) => {
    try {
      const inputMint = resolveMint(input_token);
      const outputMint = resolveMint(output_token);
      const inDecimals = resolveDecimals(input_token);
      const outDecimals = resolveDecimals(output_token);
      const amountSmallest = Math.round(amount * 10 ** inDecimals);

      // Get quote
      const quote = await fetchJupiterQuote(
        inputMint,
        outputMint,
        amountSmallest
      );

      const outAmount =
        parseInt(quote.outAmount || "0", 10) / 10 ** outDecimals;
      const priceImpact = parseFloat(quote.priceImpactPct || "0");

      // Get USD prices for both tokens
      let inputPriceUsd = null;
      let outputPriceUsd = null;

      try {
        const p = await fetchPythPrice(input_token);
        inputPriceUsd = p.price;
      } catch {
        // unavailable
      }
      try {
        const p = await fetchPythPrice(output_token);
        outputPriceUsd = p.price;
      } catch {
        // unavailable
      }

      const inputValueUsd =
        inputPriceUsd !== null ? amount * inputPriceUsd : null;
      const outputValueUsd =
        outputPriceUsd !== null ? outAmount * outputPriceUsd : null;

      const slippageCostUsd =
        inputValueUsd !== null && outputValueUsd !== null
          ? parseFloat((inputValueUsd - outputValueUsd).toFixed(4))
          : null;

      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(
              {
                input_token: input_token.toUpperCase(),
                output_token: output_token.toUpperCase(),
                input_amount: amount,
                output_amount: outAmount,
                effective_price:
                  amount > 0
                    ? parseFloat((outAmount / amount).toFixed(8))
                    : 0,
                price_impact_pct: priceImpact,
                input_value_usd: inputValueUsd,
                output_value_usd: outputValueUsd,
                estimated_cost_usd: slippageCostUsd,
                route_steps: (quote.routePlan || []).length,
                warning:
                  priceImpact > 1
                    ? `High price impact: ${priceImpact}%. Consider splitting into smaller trades.`
                    : priceImpact > 0.5
                      ? `Moderate price impact: ${priceImpact}%.`
                      : null,
                source: "Jupiter Aggregator + Pyth Network",
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
          { type: "text", text: JSON.stringify({ error: err.message }, null, 2) },
        ],
        isError: true,
      };
    }
  }
);

// 9. solana_get_fees ----------------------------------------------------------

server.tool(
  "solana_get_fees",
  "Get current Solana network fees, slot height, and transaction cost estimates. Returns base fee, priority fee stats, and estimated costs for common operations.",
  {
    rpc_url: z
      .string()
      .url()
      .optional()
      .describe("Solana RPC URL (defaults to mainnet-beta)"),
  },
  async ({ rpc_url }) => {
    try {
      const rpc = rpc_url || SOLANA_RPC_URL;

      // Get recent prioritization fees
      const feesResult = await httpPost(rpc, {
        jsonrpc: "2.0",
        id: 1,
        method: "getRecentPrioritizationFees",
        params: [],
      });

      // Get current slot
      const slotResult = await httpPost(rpc, {
        jsonrpc: "2.0",
        id: 2,
        method: "getSlot",
        params: [],
      });

      // Get latest blockhash (includes fee context)
      const blockhashResult = await httpPost(rpc, {
        jsonrpc: "2.0",
        id: 3,
        method: "getLatestBlockhash",
        params: [{ commitment: "finalized" }],
      });

      const fees = feesResult.result || [];
      const slot = slotResult.result || 0;
      const lastValidBlockHeight =
        blockhashResult.result?.value?.lastValidBlockHeight || 0;

      // Calculate priority fee stats from recent slots
      const priorityFees = fees
        .map((f) => f.prioritizationFee)
        .filter((f) => f > 0);
      const avgPriorityFee =
        priorityFees.length > 0
          ? priorityFees.reduce((a, b) => a + b, 0) / priorityFees.length
          : 0;
      const maxPriorityFee =
        priorityFees.length > 0 ? Math.max(...priorityFees) : 0;
      const medianPriorityFee =
        priorityFees.length > 0
          ? priorityFees.sort((a, b) => a - b)[
              Math.floor(priorityFees.length / 2)
            ]
          : 0;

      // Solana base fee is 5000 lamports per signature
      const baseFeePerSig = 5000;
      const baseFeeSOL = baseFeePerSig / 1e9;

      // Estimate costs
      const simpleTransferLamports = baseFeePerSig + medianPriorityFee;
      const tokenTransferLamports =
        baseFeePerSig + medianPriorityFee + 5000; // additional compute

      // Get SOL price for USD estimates
      let solPrice = null;
      try {
        const p = await fetchPythPrice("SOL");
        solPrice = p.price;
      } catch {
        // unavailable
      }

      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(
              {
                chain: "Solana",
                current_slot: slot,
                last_valid_block_height: lastValidBlockHeight,
                base_fee_lamports: baseFeePerSig,
                base_fee_sol: baseFeeSOL,
                priority_fees: {
                  median_lamports: medianPriorityFee,
                  average_lamports: Math.round(avgPriorityFee),
                  max_lamports: maxPriorityFee,
                  sample_count: priorityFees.length,
                },
                estimated_costs: {
                  sol_transfer_lamports: simpleTransferLamports,
                  sol_transfer_sol: simpleTransferLamports / 1e9,
                  sol_transfer_usd:
                    solPrice !== null
                      ? parseFloat(
                          ((simpleTransferLamports / 1e9) * solPrice).toFixed(8)
                        )
                      : null,
                  token_transfer_lamports: tokenTransferLamports,
                  token_transfer_sol: tokenTransferLamports / 1e9,
                },
                sol_price_usd: solPrice,
                rpc,
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
            text: JSON.stringify({ error: err.message }, null, 2),
          },
        ],
        isError: true,
      };
    }
  }
);

// ===========================================================================
// BASE (EVM) TOOLS
// ===========================================================================

// 10. base_check_balance -------------------------------------------------------

server.tool(
  "base_check_balance",
  "Check ETH and ERC-20 token balances for a Base wallet. Returns native ETH balance plus common token holdings on Base L2 (Chain ID 8453).",
  {
    wallet_address: z
      .string()
      .regex(/^0x[a-fA-F0-9]{40}$/)
      .describe("Base/EVM wallet address (0x...)"),
    rpc_url: z
      .string()
      .url()
      .optional()
      .describe("Base RPC URL (defaults to https://mainnet.base.org)"),
  },
  async ({ wallet_address, rpc_url }) => {
    try {
      const rpc = rpc_url || BASE_RPC_URL;
      const ethBalance = await fetchBaseEthBalance(wallet_address, rpc);

      const tokens = [];
      for (const [symbol, info] of Object.entries(BASE_TOKENS)) {
        if (info.address === "native") continue;
        try {
          const balance = await fetchBaseTokenBalance(
            wallet_address,
            info.address,
            info.decimals,
            rpc
          );
          if (balance > 0) {
            tokens.push({
              symbol,
              name: info.name,
              address: info.address,
              balance,
              decimals: info.decimals,
            });
          }
        } catch {
          // skip tokens that fail
        }
      }

      tokens.sort((a, b) => b.balance - a.balance);

      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(
              {
                chain: "Base",
                chain_id: BASE_CHAIN_ID,
                wallet: wallet_address,
                eth_balance: ethBalance,
                token_count: tokens.length,
                tokens,
                rpc,
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
          { type: "text", text: JSON.stringify({ error: err.message }, null, 2) },
        ],
        isError: true,
      };
    }
  }
);

// 11. base_get_gas_price ------------------------------------------------------

server.tool(
  "base_get_gas_price",
  "Get current gas price on Base L2. Returns gas price in Gwei and Wei, plus latest block number. Useful for estimating transaction costs.",
  {
    rpc_url: z
      .string()
      .url()
      .optional()
      .describe("Base RPC URL (defaults to https://mainnet.base.org)"),
  },
  async ({ rpc_url }) => {
    try {
      const rpc = rpc_url || BASE_RPC_URL;
      const [gasPriceWei, blockNumber] = await Promise.all([
        fetchBaseGasPrice(rpc),
        fetchBaseBlockNumber(rpc),
      ]);

      const gasPriceGwei = gasPriceWei / 1e9;

      // Estimate costs for common operations (21000 gas for ETH transfer)
      const ethTransferCost = (gasPriceWei * 21000) / 1e18;
      const erc20TransferCost = (gasPriceWei * 65000) / 1e18;

      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(
              {
                chain: "Base",
                chain_id: BASE_CHAIN_ID,
                gas_price_gwei: parseFloat(gasPriceGwei.toFixed(6)),
                gas_price_wei: gasPriceWei,
                latest_block: blockNumber,
                estimated_costs_eth: {
                  eth_transfer: parseFloat(ethTransferCost.toFixed(10)),
                  erc20_transfer: parseFloat(erc20TransferCost.toFixed(10)),
                },
                note: "Base L2 gas costs are typically very low compared to Ethereum mainnet",
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
          { type: "text", text: JSON.stringify({ error: err.message }, null, 2) },
        ],
        isError: true,
      };
    }
  }
);

// 12. base_get_token_price ----------------------------------------------------

server.tool(
  "base_get_token_price",
  "Get token price on Base via Pyth Network oracle. Supports ETH, BTC, USDC, USDT. Returns price in USD with confidence interval.",
  {
    token: z
      .string()
      .describe('Token symbol (ETH, BTC, USDC, USDT) or Pyth pair like "ETH/USD"'),
  },
  async ({ token }) => {
    try {
      // Map Base token names to Pyth feeds
      const baseTokenMap = {
        ETH: "ETH/USD",
        WETH: "ETH/USD",
        cbETH: "ETH/USD", // approximate
      };
      const mapped = baseTokenMap[token.toUpperCase()] || token;
      const priceData = await fetchPythPrice(mapped);

      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(
              {
                chain: "Base",
                symbol: token.toUpperCase(),
                pyth_feed: priceData.symbol,
                price_usd: priceData.price,
                confidence_usd: priceData.confidence,
                publish_time: priceData.publish_time,
                source: "Pyth Network (Hermes)",
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
          { type: "text", text: JSON.stringify({ error: err.message }, null, 2) },
        ],
        isError: true,
      };
    }
  }
);

// 13. base_get_portfolio ------------------------------------------------------

server.tool(
  "base_get_portfolio",
  "Get full portfolio with USD values for a Base wallet. Combines on-chain ETH and ERC-20 balances with Pyth oracle prices.",
  {
    wallet_address: z
      .string()
      .regex(/^0x[a-fA-F0-9]{40}$/)
      .describe("Base/EVM wallet address (0x...)"),
    rpc_url: z
      .string()
      .url()
      .optional()
      .describe("Base RPC URL (defaults to https://mainnet.base.org)"),
  },
  async ({ wallet_address, rpc_url }) => {
    try {
      const rpc = rpc_url || BASE_RPC_URL;
      const ethBalance = await fetchBaseEthBalance(wallet_address, rpc);

      const holdings = [];
      let totalUsd = 0;

      // ETH balance + price
      let ethPrice = null;
      try {
        const p = await fetchPythPrice("ETH");
        ethPrice = p.price;
      } catch {
        // unavailable
      }
      const ethValue = ethPrice !== null ? ethBalance * ethPrice : null;
      if (ethValue !== null) totalUsd += ethValue;
      holdings.push({
        symbol: "ETH",
        amount: ethBalance,
        price_usd: ethPrice,
        value_usd: ethValue,
      });

      // ERC-20 tokens
      for (const [symbol, info] of Object.entries(BASE_TOKENS)) {
        if (info.address === "native") continue;
        try {
          const balance = await fetchBaseTokenBalance(
            wallet_address,
            info.address,
            info.decimals,
            rpc
          );
          if (balance === 0) continue;

          let price = null;
          // Map token to Pyth feed
          const priceFeedMap = {
            WETH: "ETH",
            USDC: "USDC",
            USDbC: "USDC",
            DAI: "USDC", // approximate stablecoin
            cbETH: "ETH", // approximate
          };
          const feedSymbol = priceFeedMap[symbol];
          if (feedSymbol) {
            try {
              const p = await fetchPythPrice(feedSymbol);
              price = p.price;
            } catch {
              // unavailable
            }
          }

          const value = price !== null ? balance * price : null;
          if (value !== null) totalUsd += value;

          holdings.push({
            symbol,
            name: info.name,
            amount: balance,
            price_usd: price,
            value_usd: value,
          });
        } catch {
          // skip
        }
      }

      // Calculate percentages
      for (const h of holdings) {
        h.pct_of_portfolio =
          totalUsd > 0 && h.value_usd !== null
            ? parseFloat(((h.value_usd / totalUsd) * 100).toFixed(2))
            : null;
      }

      holdings.sort((a, b) => (b.value_usd ?? 0) - (a.value_usd ?? 0));

      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(
              {
                chain: "Base",
                chain_id: BASE_CHAIN_ID,
                wallet: wallet_address,
                total_value_usd: parseFloat(totalUsd.toFixed(2)),
                holdings,
                token_count: holdings.length,
                source: "Base RPC + Pyth Network",
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
          { type: "text", text: JSON.stringify({ error: err.message }, null, 2) },
        ],
        isError: true,
      };
    }
  }
);

// 14. base_list_tokens --------------------------------------------------------

server.tool(
  "base_list_tokens",
  "List all tokens supported on Base for balance checks and price lookups. Returns symbol, contract address, decimals, and name.",
  {},
  async () => {
    const tokens = Object.entries(BASE_TOKENS).map(([symbol, info]) => ({
      symbol,
      name: info.name,
      address: info.address,
      decimals: info.decimals,
    }));

    return {
      content: [
        {
          type: "text",
          text: JSON.stringify(
            {
              chain: "Base",
              chain_id: BASE_CHAIN_ID,
              tokens,
              rpc_default: BASE_RPC_URL,
              price_oracle: "Pyth Network (Hermes)",
              note: "Coldstar supports air-gapped signing for Base via secp256k1 ECDSA + EIP-1559 Type 2 transactions",
            },
            null,
            2
          ),
        },
      ],
    };
  }
);

// ---------------------------------------------------------------------------
// Start
// ---------------------------------------------------------------------------

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
}

main().catch((err) => {
  console.error("Coldstar MCP server failed to start:", err);
  process.exit(1);
});
