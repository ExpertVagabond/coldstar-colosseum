# Terms of Service

**Coldstar — Air-Gapped Solana Cold Wallet**
Last updated: February 15, 2026
Operated by: Purple Squirrel Media LLC

---

## 1. Acceptance

By downloading, installing, or using Coldstar, you agree to these terms. If you do not agree, do not use the software.

---

## 2. What Coldstar Is

Coldstar is open-source, self-custody wallet software for the Solana blockchain. It is designed to create air-gapped cold wallets on USB drives. Coldstar is a **tool** — it does not custody your funds, manage your accounts, or act as a financial intermediary.

**You are solely responsible for:**
- Your private keys and wallet passwords
- Your USB device and its physical security
- Every transaction you sign and broadcast
- Complying with laws in your jurisdiction

---

## 3. No Custody, No Fiduciary Duty

Coldstar does not hold, control, or have access to your private keys, funds, or tokens. We cannot:

- Reverse, cancel, or modify your transactions
- Recover lost passwords or private keys
- Freeze or seize your assets
- Access your wallet in any way

If you lose your password or USB device without a backup, **your funds are permanently lost.** There is no recovery mechanism we can provide.

---

## 4. Self-Custody Risks

You acknowledge that self-custody of digital assets carries inherent risks, including but not limited to:

- **Loss of access** — Forgotten passwords, lost USB drives, or corrupted files can result in permanent loss of funds.
- **Transaction finality** — Solana transactions are irreversible once confirmed. Sending funds to the wrong address cannot be undone.
- **Smart contract risk** — Token swaps via Jupiter interact with third-party smart contracts that may contain bugs or exploits.
- **Market risk** — Digital asset values are volatile and can drop to zero.
- **Regulatory risk** — Laws governing digital assets vary by jurisdiction and may change.

---

## 5. FairScore Reputation Gating

Coldstar integrates FairScale's FairScore API to check wallet reputation before transactions. You acknowledge:

- FairScore data is provided by a third party (FairScale) and may be inaccurate, outdated, or incomplete.
- A low FairScore does not necessarily mean a wallet is malicious. A high FairScore does not guarantee safety.
- Reputation gating is an advisory tool, not a guarantee against fraud or loss.
- Coldstar's tier system (Bronze through Diamond) sets transfer limits based on FairScore. These limits are configurable in the source code.

---

## 6. Infrastructure Fee

Coldstar includes a 1% infrastructure fee on transactions, directed to the project wallet (`Cak1aAwxM2jTdu7AtdaHbqAc3Dfafts7KdsHNrtXN5rT`). This fee:

- Is visible in the transaction details before you sign
- Supports ongoing development of Coldstar
- Can be removed or modified by you since the software is open source (see `config.py`)

---

## 7. Third-Party Services

Coldstar connects to third-party APIs for blockchain data, price feeds, reputation scores, and swap routing. These services have their own terms and privacy policies:

| Service | Purpose | Terms |
|---------|---------|-------|
| Solana RPC | Blockchain access | [solana.com/terms](https://solana.com/terms) |
| FairScale | Reputation scores | [fairscale.xyz](https://fairscale.xyz) |
| Jupiter | DEX aggregation | [jup.ag/terms](https://jup.ag/terms) |
| Pyth Network | Price feeds | [pyth.network](https://pyth.network) |

We do not control these services and are not responsible for their availability, accuracy, or data practices.

---

## 8. Open Source License

Coldstar is released under the MIT License. You may use, modify, and distribute it freely under those terms. The full license is available in the `LICENSE` file.

The MIT License means the software is provided **"as is"** without warranty of any kind.

---

## 9. Disclaimer of Warranties

TO THE MAXIMUM EXTENT PERMITTED BY LAW, COLDSTAR IS PROVIDED "AS IS" AND "AS AVAILABLE" WITHOUT WARRANTIES OF ANY KIND, WHETHER EXPRESS, IMPLIED, OR STATUTORY, INCLUDING BUT NOT LIMITED TO WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, NON-INFRINGEMENT, OR ACCURACY.

We do not warrant that:
- The software will be error-free or uninterrupted
- The Rust secure signer is free from cryptographic vulnerabilities
- Third-party API data (prices, scores, routes) is accurate
- Transactions will confirm successfully on the Solana network
- The air-gap security model prevents all possible attack vectors

---

## 10. Limitation of Liability

TO THE MAXIMUM EXTENT PERMITTED BY LAW, PURPLE SQUIRREL MEDIA LLC, ITS CONTRIBUTORS, AND AFFILIATES SHALL NOT BE LIABLE FOR ANY INDIRECT, INCIDENTAL, SPECIAL, CONSEQUENTIAL, OR PUNITIVE DAMAGES, INCLUDING BUT NOT LIMITED TO LOSS OF FUNDS, LOSS OF DATA, LOSS OF PROFITS, OR LOSS OF ACCESS TO DIGITAL ASSETS, ARISING OUT OF OR RELATED TO YOUR USE OF COLDSTAR, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGES.

IN NO EVENT SHALL OUR TOTAL LIABILITY EXCEED THE AMOUNT YOU PAID FOR THE SOFTWARE (WHICH IS $0, SINCE IT IS FREE AND OPEN SOURCE).

---

## 11. Security Disclosures

If you discover a security vulnerability in Coldstar, please report it responsibly:

- **GitHub Security Advisory:** [Report a vulnerability](https://github.com/ExpertVagabond/coldstar-colosseum/security/advisories/new)
- **Do not** post vulnerabilities as public issues.

See `SECURITY.md` for our full security policy.

---

## 12. Prohibited Uses

You agree not to use Coldstar to:

- Violate any applicable laws or regulations
- Launder money or finance terrorism
- Evade sanctions or other legal restrictions
- Facilitate fraud, theft, or other criminal activity

Coldstar is a neutral tool. We cannot prevent misuse, but we do not condone it.

---

## 13. Governing Law

These terms are governed by the laws of the State of Wyoming, United States, without regard to conflict of law principles. Any disputes shall be resolved in the courts of Wyoming.

---

## 14. Changes

We may update these terms as the project evolves. Changes will be committed to the repository with full git history. Continued use of Coldstar after changes constitutes acceptance.

---

## 15. Contact

For questions about these terms, open an issue on [GitHub](https://github.com/ExpertVagabond/coldstar-colosseum/issues) or reach us at [@buildcoldstar](https://x.com/buildcoldstar).
