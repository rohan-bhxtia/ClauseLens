
"""Deterministic risk rules over extracted facts (Day 6)."""

from typing import Literal

from pydantic import BaseModel

from clauselens.extraction.scoring import DAYS_PER_UNIT
from clauselens.schemas.lease import Fact


# Risk thresholds
LOCK_IN_MAX_DAYS = 180
DEPOSIT_MAX_RENT_MULTIPLE = 3
RENT_INCREASE_MAX_PERCENT = 10


class RiskFlag(BaseModel):
    rule_id: str
    severity: Literal["low", "medium", "high"]
    message: str
    evidence: str | None = None
    page: int | None = None


def _days(duration) -> int:
    """Convert a Duration model into days."""
    return duration.amount * DAYS_PER_UNIT[duration.unit]


def _found(facts: dict[str, Fact], field: str) -> Fact | None:
    """Return a fact only if it exists and its status is found."""
    fact = facts.get(field)

    if fact is None or fact.status != "found":
        return None

    return fact

## tenant must live there in this much time
def long_lock_in(facts: dict[str, Fact]) -> list[RiskFlag]:
    """Flag lock-in periods exceeding 180 days."""
    fact = _found(facts, "lock_in")

    if fact is None:
        return []

    if _days(fact.answer) > LOCK_IN_MAX_DAYS:
        return [
            RiskFlag(
                rule_id="long_lock_in",
                severity="medium",
                message="Lock-in period exceeds 180 days.",
                evidence=fact.line,
                page=fact.page,
            )
        ]

    return []

# comparing the timelines of both parties terminating the lease.
# lets say in lease my landlord wrote that i need to tell 3 months prior 
# and he only has to tell 1 month prior before kicking me away 
# thats imbalance 
def notice_imbalance(facts: dict[str, Fact]) -> list[RiskFlag]:
    """Flag when tenant notice exceeds landlord notice."""
    tenant = _found(facts, "tenant_notice")
    landlord = _found(facts, "landlord_notice")

    if tenant is None or landlord is None:
        return []

    if _days(tenant.answer) > _days(landlord.answer):
        return [
            RiskFlag(
                rule_id="notice_imbalance",
                severity="medium",
                message=(
                    "Tenant notice period is longer than "
                    "landlord notice period."
                ),
                evidence=tenant.line,
                page=tenant.page,
            )
        ]

    return []

# tenant has to pay high advance
def high_deposit(facts: dict[str, Fact]) -> list[RiskFlag]:
    """Flag security deposits exceeding three times monthly rent."""
    deposit = _found(facts, "security_deposit")
    rent = _found(facts, "monthly_rent")

    if deposit is None or rent is None:
        return []

    if deposit.answer > DEPOSIT_MAX_RENT_MULTIPLE * rent.answer:
        return [
            RiskFlag(
                rule_id="high_deposit",
                severity="high",
                message=(
                    "Security deposit exceeds three times "
                    "the monthly rent."
                ),
                evidence=deposit.line,
                page=deposit.page,
            )
        ]

    return []

# rent gords up a lott in short time 
def steep_rent_increase(facts: dict[str, Fact]) -> list[RiskFlag]:
    """Flag rent increases exceeding 10 percent."""
    fact = _found(facts, "rent_increase")

    if fact is None:
        return []

    if fact.answer.percent > RENT_INCREASE_MAX_PERCENT:
        return [
            RiskFlag(
                rule_id="steep_rent_increase",
                severity="medium",
                message="Rent increase exceeds 10 percent.",
                evidence=fact.line,
                page=fact.page,
            )
        ]

    return []

# lease is confusing about ending it. wordings might be conflicting
def unclear_exit_terms(facts: dict[str, Fact]) -> list[RiskFlag]:
    """Flag missing deposit refund terms and early landlord termination."""
    flags = []

    # Check 1: Deposit refund time is not found.
    refund = _found(facts, "deposit_refund_time")

    if refund is None:
        flags.append(
            RiskFlag(
                rule_id="missing_deposit_refund_time",
                severity="medium",
                message="Deposit refund time is not stated or found.",
            )
        )

    # Check 2: Landlord can terminate the agreement early.
    early_termination = _found(facts, "landlord_can_end_early")

    if early_termination is not None and early_termination.answer is True:
        flags.append(
            RiskFlag(
                rule_id="landlord_early_termination",
                severity="low",
                message="Landlord has the right to end the agreement early.",
                evidence=early_termination.line,
                page=early_termination.page,
            )
        )

    return flags


RULES = [
    long_lock_in,
    notice_imbalance,
    high_deposit,
    steep_rent_increase,
    unclear_exit_terms,
]


def check_risks(facts: dict[str, Fact]) -> list[RiskFlag]:
    """Run all risk rules and return a combined list of flags."""
    flags = []

    for rule in RULES:
        flags.extend(rule(facts))

    return flags
