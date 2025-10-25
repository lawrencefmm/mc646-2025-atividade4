import pytest
from datetime import datetime
from src.energy.DeviceSchedule import DeviceSchedule

class TestDeviceScheduleMutation:
    """Testes de mutação para DeviceSchedule."""

    def test_device_schedule_different_types(self):
        # Mutação: device_name como None
        scheduled_time = datetime(2025, 10, 2, 18, 0, 0)
        device_schedule = DeviceSchedule(None, scheduled_time)
        assert device_schedule.device_name is None
        assert device_schedule.scheduled_time == scheduled_time

    def test_device_schedule_future_time(self):
        # Mutação: scheduled_time muito no futuro
        device_name = "Future Device"
        scheduled_time = datetime(2100, 1, 1, 0, 0, 0)
        device_schedule = DeviceSchedule(device_name, scheduled_time)
        assert device_schedule.device_name == device_name
        assert device_schedule.scheduled_time == scheduled_time

    def test_device_schedule_repr_mutation(self):
        # Mutação: device_name com caracteres especiais
        device_name = "D€v!c€"
        scheduled_time = datetime(2025, 12, 31, 23, 59, 59)
        device_schedule = DeviceSchedule(device_name, scheduled_time)
        repr_string = repr(device_schedule)
        expected_repr = f"DeviceSchedule(device_name='{device_name}', scheduled_time='{scheduled_time}')"
        assert repr_string == expected_repr
