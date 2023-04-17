from pathlib import Path
from unittest import mock

import pytest

from device_adapter.device.hardware_adapter import HardwareAdapter
from device_adapter.device_adapter_config import DeviceConfig


@pytest.fixture(name='device')
def fixture_adapter() -> HardwareAdapter:
    device_config = DeviceConfig(
        runner='runner',
        build_dir=Path('build'),
    )
    return HardwareAdapter(device_config)


@mock.patch('device_adapter.device.hardware_adapter.shutil.which')
def test_if_get_command_returns_proper_string_1(patched_which, device: HardwareAdapter) -> None:
    patched_which.return_value = 'west'
    device.generate_command()
    assert isinstance(device.command, list)
    assert device.command == ['west', 'flash', '--skip-rebuild', '--build-dir', 'build', '--runner', 'runner']
