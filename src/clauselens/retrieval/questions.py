# we got predefined ques 
from dataclasses import dataclass


@dataclass(frozen=True)
class Question:
    id: str
    text: str
    keywords: tuple[str, ...]


QUESTIONS: tuple[Question, ...] = (

    Question(
        id="agreement_type",
        text="What type of agreement is this?",
        keywords=("rental agreement", "rent", "leave and licence"),
    ),

    Question(
        id="monthly_rent",
        text="What is the monthly rent the tenant must pay?",
        keywords=("monthly rent", "rent", "per month"),
    ),

    Question(
        id="security_deposit",
        text="What is the security deposit paid by the tenant?",
        keywords=("security deposit", "refundable deposit", "deposit"),
    ),

    Question(
        id="total_length",
        text="What is the total duration of the agreement?",
        keywords=("agreement period", "tenure", "duration"),
    ),

    Question(
        id="lock_in",
        text="What is the lock-in period of the agreement?",
        keywords=("lock-in period", "minimum stay", "lock in"),
    ),

    Question(
        id="lock_in_applies_to",
        text="Does the lock-in period apply to the tenant, landlord, or both?",
        keywords=("lock-in", "tenant", "landlord"),
    ),

    Question(
        id="tenant_notice",
        text="How much notice must the tenant give before terminating the agreement?",
        keywords=("tenant notice", "notice period", "termination notice"),
    ),

    Question(
        id="landlord_notice",
        text="How much notice must the landlord give before terminating the agreement?",
        keywords=("landlord notice", "notice period", "termination"),
    ),

    Question(
        id="tenant_can_leave_early",
        text="Can the tenant terminate the agreement before its expiry?",
        keywords=("early termination", "tenant", "premature exit"),
    ),

    Question(
        id="landlord_can_end_early",
        text="Can the landlord terminate the agreement before its expiry?",
        keywords=("early termination", "landlord", "premature termination"),
    ),

    Question(
        id="rent_increase",
        text="Can the rent increase, and under what conditions?",
        keywords=("rent escalation", "rent increase", "enhancement"),
    ),

    Question(
        id="maintenance",
        text="What are the maintenance charges and who is responsible for paying them?",
        keywords=("maintenance charges", "maintenance fee", "payer"),
    ),

    Question(
        id="deposit_refund_time",
        text="When must the landlord refund the security deposit?",
        keywords=("deposit refund", "refund period", "security deposit"),
    ),

    Question(
        id="auto_renewal",
        text="Does the agreement automatically renew after expiry?",
        keywords=("automatic renewal", "renewal", "extension"),
    ),

    Question(
        id="late_fee",
        text="What penalty or late fee applies if rent is paid late?",
        keywords=("late fee", "penalty", "delayed rent payment"),
    ),

)
