import pytest
from datetime import datetime, timedelta
from src.energy.EnergyManagementSystem import SmartEnergyManagementSystem
from src.energy.DeviceSchedule import DeviceSchedule


@pytest.fixture
def system():
    return SmartEnergyManagementSystem()


BASE_TIME = datetime(2025, 10, 15, 12, 0, 0)

DEVICE_PRIORITIES = {
    "Security": 1,
    "Refrigerator": 1,
    "Heating": 1,
    "Cooling": 1,
    "Lights": 2,
    "TV": 2,
    "Washer": 3,
    "Dishwasher": 3,
    "Dryer": 2,
    "Fan": 3,
    "Oven": 2,
}


def test_energy_saving_mode_turns_off_low_priority_devices(system):
    device_priorities = DEVICE_PRIORITIES.copy()
    result = system.manage_energy(
        current_price=0.3,
        price_threshold=0.2,
        device_priorities=device_priorities,
        current_time=BASE_TIME,
        current_temperature=22.0,
        desired_temperature_range=(20.0, 24.0),
        energy_usage_limit=50.0,
        total_energy_used_today=10.0,
        scheduled_devices=[],
    )
    assert result.energy_saving_mode is True
    assert result.device_status["Security"] is True
    assert result.device_status["Refrigerator"] is True
    assert result.device_status["Lights"] is False
    assert result.device_status["TV"] is False
    assert result.temperature_regulation_active is False
    assert result.device_status["Heating"] is False
    assert result.device_status["Cooling"] is False


def test_devices_remain_on_without_energy_saving(system):
    device_priorities = DEVICE_PRIORITIES.copy()
    result = system.manage_energy(
        current_price=0.15,
        price_threshold=0.2,
        device_priorities=device_priorities,
        current_time=BASE_TIME,
        current_temperature=21.5,
        desired_temperature_range=(20.0, 24.0),
        energy_usage_limit=30.0,
        total_energy_used_today=5.0,
        scheduled_devices=[DeviceSchedule("Oven", BASE_TIME + timedelta(hours=1))],
    )
    assert result.energy_saving_mode is False
    assert result.device_status["Security"] is True
    assert result.device_status["Lights"] is True
    assert result.device_status["Heating"] is False
    assert result.device_status["Cooling"] is False
    assert result.temperature_regulation_active is False
    assert result.device_status["Oven"] is True


def test_night_mode_preserves_essential_devices_only(system):
    device_priorities = DEVICE_PRIORITIES.copy()
    night_time = datetime(2025, 10, 15, 23, 30, 0)
    result = system.manage_energy(
        current_price=0.15,
        price_threshold=0.2,
        device_priorities=device_priorities,
        current_time=night_time,
        current_temperature=21.0,
        desired_temperature_range=(20.0, 24.0),
        energy_usage_limit=40.0,
        total_energy_used_today=8.0,
        scheduled_devices=[],
    )
    assert result.energy_saving_mode is False
    assert result.device_status["Security"] is True
    assert result.device_status["Refrigerator"] is True
    assert result.device_status["Lights"] is False
    assert result.device_status["TV"] is False


def test_temperature_regulation_heating_activated(system):
    device_priorities = DEVICE_PRIORITIES.copy()
    result = system.manage_energy(
        current_price=0.15,
        price_threshold=0.2,
        device_priorities=device_priorities,
        current_time=BASE_TIME,
        current_temperature=18.0,
        desired_temperature_range=(20.0, 24.0),
        energy_usage_limit=25.0,
        total_energy_used_today=7.0,
        scheduled_devices=[],
    )
    assert result.temperature_regulation_active is True
    assert result.device_status["Heating"] is True
    assert result.device_status["Cooling"] is True


def test_temperature_regulation_cooling_activated(system):
    device_priorities = DEVICE_PRIORITIES.copy()
    result = system.manage_energy(
        current_price=0.15,
        price_threshold=0.2,
        device_priorities=device_priorities,
        current_time=BASE_TIME,
        current_temperature=26.0,
        desired_temperature_range=(20.0, 24.0),
        energy_usage_limit=25.0,
        total_energy_used_today=7.0,
        scheduled_devices=[],
    )
    assert result.temperature_regulation_active is True
    assert result.device_status["Cooling"] is True
    assert result.device_status["Heating"] is True


def test_energy_limit_progressively_turns_off_low_priority_devices(system):
    device_priorities = DEVICE_PRIORITIES.copy()
    result = system.manage_energy(
        current_price=0.15,
        price_threshold=0.2,
        device_priorities=device_priorities,
        current_time=BASE_TIME,
        current_temperature=21.0,
        desired_temperature_range=(20.0, 24.0),
        energy_usage_limit=10.0,
        total_energy_used_today=12.0,
        scheduled_devices=[],
    )
    assert result.total_energy_used == pytest.approx(9.0)
    assert result.device_status["Lights"] is False
    assert result.device_status["TV"] is False
    assert result.device_status["Washer"] is False
    assert result.device_status["Dishwasher"] is True


def test_energy_limit_stops_when_no_low_priority_devices_on(system):
    device_priorities = DEVICE_PRIORITIES.copy()
    result = system.manage_energy(
        current_price=0.3,
        price_threshold=0.2,
        device_priorities=device_priorities,
        current_time=BASE_TIME,
        current_temperature=22.0,
        desired_temperature_range=(20.0, 24.0),
        energy_usage_limit=5.0,
        total_energy_used_today=15.0,
        scheduled_devices=[],
    )
    assert result.total_energy_used == pytest.approx(15.0)
    assert result.device_status["Security"] is True
    assert result.device_status["Lights"] is False


def test_scheduled_device_overrides_previous_decisions(system):
    device_priorities = DEVICE_PRIORITIES.copy()
    schedules = [
        DeviceSchedule("Fan", BASE_TIME + timedelta(hours=1)),
        DeviceSchedule("Oven", BASE_TIME),
    ]
    result = system.manage_energy(
        current_price=0.3,
        price_threshold=0.2,
        device_priorities=device_priorities,
        current_time=BASE_TIME,
        current_temperature=22.0,
        desired_temperature_range=(20.0, 24.0),
        energy_usage_limit=40.0,
        total_energy_used_today=8.0,
        scheduled_devices=schedules,
    )
    assert result.device_status["Fan"] is False
    assert result.device_status["Oven"] is True
    assert result.energy_saving_mode is True
