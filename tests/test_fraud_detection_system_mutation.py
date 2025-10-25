from datetime import datetime, timedelta
from src.fraud.FraudDetectionSystem import FraudDetectionSystem
from src.fraud.Transaction import Transaction

class TestFraudDetectionSystemMutation:
    """Testes de mutação para FraudDetectionSystem."""

    def test_fraud_blacklisted_location(self):
        fds = FraudDetectionSystem()
        now = datetime.now()
        current_transaction = Transaction(amount=100.0, timestamp=now, location="Pyongyang")
        previous_transactions = []
        blacklisted_locations = ["Caracas", "Pyongyang"]
        result = fds.check_for_fraud(
            current_transaction=current_transaction,
            previous_transactions=previous_transactions,
            blacklisted_locations=blacklisted_locations
        )
        assert result.is_blocked or result.is_fraudulent

    def test_fraud_negative_amount(self):
        fds = FraudDetectionSystem()
        now = datetime.now()
        current_transaction = Transaction(amount=-100.0, timestamp=now, location="São Paulo")
        previous_transactions = []
        blacklisted_locations = []
        result = fds.check_for_fraud(
            current_transaction=current_transaction,
            previous_transactions=previous_transactions,
            blacklisted_locations=blacklisted_locations
        )
        assert result.is_fraudulent or result.risk_score > 0

    def test_fraud_empty_location(self):
        fds = FraudDetectionSystem()
        now = datetime.now()
        current_transaction = Transaction(amount=100.0, timestamp=now, location="")
        previous_transactions = []
        blacklisted_locations = []
        result = fds.check_for_fraud(
            current_transaction=current_transaction,
            previous_transactions=previous_transactions,
            blacklisted_locations=blacklisted_locations
        )
        assert result.risk_score >= 0
