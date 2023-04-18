from __future__ import annotations

import datetime
import logging
import os
import shutil
from pathlib import Path

import pytest

from device_adapter.device_adapter_config import DeviceAdapterConfig
from device_adapter.log import configure_logging

logger = logging.getLogger(__name__)

pytest_plugins = (
    'device_adapter.fixtures.dut'
)


def pytest_addoption(parser: pytest.Parser):
    device_adapter_group = parser.getgroup('Device adapter')
    device_adapter_group.addoption(
        '--device-adapter',
        action='store_true',
        default=False,
        help='Activate Device adapter plugin'
    )
    parser.addini(
        'device_adapter',
        'Activate Device adapter plugin',
        type='bool'
    )
    device_adapter_group.addoption(
        '--clear',
        dest='clear',
        action='store',
        default='archive',
        choices=('no', 'delete', 'archive'),
        help='Clear Device adapter artifacts. '
             '"no" - use previous artifacts, '
             '"delete" - delete previous artifacts, '
             '"archive" - keep previous artifacts '
             '(default=%(default)s)'
    )
    device_adapter_group.addoption(
        '-O',
        '--outdir',
        metavar='PATH',
        dest='output_dir',
        default='device_adapter_out',
        help='output directory for logs and binaries (default: %(default)s)'
    )
    device_adapter_group.addoption(
        '--platform',
        help='Choose specific platform'
    )
    device_adapter_group.addoption(
        '--device-type',
        help='Choose type of device (hardware, qemu, etc.)'
    )
    device_adapter_group.addoption(
        '--device-serial',
        help='Serial device for accessing the board '
             '(e.g., /dev/ttyACM0)'
    )
    device_adapter_group.addoption(
        '--device-serial-baud',
        type=int,
        default=115200,
        help='Serial device baud rate (default 115200)'
    )
    device_adapter_group.addoption(
        '--runner',
        help='use the specified west runner (pyocd, nrfjprog, etc)'
    )
    device_adapter_group.addoption(
        '--device-id',
        help='ID of connected hardware device (for example 000682459367)'
    )
    device_adapter_group.addoption(
        '--device-product',
        help='Product name of connected hardware device (for example "STM32 STLink")'
    )
    device_adapter_group.addoption(
        '--device-serial-pty',
        metavar='PATH',
        help='Script for controlling pseudoterminal. '
             'E.g --device-testing --device-serial-pty=<script>'
    )
    device_adapter_group.addoption(
        '--west-flash-extra-args',
        help='Extend parameters for west flash. '
             'E.g. --west-flash-extra-args="--board-id=foobar,--erase" '
             'will translate to "west flash -- --board-id=foobar --erase"'
    )
    device_adapter_group.addoption(
        '--flashing-timeout',
        type=int,
        default=60,
        help='Set timeout for the device flash operation in seconds.'
    )
    device_adapter_group.addoption(
        '--build-dir',
        metavar='PATH',
        help='Directory with built application.'
    )
    device_adapter_group.addoption(
        '--binary-file',
        metavar='PATH',
        help='Path to file which should be flashed.'
    )


def pytest_configure(config: pytest.Config):
    if config.getoption('help'):
        return

    if not (config.getoption('device_adapter') or config.getini('device_adapter')):
        return

    validate_options(config)

    config.option.output_dir = _normalize_path(config.option.output_dir)

    xdist_worker = hasattr(config, 'workerinput')  # xdist worker

    if not xdist_worker:
        run_artifactory_cleanup(config)

    # create output directory if not exists
    os.makedirs(config.option.output_dir, exist_ok=True)

    configure_logging(config)

    config.device_adapter_config = DeviceAdapterConfig.create(config)  # type: ignore


def validate_options(config: pytest.Config) -> None:
    """Verify if user provided proper options"""
    # TBD


def run_artifactory_cleanup(config: pytest.Config) -> None:
    """Clean, archive or delete an output dir. If load test file
    is in impacted directory, backup them or update path"""
    if os.path.exists(config.option.output_dir) is False:
        return

    choice = config.option.clear
    output_dir = config.option.output_dir
    if choice == 'no':
        print('Keeping previous artifacts untouched')
    elif choice == 'delete':
        print(f'Deleting previous artifacts from {output_dir}')
        shutil.rmtree(output_dir, ignore_errors=True)
    elif choice == 'archive':
        timestamp = os.path.getmtime(output_dir)
        file_date = datetime.datetime.fromtimestamp(timestamp).strftime('%y%m%d%H%M%S')
        new_output_dir = f'{output_dir}_{file_date}'
        print(f'Renaming output directory to {new_output_dir}')
        shutil.move(str(output_dir), new_output_dir)


def _normalize_path(path: str | Path) -> str:
    path = os.path.expanduser(os.path.expandvars(path))
    path = os.path.normpath(os.path.abspath(path))
    return path
