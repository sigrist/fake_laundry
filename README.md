# Fake Laundry

A Home Assistant integration that simulates a laundry machine's behavior by monitoring power consumption sensors.

## Features

- Monitors current, voltage, and power sensors
- Detects when the machine is running based on power consumption
- Provides machine state: idle, running, or finished
- Updates sensor values in real-time

## Installation

### HACS Installation (Recommended)

1. Make sure [HACS](https://hacs.xyz/) is installed in your Home Assistant instance
2. Add this repository to HACS:
   - Click on HACS in the sidebar
   - Click on "Integrations"
   - Click the three dots in the top right corner
   - Click "Custom repositories"
   - Add `sigrist/fake_laundry` as a repository
   - Select "Integration" as the category
3. Click "Download" on the Fake Laundry integration
4. Restart Home Assistant

### Manual Installation

1. Copy the `custom_components/fake_laundry` directory to your Home Assistant's `custom_components` directory
2. Restart Home Assistant

## Configuration

1. Go to Settings > Devices & Services
2. Click "Add Integration"
3. Search for "Fake Laundry"
4. Select the sensors for:
   - Current (in Amps)
   - Voltage (in Volts)
   - Power (in Watts)

## Usage

The integration will create a sensor entity that shows the current state of your laundry machine (idle/running/finished) based on the power consumption. The sensor's attributes will include the current values from all monitored sensors.
