from clauselens.risk.rules import (
    long_lock_in,
    notice_imbalance,
    high_deposit,
    steep_rent_increase,
    unclear_exit_terms,
    check_risks,
)
from clauselens.schemas.lease import Fact, Duration, RentIncrease


def make_fact(answer, line="Test evidence", page=1):
    return Fact(
        status="found",
        answer=answer,
        line=line,
        page=page,
    )


def make_missing_fact():
    return Fact(status="not_stated")


def test_long_lock_in_fires():
    facts = {"lock_in": make_fact(Duration(amount=8, unit="months"))}
    assert long_lock_in(facts)[0].rule_id == "long_lock_in"


def test_long_lock_in_does_not_fire():
    facts = {"lock_in": make_fact(Duration(amount=3, unit="months"))}
    assert long_lock_in(facts) == []


def test_long_lock_in_stays_silent_when_missing():
    assert long_lock_in({}) == []
    assert long_lock_in({"lock_in": make_missing_fact()}) == []


def test_notice_imbalance_fires():
    facts = {
        "tenant_notice": make_fact(Duration(amount=3, unit="months")),
        "landlord_notice": make_fact(Duration(amount=1, unit="months")),
    }
    assert notice_imbalance(facts)[0].rule_id == "notice_imbalance"


def test_notice_imbalance_does_not_fire():
    facts = {
        "tenant_notice": make_fact(Duration(amount=1, unit="months")),
        "landlord_notice": make_fact(Duration(amount=3, unit="months")),
    }
    assert notice_imbalance(facts) == []


def test_notice_imbalance_stays_silent_when_missing():
    assert notice_imbalance({}) == []


def test_high_deposit_fires():
    facts = {
        "security_deposit": make_fact(100000),
        "monthly_rent": make_fact(25000),
    }
    assert high_deposit(facts)[0].rule_id == "high_deposit"


def test_high_deposit_does_not_fire():
    facts = {
        "security_deposit": make_fact(75000),
        "monthly_rent": make_fact(25000),
    }
    assert high_deposit(facts) == []


def test_high_deposit_stays_silent_when_missing():
    assert high_deposit({}) == []


def test_steep_rent_increase_fires():
    facts = {
        "rent_increase": make_fact(
            RentIncrease(percent=15, when="every_year")
        )
    }
    assert steep_rent_increase(facts)[0].rule_id == "steep_rent_increase"


def test_steep_rent_increase_does_not_fire():
    facts = {
        "rent_increase": make_fact(
            RentIncrease(percent=10, when="every_year")
        )
    }
    assert steep_rent_increase(facts) == []


def test_steep_rent_increase_stays_silent_when_missing():
    assert steep_rent_increase({}) == []


def test_unclear_exit_terms_fires():
    facts = {
        "deposit_refund_time": make_missing_fact(),
        "landlord_can_end_early": make_fact(True),
    }
    flags = unclear_exit_terms(facts)
    assert len(flags) == 2


def test_unclear_exit_terms_does_not_flag_early_termination():
    facts = {
        "deposit_refund_time": make_fact(Duration(amount=30, unit="days")),
        "landlord_can_end_early": make_fact(False),
    }
    flags = unclear_exit_terms(facts)
    assert len(flags) == 0


def test_unclear_exit_terms_stays_silent_about_early_termination_when_missing():
    facts = {
        "deposit_refund_time": make_fact(Duration(amount=30, unit="days"))
    }
    assert unclear_exit_terms(facts) == []


def test_check_risks_combines_flags():
    facts = {
        "lock_in": make_fact(Duration(amount=8, unit="months")),
        "security_deposit": make_fact(100000),
        "monthly_rent": make_fact(25000),
    }
    flags = check_risks(facts)
    assert len(flags) == 3