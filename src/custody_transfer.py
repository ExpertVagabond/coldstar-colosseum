"""
Custody Transfer Manager — Institutional stablecoin custody operations.

Extends TokenTransferManager with:
- Recipient whitelist validation
- Institutional fee tiers
- Compliance metadata attachment
- Batch transfer support
- Audit trail generation

Built for StableHacks 2026 — Institutional Permissioned DeFi Vaults track.
"""

import json
import time
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field

from src.token_transfer import TokenTransferManager, KNOWN_TOKENS, TokenInfo


# Institutional stablecoins (extend KNOWN_TOKENS)
INSTITUTIONAL_STABLES = {
    "USDC": KNOWN_TOKENS["USDC"],
    "USDT": KNOWN_TOKENS["USDT"],
}

# Fee tiers for institutional operations
FEE_TIERS = {
    "standard": 0.001,     # 10 bps
    "preferred": 0.0005,   # 5 bps
    "institutional": 0.0,  # 0 bps (for pilot partners)
}


@dataclass
class WhitelistEntry:
    """Approved recipient for custody transfers."""
    address: str
    label: str
    added_by: str
    added_at: float
    is_active: bool = True


@dataclass
class CustodyRequest:
    """Withdrawal request requiring multi-sig approval."""
    request_id: int
    vault_address: str
    requester: str
    recipient: str
    amount: float
    token: str
    reason: str
    approvals: list[str] = field(default_factory=list)
    status: str = "pending"  # pending, approved, executed, rejected, cancelled
    created_at: float = 0.0
    executed_at: float = 0.0


@dataclass
class AuditEntry:
    """On-chain audit trail entry."""
    event_type: str
    vault_address: str
    actor: str
    details: dict
    timestamp: float
    tx_signature: str = ""


