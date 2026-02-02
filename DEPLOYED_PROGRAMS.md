# Coldstar DAO Programs - Devnet Deployment

## Deployed Programs

### Network: Solana Devnet

**Deployment Date**: 2025-01-25
**Deployer Wallet**: `EbRUGhi2uLP5TamZx8fjNwn3dnvqoN4VNFRcent5Zykp`

---

## Program IDs

### 1. Coldstar DAO
**Program ID**: `Ue6Z2MBm7DxR5QTAYRRNsdXc7KBRgASQabA7DJYXeat`
- **Binary**: `target/deploy/coldstar_dao.so`
- **Size**: 486KB
- **Purpose**: DAO governance for community-managed cold storage vaults
- **Features**:
  - Proposal creation and voting
  - Multi-sig treasury management
  - Epoch-based rewards
  - On-chain governance

**Solana Explorer**:
https://explorer.solana.com/address/Ue6Z2MBm7DxR5QTAYRRNsdXc7KBRgASQabA7DJYXeat?cluster=devnet

### 2. Coldstar Voter Stake Registry
**Program ID**: `2ueu2H3tN8U3SWNsQPogd3dWhjnNBXH5AqiZ1H47ViZx`
- **Binary**: `target/deploy/coldstar_voter_stake_registry.so`
- **Size**: 387KB
- **Purpose**: Decentralized voting power calculation based on staked tokens
- **Features**:
  - Stake-weighted voting
  - Lock-up periods for increased voting power
  - Vote delegation
  - On-chain vote tracking

**Solana Explorer**:
https://explorer.solana.com/address/2ueu2H3tN8U3SWNsQPogd3dWhjnNBXH5AqiZ1H47ViZx?cluster=devnet

---

## Test Tokens (Devnet)

### CRT (Coldstar Governance Token)
- **Mint**: `3RDBd1ASrCHjYQyneDJQKCvEezn4hXQrLXJeCjdVP8JF`
- **Treasury**: `GkDUAQunG9D8cPp4fuiiqtRKroQiSSYJF9UKxz27956k`
- **Note**: Mainnet version will be launched via DeAura.io

### xSLV (Silver-backed Token)
- **Mint**: `46HC14Yy7gprgCUpjrzycuG4LnCjnxTgrE97RP8k2ex9`
- **Treasury**: `Ayej7iaxoYKqQUNmrzBfM9MiiXZDLWTSWFJUKxa79kFo`

### xPLT (Platinum-backed Token)
- **Mint**: `G4YU1dyuSncnYRXPVHuFkYViADv6qf4y16sQSPZZ3xE4`
- **Treasury**: `8okZWGbkkLLto8QXdNegEkLMdK8bujnnA9UaQJX82t8c`

### xOIL (Oil-backed Token)
- **Mint**: `Ao3boF124LC1AkDnCn2KBPmoPzD7RtHhWUPgG8qDHQEa`
- **Treasury**: `HL1dvon3Q7rsz78TihWEZn37u4aEUaUuTwutStyVcX3L`

### xURA (Uranium-backed Token)
- **Mint**: `7FKkxayYGSUqVxbKsZixcEtRv3GMQuYLst1oD3xJw85W`
- **Treasury**: `35JWwPKTd49ugJso6d6eD6L8FFQXeGxEPqSJkzav89k5`

---

## Usage Examples

### Create a DAO Vault

```typescript
import { Program, AnchorProvider } from "@coral-xyz/anchor";
import { ColdstarDao } from "./target/types/coldstar_dao";

const programId = "Ue6Z2MBm7DxR5QTAYRRNsdXc7KBRgASQabA7DJYXeat";
const program = new Program<ColdstarDao>(idl, programId, provider);

await program.methods
  .createVault(
    "Agent Treasury",  // name
    3,                 // threshold (3 of 5)
    [agent1, agent2, agent3, agent4, agent5]  // members
  )
  .accounts({
    vault: vaultPda,
    authority: wallet.publicKey,
  })
  .rpc();
```

### Create Proposal

```typescript
await program.methods
  .createProposal(
    "Transfer 100 SOL to development fund",
    ProposalType.Transfer,
    { amount: 100_000_000_000, recipient: devFund }
  )
  .accounts({
    vault: vaultPda,
    proposal: proposalPda,
    proposer: wallet.publicKey,
  })
  .rpc();
```

### Vote on Proposal

```typescript
await program.methods
  .vote(Vote.Approve)
  .accounts({
    proposal: proposalPda,
    voter: wallet.publicKey,
    voterRecord: voterRecordPda,
  })
  .rpc();
```

### Execute Proposal

```typescript
// Automatically executes when threshold is reached
await program.methods
  .executeProposal()
  .accounts({
    proposal: proposalPda,
    vault: vaultPda,
  })
  .rpc();
```

---

## Integration with Coldstar CLI

The Coldstar CLI integrates with these programs for secure DAO operations:

```bash
# Create DAO vault (online device)
coldstar dao create-vault \
  --name "Agent Treasury" \
  --threshold 3 \
  --members agent1,agent2,agent3,agent4,agent5

# Create proposal (online device)
coldstar dao propose \
  --vault AgentTreasury \
  --action transfer \
  --amount 100 \
  --recipient TargetWallet

# Vote on proposal (air-gapped device for each member)
coldstar dao vote \
  --proposal ProposalID \
  --vote approve

# Sign vote transaction (offline)
coldstar sign-transaction --input vote.json --output vote_signed.json

# Broadcast vote (online)
coldstar broadcast --input vote_signed.json
```

---

## Security Features

### Air-Gapped Voting
- Each member reviews proposal details on offline device
- Private keys never exposed to network
- QR code workflow for transaction transfer
- Full transaction visibility before signing

### Multi-Sig Protection
- Requires M-of-N signatures (configurable)
- No single point of failure
- On-chain verification of all signatures
- Transparent execution

### Governance
- Epoch-based proposal lifecycle
- Vote delegation support
- Stake-weighted voting power
- Automatic execution when threshold met

---

## Testing on Devnet

### Get Devnet SOL
```bash
solana airdrop 2 YOUR_WALLET --url devnet
```

### Mint Test CRT Tokens
```bash
spl-token mint 3RDBd1ASrCHjYQyneDJQKCvEezn4hXQrLXJeCjdVP8JF 1000 \
  --url devnet
```

### Verify Program Deployment
```bash
solana program show Ue6Z2MBm7DxR5QTAYRRNsdXc7KBRgASQabA7DJYXeat \
  --url devnet
```

---

## Roadmap

### Phase 1: Devnet Testing (Current)
- [x] Deploy DAO program
- [x] Deploy voter-stake-registry
- [x] Test token minting
- [ ] End-to-end DAO workflow testing
- [ ] CLI integration testing

### Phase 2: Mainnet Launch (Future)
- [ ] Security audit
- [ ] Launch CRT token via DeAura.io
- [ ] Mainnet deployment
- [ ] Community governance activation

### Phase 3: Advanced Features (Future)
- [ ] Time-locked proposals
- [ ] Quadratic voting
- [ ] Delegation marketplace
- [ ] Cross-program governance

---

## Resources

- **Program Code**: `/Volumes/Virtual Server/projects/coldstar-repo/programs/`
- **Anchor Framework**: https://www.anchor-lang.com/
- **Solana Explorer**: https://explorer.solana.com/?cluster=devnet
- **Documentation**: See `README.md` in program directories

---

*Deployed for the Colosseum Agent Hackathon*
*Agent: coldstar-agent | Project: Coldstar - Air-Gapped Solana Vault*
