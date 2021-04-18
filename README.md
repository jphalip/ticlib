`ticlib` is a pure-Python library to drive [Pololu Tic stepper motor controllers](https://www.pololu.com/category/212/tic-stepper-motor-controllers)
over a serial, I²C, or USB connection.

# Example code

```python
from src.ticlib import TicUSB
from time import sleep

tic = TicUSB()

tic.halt_and_set_position(0)
tic.energize()
tic.exit_safe_start()

positions = [500, 300, 800, 0]
for position in positions:
    tic.set_target_position(position)
    while tic.get_current_position() != tic.get_target_position():
        sleep(0.1)

tic.deenergize()
tic.enter_safe_start()
```

# Available controllers

## Serial

The serial controller has a dependency on the [pyserial](https://pypi.org/project/pyserial/) library.

Example:

```python
import serial
from src.ticlib import TicSerial

port_name = "/dev/ttyS0"
baud_rate = 9600
port = serial.Serial(port_name, baud_rate, timeout=0.1, write_timeout=0.1)

tic = TicSerial(port)
```

Instantiation parameters for `TicSerial`:

- `port` (required): Serial port used to communicate with the Tic.
- `device_number` (optional): Number of the device that you want to control. Use this if you have multiple devices
  connected to your serial line. Defaults to `None`.
- `crc_for_commands` (optional): If `True`, the library will append a CRC byte to every command sent to the Tic. Set
  this to `True` if your Tic's "Enable CRC for commands" setting is turned on. Defaults to `False`.
- `crc_for_responses` (optional): If `True`, the library will expect a CRC byte at the end of every response returned
  by the Tic. Set this to `True` if your Tic's "Enable CRC for responses" setting is turned on. Defaults to `False`.

For more details, see Pololu's official documentation on [serial command encoding](https://www.pololu.com/docs/0J71/9).


## I²C

The I²C controller has a dependency on the [smbus2](https://pypi.org/project/smbus2/) library.

Example:

```python
from smbus2 import SMBus
from src.ticlib import TicI2C

bus = SMBus(3)
address = 14

tic = TicI2C(bus, address)
```

Instantiation parameters for `TicI2C`:

- `bus` (required): Your Tic's I²C bus. For example, `SMBus(3)` represents `/dev/i2c-3`.
- `address` (required): Address of the Tic, that is its device number.

Note: If you use a Raspberry Pi, make sure to follow the workaround described in the [Pololu documentation](https://www.pololu.com/docs/0J71/12.8).

For more details, see Pololu's official documentation on [I²C command encoding](https://www.pololu.com/docs/0J71/10).

## USB

The USB controller has a dependency on the [pyusb](https://pypi.org/project/pyusb/) library.

Example:

```python
from src.ticlib import TicUSB

tic = TicUSB()
```

Instantiation parameters for `TicUSB`:

- `product` (optional): USB product ID for your Tic. If `None`, the device will be automatically detected. Use this if
  multiple Tic devices are connected to your computer. The available options are: `TIC_T825` (`0x00b3`), `TIC_T834`
  (`0x00b5`), `TIC_T500` (`0x00bd`), `TIC_N825` (`0x00c3`), `TIC_T249` (`0x00c9`), and `TIC_36v4` (`0x00cb`). Defaults
  to `None`.
- `serial_number` (optional): The serial number (in string format) of your Tic. If `None`, the device will be
  automatically detected. Use this if multiple Tic devices are connected to your computer. Default to `None`.

For more details, see Pololu's official documentation on [USB command encoding](https://www.pololu.com/docs/0J71/11).

# Commands:

Available commands:

```python
tic.clear_driver_error()
tic.deenergize()
tic.energize()
tic.enter_safe_start()
tic.exit_safe_start()
tic.go_home(value)
tic.halt_and_hold()
tic.halt_and_set_position(value)
tic.reset()
tic.reset_command_timeout()
tic.set_agc_option(value)
tic.set_current_limit(value)
tic.set_decay_mode(value)
tic.set_max_acceleration(value)
tic.set_max_deceleration(value)
tic.set_max_speed(value)
tic.set_starting_speed(value)
tic.set_step_mode(value)
tic.set_target_position(value)
tic.set_target_velocity(value)
```

For more details, see the official [command reference](https://www.pololu.com/docs/0J71/8).

# Variables

Available variables:

```python
# General status  -------------------------------------
tic.get_error_occured()
tic.get_error_status()
tic.get_misc_flags()
tic.get_operation_state()

# Step planning ---------------------------------------
tic.get_acting_target_position()
tic.get_current_position()
tic.get_current_velocity()
tic.get_max_acceleration()
tic.get_max_deceleration()
tic.get_max_speed()
tic.get_planning_mode()
tic.get_starting_speed()
tic.get_target_position()
tic.get_target_velocity()
tic.get_time_since_last_step()

# Other -----------------------------------------------
tic.get_analog_reading_rx()
tic.get_analog_reading_scl()
tic.get_analog_reading_sda()
tic.get_analog_reading_tx()
tic.get_current_limit()
tic.get_decay_mode()
tic.get_device_reset()
tic.get_digital_readings()
tic.get_encoder_position()
tic.get_input_after_averaging()
tic.get_input_after_hysteresis()
tic.get_input_after_scaling()
tic.get_input_state()
tic.get_pin_states()
tic.get_rc_pulse()
tic.get_step_mode()
tic.get_vin_voltage()
tic.get_uptime()

# T249-only -------------------------------------------
tic.get_agc_bottom_current_limit()
tic.get_agc_current_boost_steps()
tic.get_agc_frequency_limit()
tic.get_agc_mode()
tic.get_last_motor_driver_error()

# 36v4-only -------------------------------------------
tic.get_last_hp_driver_errors()
```

For more details, see the official [variable reference](https://www.pololu.com/docs/0J71/7).

# Settings

Available settings:

```python
tic.settings.get_control_mode()

# Miscellaneous -------------------------------------------------
tic.settings.get_auto_clear_driver_error()
tic.settings.get_disable_safe_start()
tic.settings.get_ignore_err_line_high()
tic.settings.get_never_sleep()
tic.settings.get_vin_calibration()

# Soft error response -------------------------------------------
tic.settings.get_current_limit_during_error()
tic.settings.get_soft_error_position()
tic.settings.get_soft_error_response()

# Serial --------------------------------------------------------
tic.settings.get_serial_7bit_responses()
tic.settings.get_serial_14bit_device_number()
tic.settings.get_serial_alt_device_number()
tic.settings.get_serial_baud_rate()
tic.settings.get_serial_command_timeout()
tic.settings.get_serial_crc_for_commands()
tic.settings.get_serial_crc_for_responses()
tic.settings.get_serial_device_number()
tic.settings.get_serial_enable_alt_device_number()
tic.settings.get_serial_response_delay()

# Encoder -------------------------------------------------------
tic.settings.get_encoder_postscaler()
tic.settings.get_encoder_prescaler()
tic.settings.get_encoder_unlimited()

# Input conditioning --------------------------------------------
tic.settings.get_input_averaging_enabled()
tic.settings.get_input_hysteresis()

# RC and analog scaling -----------------------------------------
tic.settings.get_input_invert()
tic.settings.get_input_max()
tic.settings.get_input_min()
tic.settings.get_input_neutral_max()
tic.settings.get_input_neutral_min()
tic.settings.get_input_scaling_degree()
tic.settings.get_output_max()
tic.settings.get_output_min()

# Pin Configuration ---------------------------------------------
# SCL
tic.settings.get_scl_active_high()
tic.settings.get_scl_config()
tic.settings.get_scl_enable_analog()
tic.settings.get_scl_enable_pull_up()
tic.settings.get_scl_kill_switch()
tic.settings.get_scl_limit_switch_forward()
tic.settings.get_scl_limit_switch_reverse()
tic.settings.get_scl_pin_function()
# SDA
tic.settings.get_sda_active_high()
tic.settings.get_sda_config()
tic.settings.get_sda_enable_analog()
tic.settings.get_sda_enable_pull_up()
tic.settings.get_sda_kill_switch()
tic.settings.get_sda_limit_switch_forward()
tic.settings.get_sda_limit_switch_reverse()
tic.settings.get_sda_pin_function()
# TX
tic.settings.get_tx_active_high()
tic.settings.get_tx_config()
tic.settings.get_tx_enable_analog()
tic.settings.get_tx_kill_switch()
tic.settings.get_tx_limit_switch_forward()
tic.settings.get_tx_limit_switch_reverse()
tic.settings.get_tx_pin_function()
# RX
tic.settings.get_rx_active_high()
tic.settings.get_rx_config()
tic.settings.get_rx_enable_analog()
tic.settings.get_rx_kill_switch()
tic.settings.get_rx_limit_switch_forward()
tic.settings.get_rx_limit_switch_reverse()
tic.settings.get_rx_pin_function()
# RC
tic.settings.get_rc_active_high()
tic.settings.get_rc_config()
tic.settings.get_rc_kill_switch()
tic.settings.get_rc_limit_switch_forward()
tic.settings.get_rc_limit_switch_reverse()

# Motor ---------------------------------------------------------
tic.settings.get_current_limit()
tic.settings.get_decay_mode()
tic.settings.get_invert_motor_direction()
tic.settings.get_max_acceleration()
tic.settings.get_max_deceleration()
tic.settings.get_max_speed()
tic.settings.get_starting_speed()
tic.settings.get_step_mode()

# Homing --------------------------------------------------------
tic.settings.get_auto_homing()
tic.settings.get_auto_homing_forward()
tic.settings.get_homing_speed_away()
tic.settings.get_homing_speed_towards()

# T249-only -----------------------------------------------------
tic.settings.get_agc_bottom_current_limit()
tic.settings.get_agc_current_boost_steps()
tic.settings.get_agc_mode()
tic.settings.get_agc_frequency_limit()

# 36v4-only -----------------------------------------------------
tic.settings.get_hp_current_trip_blanking_time()
tic.settings.get_hp_decay_mode()
tic.settings.get_hp_enable_adaptive_blanking_time()
tic.settings.get_hp_enable_unrestricted_current_limits()
tic.settings.get_hp_fixed_off_time()
tic.settings.get_hp_mixed_decay_transition_time()
```

Modifying settings is currently not supported.

For more details, see the official [settings reference](https://www.pololu.com/docs/0J71/6).