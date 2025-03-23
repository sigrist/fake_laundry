"""Config flow for the Fake Laundry integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers import selector
from homeassistant.exceptions import HomeAssistantError

from .const import (
    DOMAIN,
    DEFAULT_NAME,
    CONF_CURRENT_SENSOR,
    CONF_VOLTAGE_SENSOR,
    CONF_POWER_SENSOR,
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME, default=DEFAULT_NAME): str,
        vol.Required(CONF_CURRENT_SENSOR): selector.EntitySelector(
            selector.EntitySelectorConfig(domain="sensor")
        ),
        vol.Required(CONF_VOLTAGE_SENSOR): selector.EntitySelector(
            selector.EntitySelectorConfig(domain="sensor")
        ),
        vol.Required(CONF_POWER_SENSOR): selector.EntitySelector(
            selector.EntitySelectorConfig(domain="sensor")
        ),
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    # Validate that all sensors exist
    for sensor in [
        data[CONF_CURRENT_SENSOR],
        data[CONF_VOLTAGE_SENSOR],
        data[CONF_POWER_SENSOR],
    ]:
        if not hass.states.get(sensor):
            raise CannotConnect(f"Sensor {sensor} not found")

    return {"title": data[CONF_NAME]}


class FakeLaundryConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Fake Laundry."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
                return self.async_create_entry(title=info["title"], data=user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""
