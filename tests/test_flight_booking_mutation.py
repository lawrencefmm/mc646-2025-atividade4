import pytest
from datetime import datetime, timedelta
from src.flight.FlightBookingSystem import FlightBookingSystem

@pytest.fixture
def booking_system():
    return FlightBookingSystem()

NOW = datetime(2025, 10, 15, 10, 0, 0)

class TestFlightBookingSystemMutation:

    def test_booking_zero_passengers(self, booking_system):
        departure_time = NOW + timedelta(days=1)
        result = booking_system.book_flight(
            passengers=0,
            booking_time=NOW,
            available_seats=100,
            current_price=500.0,
            previous_sales=50,
            is_cancellation=False,
            departure_time=departure_time,
            reward_points_available=0,
        )
        assert not result.confirmation
        assert result.total_price == 0.0

    def test_booking_negative_price(self, booking_system):
        departure_time = NOW + timedelta(days=1)
        result = booking_system.book_flight(
            passengers=1,
            booking_time=NOW,
            available_seats=100,
            current_price=-100.0,
            previous_sales=50,
            is_cancellation=False,
            departure_time=departure_time,
            reward_points_available=0,
        )
        assert not result.confirmation or result.total_price <= 0.0

    def test_booking_with_reward_points(self, booking_system):
        departure_time = NOW + timedelta(days=2)
        result = booking_system.book_flight(
            passengers=1,
            booking_time=NOW,
            available_seats=100,
            current_price=500.0,
            previous_sales=50,
            is_cancellation=False,
            departure_time=departure_time,
            reward_points_available=1000,
        )
        assert result.points_used is True or result.total_price < 500.0
