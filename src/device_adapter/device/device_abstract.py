from __future__ import annotations

import abc
import logging
import os
from typing import Generator

from device_adapter.device_adapter_config import DeviceConfig

logger = logging.getLogger(__name__)


class DeviceAbstract(abc.ABC):
    """Class defines an interface for all devices."""

    def __init__(self, device_config: DeviceConfig, **kwargs) -> None:
        """
        :param device_config: device configuration
        """
        self.device_config: DeviceConfig = device_config

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}()'

    @property
    def env(self) -> dict[str, str]:
        env = os.environ.copy()
        return env

    @abc.abstractmethod
    def connect(self, timeout: float = 1) -> None:
        """Connect with the device (e.g. via UART)"""

    @abc.abstractmethod
    def disconnect(self) -> None:
        """Close a connection with the device"""

    @abc.abstractmethod
    def generate_command(self) -> None:
        """
        Generate command which will be used during flashing or running device.

        :param build_dir: path to directory with built application
        """

    def flash_and_run(self) -> None:
        """
        Flash and run application on a device.

        :param timeout: time out in seconds
        """

    @property
    @abc.abstractmethod
    def iter_stdout(self) -> Generator[str, None, None]:
        """Iterate stdout from a device."""

    def stop(self) -> None:
        """Stop device."""