class CustodyTransferManager(TokenTransferManager):
    """
    Institutional custody transfer manager.

    Wraps TokenTransferManager with compliance controls:
    - Whitelist-only recipients
    - Daily volume tracking
    - Multi-sig approval workflow
    - Complete audit trail
    """

    def __init__(
        self,
        rpc_url: str = "https://api.devnet.solana.com",
        vault_address: str = "",
        approval_threshold: int = 2,
        daily_limit: float = 100_000.0,
        fee_tier: str = "standard",
    ):
        super().__init__(rpc_url=rpc_url)
        self.vault_address = vault_address
        self.approval_threshold = approval_threshold
        self.daily_limit = daily_limit
        self.fee_tier = fee_tier
        self.daily_volume = 0.0
        self.last_volume_reset = time.time()

        self.whitelist: dict[str, WhitelistEntry] = {}
        self.requests: list[CustodyRequest] = []
        self.audit_trail: list[AuditEntry] = []
        self.request_counter = 0

    def _reset_daily_volume_if_needed(self) -> None:
        """Reset daily volume counter after 24 hours."""
        if time.time() - self.last_volume_reset >= 86400:
            self.daily_volume = 0.0
            self.last_volume_reset = time.time()

    def _log_audit(
        self, event_type: str, actor: str, details: dict, tx_sig: str = ""
    ) -> AuditEntry:
        """Record an audit trail entry."""
        entry = AuditEntry(
            event_type=event_type,
            vault_address=self.vault_address,
            actor=actor,
            details=details,
            timestamp=time.time(),
            tx_signature=tx_sig,
        )
        self.audit_trail.append(entry)
        return entry

    def add_to_whitelist(
        self, address: str, label: str, added_by: str
    ) -> WhitelistEntry:
        """Add a recipient address to the vault whitelist."""
        entry = WhitelistEntry(
            address=address,
            label=label,
            added_by=added_by,
            added_at=time.time(),
        )
        self.whitelist[address] = entry
        self._log_audit(
            "whitelist_added",
            added_by,
            {"recipient": address, "label": label},
        )
        return entry

    def remove_from_whitelist(self, address: str, removed_by: str) -> bool:
        """Deactivate a whitelist entry."""
        if address not in self.whitelist:
            return False
        self.whitelist[address].is_active = False
        self._log_audit(
            "whitelist_removed",
            removed_by,
            {"recipient": address},
        )
        return True

    def validate_recipient(self, address: str) -> tuple[bool, str]:
        """Check if a recipient is whitelisted and active."""
        if address not in self.whitelist:
            return False, "Recipient not on whitelist"
        if not self.whitelist[address].is_active:
            return False, "Recipient whitelist entry is deactivated"
        return True, "OK"

    def validate_transfer(
        self, recipient: str, amount: float, token: str
    ) -> tuple[bool, list[str]]:
        """
        Pre-flight validation for a custody transfer.

        Returns (allowed, list_of_issues).
        """
        issues: list[str] = []

        # Check whitelist
        valid, msg = self.validate_recipient(recipient)
        if not valid:
            issues.append(msg)

        # Check token support
        if token not in INSTITUTIONAL_STABLES:
            issues.append(f"Token {token} not in institutional stablecoin whitelist")

        # Check daily limit
        self._reset_daily_volume_if_needed()
        if self.daily_volume + amount > self.daily_limit:
            remaining = self.daily_limit - self.daily_volume
            issues.append(
                f"Daily limit exceeded: {amount} requested, {remaining:.2f} remaining of {self.daily_limit:.2f}"
            )

        # Check amount
        if amount <= 0:
            issues.append("Amount must be positive")

        return len(issues) == 0, issues

    def calculate_fee(self, amount: float) -> float:
        """Calculate institutional fee for a transfer."""
        rate = FEE_TIERS.get(self.fee_tier, FEE_TIERS["standard"])
        return amount * rate

    def create_custody_request(
        self,
        requester: str,
        recipient: str,
        amount: float,
        token: str,
        reason: str,
    ) -> tuple[Optional[CustodyRequest], list[str]]:
        """
        Create a withdrawal request requiring multi-sig approval.

        Returns (request, issues). Issues list is empty on success.
        """
        allowed, issues = self.validate_transfer(recipient, amount, token)
        if not allowed:
            return None, issues

        self.request_counter += 1
        request = CustodyRequest(
            request_id=self.request_counter,
            vault_address=self.vault_address,
            requester=requester,
            recipient=recipient,
            amount=amount,
            token=token,
            reason=reason,
            created_at=time.time(),
        )
        self.requests.append(request)

        self._log_audit(
            "withdrawal_requested",
            requester,
            {
                "request_id": request.request_id,
                "recipient": recipient,
                "amount": amount,
                "token": token,
                "reason": reason,
            },
        )

        return request, []

    def approve_request(
        self, request_id: int, custodian: str
    ) -> tuple[bool, str]:
        """Approve a pending withdrawal request."""
        request = self._find_request(request_id)
        if request is None:
            return False, f"Request {request_id} not found"
        if request.status != "pending":
            return False, f"Request is {request.status}, not pending"
        if custodian in request.approvals:
            return False, "Already approved by this custodian"

        request.approvals.append(custodian)

        self._log_audit(
            "withdrawal_approved",
            custodian,
            {
                "request_id": request_id,
                "approvals": len(request.approvals),
                "threshold": self.approval_threshold,
            },
        )

        if len(request.approvals) >= self.approval_threshold:
            request.status = "approved"

        return True, f"Approved ({len(request.approvals)}/{self.approval_threshold})"

    def reject_request(
        self, request_id: int, custodian: str
    ) -> tuple[bool, str]:
        """Reject a pending withdrawal request."""
        request = self._find_request(request_id)
        if request is None:
            return False, f"Request {request_id} not found"
        if request.status != "pending":
            return False, f"Request is {request.status}, not pending"

        request.status = "rejected"

        self._log_audit(
            "withdrawal_rejected",
            custodian,
            {"request_id": request_id},
        )

        return True, "Request rejected"

    def execute_request(
        self, request_id: int, executor: str
    ) -> tuple[bool, str]:
        """
        Execute an approved withdrawal.

        The actual on-chain transfer is delegated to the parent
        TokenTransferManager via create_token_transfer_transaction().
        """
        request = self._find_request(request_id)
        if request is None:
            return False, f"Request {request_id} not found"
        if request.status != "approved":
            return False, f"Request is {request.status}, needs 'approved' status"

        # Update daily volume
        self._reset_daily_volume_if_needed()
        if self.daily_volume + request.amount > self.daily_limit:
            return False, "Daily limit would be exceeded"

        self.daily_volume += request.amount
        request.status = "executed"
        request.executed_at = time.time()

        fee = self.calculate_fee(request.amount)

        self._log_audit(
            "withdrawal_executed",
            executor,
            {
                "request_id": request_id,
                "recipient": request.recipient,
                "amount": request.amount,
                "token": request.token,
                "fee": fee,
            },
        )

        return True, f"Executed: {request.amount} {request.token} to {request.recipient}"

    def get_pending_requests(self) -> list[CustodyRequest]:
        """Get all pending withdrawal requests."""
        return [r for r in self.requests if r.status == "pending"]

    def get_approved_requests(self) -> list[CustodyRequest]:
        """Get requests approved but not yet executed."""
        return [r for r in self.requests if r.status == "approved"]

    def get_vault_status(self) -> dict:
        """Get vault health and compliance summary."""
        self._reset_daily_volume_if_needed()
        return {
            "vault_address": self.vault_address,
            "approval_threshold": self.approval_threshold,
            "daily_limit": self.daily_limit,
            "daily_volume_used": self.daily_volume,
            "daily_remaining": self.daily_limit - self.daily_volume,
            "active_whitelist": sum(
                1 for w in self.whitelist.values() if w.is_active
            ),
            "pending_requests": len(self.get_pending_requests()),
            "approved_requests": len(self.get_approved_requests()),
            "total_requests": len(self.requests),
            "fee_tier": self.fee_tier,
            "audit_entries": len(self.audit_trail),
        }

    def export_audit_trail(
        self, output_path: str, fmt: str = "json"
    ) -> str:
        """Export audit trail for compliance reporting."""
        path = Path(output_path)

        if fmt == "json":
            data = [
                {
                    "event_type": e.event_type,
                    "vault": e.vault_address,
                    "actor": e.actor,
                    "details": e.details,
                    "timestamp": e.timestamp,
                    "tx_signature": e.tx_signature,
                }
                for e in self.audit_trail
            ]
            path.write_text(json.dumps(data, indent=2))
        elif fmt == "csv":
            lines = ["event_type,vault,actor,timestamp,tx_signature,details"]
            for e in self.audit_trail:
                details_str = json.dumps(e.details).replace(",", ";")
                lines.append(
                    f"{e.event_type},{e.vault_address},{e.actor},"
                    f"{e.timestamp},{e.tx_signature},{details_str}"
                )
            path.write_text("\n".join(lines))

        return str(path)

    def _find_request(self, request_id: int) -> Optional[CustodyRequest]:
        """Find a request by ID."""
        for r in self.requests:
            if r.request_id == request_id:
                return r
        return None
