from datetime import datetime, timedelta
from src.fraud.FraudDetectionSystem import FraudDetectionSystem
from src.fraud.Transaction import Transaction

class TestFraudDetectionSystemMutation:

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
        current_transaction = Transaction(amount=-100.0, timestamp=now, location="Sao Paulo")
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

    def test_check_for_fraud_boundary_value_10000(self):
        fds = FraudDetectionSystem()
        now = datetime.now()

        current_transaction = Transaction(amount=10000.00, timestamp=now, location="Sao Paulo")
        previous_transactions = []
        blacklisted_locations = []

        result = fds.check_for_fraud(
            current_transaction=current_transaction,
            previous_transactions=previous_transactions,
            blacklisted_locations=blacklisted_locations
        )

        assert result.risk_score == 0
        assert not result.is_fraudulent

    def test_check_for_fraud_excessive_transactions_in_short_period_60_minutes(self):
        ## muitas transacoes em pouco tempo
        fds = FraudDetectionSystem()

        now = datetime.now()

        current_transaction = Transaction(amount=50.00,timestamp=now,location="Sao Paulo")

        previous_transactions = [
            Transaction(
                amount=25.00,
                timestamp=now - timedelta(minutes=60),
                location="Campinas"
            ) for i in range(1, 12)
        ]

        blacklisted_locations = ["Caracas", "Pyongyang"]

        result = fds.check_for_fraud(
            current_transaction=current_transaction,
            previous_transactions=previous_transactions,
            blacklisted_locations=blacklisted_locations
        )

        assert not result.is_fraudulent
        assert result.is_blocked
        assert not result.verification_required
        assert result.risk_score == 30


    def test_check_for_fraud_excessive_transactions_in_short_period_over_60_minutes(self):
        ## muitas transacoes em pouco tempo
        fds = FraudDetectionSystem()

        now = datetime.now()

        current_transaction = Transaction(amount=50.00,timestamp=now,location="Sao Paulo")

        previous_transactions = [
            Transaction(
                amount=25.00,
                timestamp=now - timedelta(seconds=3630),
                location="Campinas"
            ) for i in range(1, 12)
        ]

        blacklisted_locations = ["Caracas", "Pyongyang"]

        result = fds.check_for_fraud(
            current_transaction=current_transaction,
            previous_transactions=previous_transactions,
            blacklisted_locations=blacklisted_locations
        )

        assert not result.is_fraudulent
        assert not result.is_blocked
        assert not result.verification_required
        assert result.risk_score == 0


    def test_check_for_fraud_high_value_and_excessive_transactions(self):
        # teste para matar o mutante 97
        fds = FraudDetectionSystem()
        now = datetime.now()

        current_transaction = Transaction(amount=12000.00, timestamp=now, location="Sao Paulo")

        previous_transactions = [
            Transaction(
                amount=25.00,
                timestamp=now - timedelta(minutes=i * 5),
                location="Campinas"
            ) for i in range(1, 12)
        ]

        blacklisted_locations = ["Caracas"]

        result = fds.check_for_fraud(
            current_transaction=current_transaction,
            previous_transactions=previous_transactions,
            blacklisted_locations=blacklisted_locations
        )

        assert result.risk_score == 80
        assert result.is_blocked
        assert result.is_fraudulent

    def test_check_for_fraud_location_change_boundary_30_min(self):
        fds = FraudDetectionSystem()
        now = datetime.now()

        current_transaction = Transaction(amount=200.00, timestamp=now, location="Rio de Janeiro")

        previous_transactions = [
            Transaction(amount=150.00, timestamp=now - timedelta(seconds=1806), location="Sao Paulo")
        ]

        blacklisted_locations = ["Caracas"]

        result = fds.check_for_fraud(
            current_transaction=current_transaction,
            previous_transactions=previous_transactions,
            blacklisted_locations=blacklisted_locations
        )

        assert result.risk_score == 0
        assert not result.is_fraudulent

    def test_check_for_fraud_excessive_transactions_in_short_period_10_transactions(self):
        ## muitas transacoes em pouco tempo
        fds = FraudDetectionSystem()

        now = datetime.now()

        current_transaction = Transaction(amount=50.00,timestamp=now,location="Sao Paulo")

        previous_transactions = [
            Transaction(
                amount=25.00,
                timestamp=now - timedelta(minutes=i * 5),
                location="Campinas"
            ) for i in range(1, 11)
        ]

        blacklisted_locations = ["Caracas", "Pyongyang"]

        result = fds.check_for_fraud(
            current_transaction=current_transaction,
            previous_transactions=previous_transactions,
            blacklisted_locations=blacklisted_locations
        )

        assert not result.is_fraudulent
        assert not result.is_blocked
        assert not result.verification_required
        assert result.risk_score == 0



    def test_check_for_fraud_multiple_triggers_high_value_and_location_change(self):
        fds = FraudDetectionSystem()
        now = datetime.now()

        current_transaction = Transaction(amount=12000.00, timestamp=now, location="Rio de Janeiro")

        previous_transactions = [
            Transaction(amount=100.00, timestamp=now - timedelta(minutes=20), location="Sao Paulo")
        ]

        blacklisted_locations = ["Caracas"]

        result = fds.check_for_fraud(
            current_transaction=current_transaction,
            previous_transactions=previous_transactions,
            blacklisted_locations=blacklisted_locations
        )

        assert result.is_fraudulent
        assert not result.is_blocked
        assert result.verification_required
        assert result.risk_score == 70


    def test_check_for_fraud_location_change_exact_30_min(self):
        fds = FraudDetectionSystem()
        now = datetime.now()

        current_transaction = Transaction(amount=200.00, timestamp=now, location="Rio de Janeiro")

        previous_transactions = [
            Transaction(amount=150.00, timestamp=now - timedelta(minutes=30), location="Sao Paulo")
        ]

        blacklisted_locations = ["Caracas"]

        result = fds.check_for_fraud(
            current_transaction=current_transaction,
            previous_transactions=previous_transactions,
            blacklisted_locations=blacklisted_locations
        )

        assert result.risk_score == 0
        assert not result.is_fraudulent