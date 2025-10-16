import pytest
from datetime import datetime, timedelta
from src.flight.FlightBookingSystem import FlightBookingSystem


@pytest.fixture
def booking_system():
    return FlightBookingSystem()


NOW = datetime(2025, 10, 15, 10, 0, 0)


def test_standard_booking_successful(booking_system):
    departure_time = NOW + timedelta(days=5)
    result = booking_system.book_flight(
        passengers=2,
        booking_time=NOW,
        available_seats=100,
        current_price=500.0,
        previous_sales=50,
        is_cancellation=False,
        departure_time=departure_time,
        reward_points_available=0,
    )
    assert result.confirmation is True
    assert result.total_price == pytest.approx(400.0)
    assert result.refund_amount == 0.0
    assert result.points_used is False


def test_booking_fails_insufficient_seats(booking_system):
    departure_time = NOW + timedelta(days=5)
    result = booking_system.book_flight(
        passengers=5,
        booking_time=NOW,
        available_seats=4,
        current_price=500.0,
        previous_sales=50,
        is_cancellation=False,
        departure_time=departure_time,
        reward_points_available=0,
    )
    assert result.confirmation is False
    assert result.total_price == 0.0
    assert result.refund_amount == 0.0
    assert result.points_used is False


def test_last_minute_fee_applied(booking_system):
    departure_time = NOW + timedelta(hours=23)
    result = booking_system.book_flight(
        passengers=1,
        booking_time=NOW,
        available_seats=100,
        current_price=500.0,
        previous_sales=50,
        is_cancellation=False,
        departure_time=departure_time,
        reward_points_available=0,
    )
    assert result.confirmation is True
    assert result.total_price == pytest.approx(300.0)


def test_group_discount_applied(booking_system):
    departure_time = NOW + timedelta(days=10)
    result = booking_system.book_flight(
        passengers=5,
        booking_time=NOW,
        available_seats=100,
        current_price=500.0,
        previous_sales=50,
        is_cancellation=False,
        departure_time=departure_time,
        reward_points_available=0,
    )
    assert result.confirmation is True
    assert result.total_price == pytest.approx(950.0)


def test_reward_points_used(booking_system):
    departure_time = NOW + timedelta(days=10)
    result = booking_system.book_flight(
        passengers=2,
        booking_time=NOW,
        available_seats=100,
        current_price=500.0,
        previous_sales=50,
        is_cancellation=False,
        departure_time=departure_time,
        reward_points_available=5000,
    )
    assert result.confirmation is True
    assert result.total_price == pytest.approx(350.0)
    assert result.points_used is True


def test_price_becomes_zero_with_excessive_points(booking_system):
    departure_time = NOW + timedelta(days=10)
    result = booking_system.book_flight(
        passengers=1,
        booking_time=NOW,
        available_seats=100,
        current_price=200.0,
        previous_sales=50,
        is_cancellation=False,
        departure_time=departure_time,
        reward_points_available=10000,
    )
    assert result.confirmation is True
    assert result.total_price == pytest.approx(0.0)
    assert result.points_used is True


def test_cancellation_full_refund(booking_system):
    departure_time = NOW + timedelta(hours=49)
    result = booking_system.book_flight(
        passengers=2,
        booking_time=NOW,
        available_seats=100,
        current_price=500.0,
        previous_sales=50,
        is_cancellation=True,
        departure_time=departure_time,
        reward_points_available=0,
    )
    assert result.confirmation is False
    assert result.total_price == 0
    assert result.refund_amount == pytest.approx(400.0)
    assert result.points_used is False


def test_cancellation_partial_refund(booking_system):
    departure_time = NOW + timedelta(hours=47)
    result = booking_system.book_flight(
        passengers=2,
        booking_time=NOW,
        available_seats=100,
        current_price=500.0,
        previous_sales=50,
        is_cancellation=True,
        departure_time=departure_time,
        reward_points_available=0,
    )
    assert result.confirmation is False
    assert result.total_price == 0
    assert result.refund_amount == pytest.approx(200.0)
    assert result.points_used is False
