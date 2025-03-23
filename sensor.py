"""Support for fake laundry sensors."""
from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.helpers.typing import EventType, StateType

from .const import (
    ATTR_CURRENT,
    ATTR_POWER,
    ATTR_STATE,
    ATTR_VOLTAGE,
    CONF_CURRENT_SENSOR,
    CONF_POWER_SENSOR,
    CONF_VOLTAGE_SENSOR,
    DOMAIN,
    STATE_IDLE,
    STATE_RUNNING,
    STATE_FINISHED,
)

_LOGGER = logging.getLogger(__name__)

# Power threshold in watts to determine if the machine is running
POWER_THRESHOLD = 10
# Time in minutes to consider the cycle finished after power drops below threshold
FINISH_DELAY = 2


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the fake laundry sensor."""
    name = config_entry.data[CONF_NAME]
    current_sensor = config_entry.data[CONF_CURRENT_SENSOR]
    voltage_sensor = config_entry.data[CONF_VOLTAGE_SENSOR]
    power_sensor = config_entry.data[CONF_POWER_SENSOR]

    async_add_entities(
        [
            FakeLaundrySensor(
                name, current_sensor, voltage_sensor, power_sensor, hass
            )
        ]
    )


class FakeLaundrySensor(SensorEntity):
    """Representation of a Fake Laundry sensor."""

    _attr_should_poll = False
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self,
        name: str,
        current_sensor: str,
        voltage_sensor: str,
        power_sensor: str,
        hass: HomeAssistant,
    ) -> None:
        """Initialize the sensor."""
        self._attr_name = name
        self._attr_unique_id = f"{DOMAIN}_{name}"
        self._current_sensor = current_sensor
        self._voltage_sensor = voltage_sensor
        self._power_sensor = power_sensor
        self._hass = hass
        self._state = STATE_IDLE
        self._finish_timer = None
        self._attr_extra_state_attributes = {
            ATTR_STATE: STATE_IDLE,
            ATTR_CURRENT: None,
            ATTR_VOLTAGE: None,
            ATTR_POWER: None,
        }

    async def async_added_to_hass(self) -> None:
        """Register callbacks."""
        self.async_on_remove(
            async_track_state_change_event(
                self._hass,
                [self._current_sensor, self._voltage_sensor, self._power_sensor],
                self._async_sensor_changed,
            )
        )

    @callback
    def _async_sensor_changed(self, event: EventType) -> None:
        """Handle sensor state changes."""
        new_state = event.data.get("new_state")
        if new_state is None:
            return

        # Update the corresponding attribute
        entity_id = event.data["entity_id"]
        try:
            value = float(new_state.state)
            if entity_id == self._current_sensor:
                self._attr_extra_state_attributes[ATTR_CURRENT] = value
            elif entity_id == self._voltage_sensor:
                self._attr_extra_state_attributes[ATTR_VOLTAGE] = value
            elif entity_id == self._power_sensor:
                self._attr_extra_state_attributes[ATTR_POWER] = value
                self._handle_power_change(value)
        except ValueError:
            _LOGGER.warning("Could not parse sensor value: %s", new_state.state)

        self.async_write_ha_state()

    @callback
    def _handle_power_change(self, power: float) -> None:
        """Handle changes in power consumption."""
        if power > POWER_THRESHOLD:
            if self._state != STATE_RUNNING:
                self._state = STATE_RUNNING
                self._attr_extra_state_attributes[ATTR_STATE] = STATE_RUNNING
                if self._finish_timer:
                    self._finish_timer()
                    self._finish_timer = None
        elif self._state == STATE_RUNNING:
            # Start the finish timer
            if not self._finish_timer:
                self._finish_timer = self._hass.loop.call_later(
                    FINISH_DELAY * 60, self._finish_cycle
                )

    @callback
    def _finish_cycle(self) -> None:
        """Mark the cycle as finished."""
        self._state = STATE_FINISHED
        self._attr_extra_state_attributes[ATTR_STATE] = STATE_FINISHED
        self._finish_timer = None
        self.async_write_ha_state()

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        return self._state
