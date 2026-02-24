# Coldstar — Solana Security Knowledge Base

*This file is Coldstar's domain-specific security competency. Use it when evaluating transactions, auditing programs, or advising on signing security.*

## Core Competencies (11 published deep dives)

### 1. Signing Surface
- Transactions bundle multiple instructions — signing one means signing ALL of them
- Ed25519: native Solana signatures, on-chain verification without signer present
- Secp256k1: Ethereum-compatible, used by cross-chain bridges
- Partial signing: multi-party transactions, cold device signs only its accounts
- Durable nonces: blockhash substitute for offline signing (THE cold signing primitive)
- Replay prevention: blockhash/nonce consumed on use, track nonce advancement

### 2. Compute Exhaustion Attacks
- Unbounded iteration: attacker fills vectors, every instruction burns CUs → paginate
- Excessive deserialization: inflate accounts to max size → use zero-copy
- Deep CPI chains: 4-level depth limit, each level costs compute
- Log spam: msg!() consumes CUs — 10K chars ≈ 10K CUs
- Liveness attack, not safety — program unusable, funds not stolen, but cold wallet jammed

### 3. Reentrancy
- Classic reentrancy impossible: runtime locks accounts during CPI
- Cross-instruction reentrancy: no locking between instructions in same transaction
- CPI callback patterns: shared state modified by intermediate programs
- Account aliasing: same data via different keys → double-counting/double-spending
- Cold signing: verify instruction ordering AND account overlap, not just individual instructions

### 4. Upgradeable Program Security
- Upgrade authority = single keypair can replace ALL program bytecode
- Attack: replace bytecode → drain all PDAs → no user interaction needed
- Defense layers: multisig authority → timelock (24-48hr) → immutability → verified builds
- Cold signing risk: program upgraded between verification and landing = different logic
- Rule: only interact with immutable programs or multisig+timelock upgrade authorities

### 5. MEV (Maximal Extractable Value)
- No public mempool, but Jito block engine creates one for searchers
- Sandwich: buy before your swap, let you execute at worse price, sell after
- Defenses: tight slippage limits, Jito bundles for protection, private submission
- Cold signers can't react in real-time → pre-sign with conservative slippage

### 6. Multisig Patterns
- M-of-N threshold: 2-of-3 (small teams), 3-of-5 (DAOs), 4-of-7 (treasuries)
- Squads v4: time-locks, spending limits, role-based, smart account abstractions
- Cold multisig: proposal on-chain → fetch offline → sign offline → collect → execute
- Escrow: PDA owned by multisig, 2-of-3 with arbiter for disputes
- Key loss failure mode: in 3-of-5, losing 3 keys = permanently locked funds

### 7. Account Ownership
- Only owning program can modify account data — foundational security primitive
- Fake account injection: attacker passes their account where yours expected → verify owner
- Writable account substitution: config passed as user account → verify discriminator + PDA
- UncheckedAccount in Anchor: skips validation, every writable one is a vulnerability
- Cold signing rule: check writable accounts in transaction — unexpected writables = reject

### 8. PDA Seed Collision Attacks
- User-controlled string seeds can collide with legitimate PDAs
- Numeric overflow in seeds enables precomputing future PDAs
- Defense: include signer pubkey in all user-specific PDAs
- Use account type prefixes: ["user_profile",...] vs ["user_settings",...]
- Enforce canonical bump always

### 9. Missing Signer Checks
- Most common vulnerability: forgetting to verify is_signer
- Use Anchor's Signer<'info> type for automatic enforcement
- Check: is the authority account actually signing? Not just passed?
- has_one constraint validates account relationships

### 10. Arithmetic Overflow
- Rust release mode wraps silently — Solana compiles release mode
- Use checked_add/checked_sub/checked_mul
- Intermediate overflow: use u128 for calculations, downcast result
- Anchor checked math feature auto-replaces operators

### 11. Flash Loan Patterns
- Borrow unlimited capital, repay same transaction
- Oracle manipulation: dump → exploit → restore → repay
- Governance attacks: borrow tokens → vote → execute → repay
- Defense: TWAP oracles, commit-reveal, minimum lock periods

## Transaction Review Checklist (for cold signing)
1. List all writable accounts — are any unexpected?
2. Check all program IDs — are any unfamiliar or upgradeable?
3. Verify instruction count — multiple instructions to same program = suspicious
4. Check for account overlap between instructions (aliasing risk)
5. Verify durable nonce is used (not recent blockhash)
6. Confirm slippage limits on any swap instructions
7. Verify the upgrade authority of any program being called (multisig? timelock? immutable?)

## Remaining Topics (17 to publish)
- [ ] Signer impersonation patterns
- [ ] Authority transfers/revocation
- [ ] Token account closure risks
- [ ] Type confusion exploits
- [ ] Oracle manipulation
- [ ] Time-of-check vs time-of-use
- [ ] Instruction introspection attacks
- [ ] Cross-program invocation risks
- [ ] Rent exemption edge cases
- [ ] Account close and recreate
- [ ] Initialization frontrunning
- [ ] Missing rent validation
- [ ] Fake program ID injection
- [ ] Ed25519 vs secp256k1 verification
- [ ] Durable nonce security
- [ ] Partial signing risks
- [ ] Hardware wallet integration patterns
