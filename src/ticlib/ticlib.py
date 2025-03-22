# BSD 2-Clause License
#
# Copyright (c) 2021, Julien Phalip
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

__all__ = [
    'TicSerial', 'TicI2C', 'TicUSB', 'SMBus2Backend', 'MachineI2CBackend',
    'TIC_T825', 'TIC_T834', 'TIC_T500', 'TIC_N825', 'TIC_T249', 'TIC_36v4'
]

import sys
from typing import TYPE_CHECKING

if sys.implementation.name == 'micropython':
    def partial(function, *args):
        """
        Substitute to Python's `functools.partial`
        """
        def _partial(*extra_args):
            return function(*(args + extra_args))
        return _partial
else:
    from functools import partial

try:
    from machine import I2C as machine_i2c
except ImportError:
    machine_i2c = None

try:
    from smbus2 import i2c_msg
except ImportError:
    i2c_msg = None

try:
    import serial
except ImportError:
    serial = None

try:
    import usb.core as usb_core
except ImportError:
    usb_core = None


class MachineI2CBackend(object):
    """
    I2C backend that acts as a wrapper around the `machine.I2C` class.
    """

    def __init__(self, i2c, address):
        if machine_i2c is None:
            raise Exception("Missing dependency: machine.I2C (Micropython)")
        self.i2c = i2c
        self.address = address

    def read(self, length):
        return self.i2c.readfrom(self.address, length)

    def write(self, serialized):
        self.i2c.writeto(self.address, serialized)


class SMBus2Backend(object):
    """
    I2C Backend that uses the smbus2 library.
    """

    def __init__(self, bus, address):
        if i2c_msg is None:
            raise Exception("Missing dependency: smbus2")
        self.address = address
        self.bus = bus

    def read(self, length):
        read = i2c_msg.read(self.address, length)
        self.bus.i2c_rdwr(read)
        return read.__bytes__()[0: length]

    def write(self, serialized):
        write = i2c_msg.write(self.address, serialized)
        self.bus.i2c_rdwr(write)


# Output formatting functions ---------------------------------------------------

def boolean(bit_index, value):
    """
    Returns `True` if the bit located at `bit_index` in the given `value` is set. Returns `False` otherwise.
    The least-significant bit is at index 0.
    """
    int_value = int.from_bytes(bytearray(value), 'little')
    return (int_value & (1 << bit_index)) != 0


def bit_range(start, end, value):
    """
    Returns the bits between the `start` and `end` indices in the byte `value`.
    """
    int_value = int.from_bytes(bytearray(value), 'little')
    binary = bin(int_value)
    # Remove first two characters
    binary = binary[2:]
    # Extract bits
    bits = ''.join(reversed(''.join(reversed(binary))[start:end + 1]))  # Use "reversed()" instead of the less verbose [::-1] to be compatible with micropython
    # Convert to int
    return int(bits, 2)


def signed_int(value):
    """
    Converts the given byte value to a signed integer.
    """
    result = int.from_bytes(bytearray(value), 'little')
    num_bytes = len(value)
    if result >= (1 << (num_bytes * 8 - 1)):
        result -= (1 << (num_bytes * 8))
    return result


def unsigned_int(value):
    """
    Converts the given byte value to an unsigned integer.
    """
    return int.from_bytes(bytearray(value), 'little')


# USB IDs ---------------------------------------------------
VENDOR = 0x1ffb  # Pololu's vendor ID
TIC_T825 = 0x00b3
TIC_T834 = 0x00b5
TIC_T500 = 0x00bd
TIC_N825 = 0x00c3
TIC_T249 = 0x00c9
TIC_36v4 = 0x00cb


# Commands ---------------------------------------------------

# Command input formats:
QUICK = 'QUICK'
THIRTY_TWO_BITS = 'THIRTY_TWO_BITS'
SEVEN_BITS = 'SEVEN_BITS'
BLOCK_READ = 'BLOCK_READ'


# See list of commands in the official documentation: https://www.pololu.com/docs/0J71/8
COMMANDS = [
    ('set_target_position', 0xE0, THIRTY_TWO_BITS),
    ('set_target_velocity', 0xE3, THIRTY_TWO_BITS),
    ('halt_and_set_position', 0xEC, THIRTY_TWO_BITS),
    ('halt_and_hold', 0x89, QUICK),
    ('go_home', 0x97, SEVEN_BITS),
    ('reset_command_timeout', 0x8C, QUICK),
    ('deenergize', 0x86, QUICK),
    ('energize', 0x85, QUICK),
    ('exit_safe_start', 0x83, QUICK),
    ('enter_safe_start', 0x8F, QUICK),
    ('reset', 0xB0, QUICK),
    ('clear_driver_error', 0x8A, QUICK),
    ('set_max_speed', 0xE6, THIRTY_TWO_BITS),
    ('set_starting_speed', 0xE5, THIRTY_TWO_BITS),
    ('set_max_acceleration', 0xEA, THIRTY_TWO_BITS),
    ('set_max_deceleration', 0xE9, THIRTY_TWO_BITS),
    ('set_step_mode', 0x94, SEVEN_BITS),
    ('set_current_limit', 0x91, THIRTY_TWO_BITS),
    ('set_decay_mode', 0x92, SEVEN_BITS),
    ('set_agc_option', 0x98, SEVEN_BITS),
]

GET_VARIABLE_CMD = 0xA1
GET_SETTING_CMD = 0xA8


# Variables ---------------------------------------------------

# See list of variables in the official documentation: https://www.pololu.com/docs/0J71/7
VARIABLES = [
    # General status  -------------------------------------
    ('operation_state', 0x00, 1, unsigned_int),
    ('misc_flags', 0x01, 1, None),
    ('error_status', 0x02, 2, None),
    ('error_occured', 0x04, 4, None),

    # Step planning ---------------------------------------
    ('planning_mode', 0x09, 1, unsigned_int),
    ('target_position', 0x0A, 4, signed_int),
    ('target_velocity', 0x0E, 4, signed_int),
    ('starting_speed', 0x12, 4, unsigned_int),
    ('max_speed', 0x16, 4, unsigned_int),
    ('max_deceleration', 0x1A, 4, unsigned_int),
    ('max_acceleration', 0x1E, 4, unsigned_int),
    ('current_position', 0x22, 4, signed_int),
    ('current_velocity', 0x26, 4, signed_int),
    ('acting_target_position', 0x2A, 4, signed_int),
    ('time_since_last_step', 0x2E, 4, unsigned_int),

    # Other -----------------------------------------------
    ('device_reset', 0x32, 1, unsigned_int),
    ('vin_voltage', 0x33, 2, unsigned_int),
    ('uptime', 0x35, 4, unsigned_int),
    ('encoder_position', 0x39, 4, signed_int),
    ('rc_pulse', 0x3D, 2, unsigned_int),
    ('analog_reading_scl', 0x3F, 2, unsigned_int),
    ('analog_reading_sda', 0x41, 2, unsigned_int),
    ('analog_reading_tx', 0x43, 2, unsigned_int),
    ('analog_reading_rx', 0x45, 2, unsigned_int),
    ('digital_readings', 0x47, 1, None),
    ('pin_states', 0x48, 1, None),
    ('step_mode', 0x49, 1, unsigned_int),
    ('current_limit', 0x4A, 1, unsigned_int),
    ('decay_mode', 0x4B, 1, unsigned_int),  # Not valid for 36v4
    ('input_state', 0x4C, 1, unsigned_int),
    ('input_after_averaging', 0x4D, 2, unsigned_int),
    ('input_after_hysteresis', 0x4F, 2, unsigned_int),
    ('input_after_scaling', 0x51, 4, signed_int),

    # T249-only -------------------------------------------
    ('last_motor_driver_error', 0x55, 1, unsigned_int),
    ('agc_mode', 0x56, 1, unsigned_int),
    ('agc_bottom_current_limit', 0x57, 1, unsigned_int),
    ('agc_current_boost_steps', 0x58, 1, unsigned_int),
    ('agc_frequency_limit', 0x59, 1, unsigned_int),

    # 36v4-only -------------------------------------------
    ('last_hp_driver_errors', 0xFF, 1, None),
]


# Settings ---------------------------------------------------

# See list of settings in the official documentation: https://www.pololu.com/docs/0J71/6
SETTINGS = [
    ('control_mode', 0x01, 1, unsigned_int),

    # Miscellaneous -------------------------------------------------
    ('disable_safe_start', 0x03, 1, partial(boolean, 0)),
    ('ignore_err_line_high', 0x04, 1, partial(boolean, 0)),
    ('auto_clear_driver_error', 0x08, 1, partial(boolean, 0)),
    ('never_sleep', 0x02, 1, partial(boolean, 0)),
    ('vin_calibration', 0x14, 2, signed_int),

    # Soft error response -------------------------------------------
    ('soft_error_response', 0x53, 1, unsigned_int),
    ('soft_error_position', 0x54, 4, signed_int),
    ('current_limit_during_error', 0x31, 1, unsigned_int),

    # Serial --------------------------------------------------------
    ('serial_baud_rate', 0x06, 2, unsigned_int),  # Returns odd result
    ('serial_enable_alt_device_number', 0x6A, 1, partial(boolean, 7)),
    ('serial_14bit_device_number', 0x0B, 1, partial(boolean, 3)),
    ('serial_response_delay', 0x5E, 1, unsigned_int),
    ('serial_command_timeout', 0x09, 2, unsigned_int),
    ('serial_crc_for_commands', 0x0B, 1, partial(boolean, 0)),
    ('serial_crc_for_responses', 0x0B, 1, partial(boolean, 1)),
    ('serial_7bit_responses', 0x0B, 1, partial(boolean, 2)),
    # Note: The device number and alternative device number settings are defined in the TicSerial class

    # Encoder -------------------------------------------------------
    ('encoder_prescaler', 0x58, 4, unsigned_int),
    ('encoder_postscaler', 0x37, 4, unsigned_int),
    ('encoder_unlimited', 0x5C, 1, partial(boolean, 0)),

    # Input conditioning --------------------------------------------
    ('input_averaging_enabled', 0x2E, 1, partial(boolean, 0)),
    ('input_hysteresis', 0x2F, 2, unsigned_int),

    # RC and analog scaling -----------------------------------------
    ('input_invert', 0x21, 1, partial(boolean, 0)),
    ('input_max', 0x28, 2, unsigned_int),
    ('output_max', 0x32, 4, signed_int),
    ('input_neutral_max', 0x26, 2, unsigned_int),
    ('input_neutral_min', 0x24, 2, unsigned_int),
    ('input_min', 0x22, 2, unsigned_int),
    ('output_min', 0x2A, 4, signed_int),
    ('input_scaling_degree', 0x20, 1, unsigned_int),

    # Pin Configuration ---------------------------------------------
    # SCL
    ('scl_config', 0x3B, 1, None),
    ('scl_pin_function', 0x3B, 1, partial(bit_range, 0, 3)),
    ('scl_enable_analog', 0x3B, 1, partial(boolean, 6)),
    ('scl_enable_pull_up', 0x3B, 1, partial(boolean, 7)),
    ('scl_active_high', 0x36, 1, partial(boolean, 0)),
    ('scl_kill_switch', 0x5D, 1, partial(boolean, 0)),
    ('scl_limit_switch_forward', 0x5F, 1, partial(boolean, 0)),
    ('scl_limit_switch_reverse', 0x60, 1, partial(boolean, 0)),
    # SDA
    ('sda_config', 0x3C, 1, None),
    ('sda_pin_function', 0x3C, 1, partial(bit_range, 0, 3)),
    ('sda_enable_analog', 0x3C, 1, partial(boolean, 6)),
    ('sda_enable_pull_up', 0x3C, 1, partial(boolean, 7)),
    ('sda_active_high', 0x36, 1, partial(boolean, 1)),
    ('sda_kill_switch', 0x5D, 1, partial(boolean, 1)),
    ('sda_limit_switch_forward', 0x5F, 1, partial(boolean, 1)),
    ('sda_limit_switch_reverse', 0x60, 1, partial(boolean, 1)),
    # TX
    ('tx_config', 0x3D, 1, None),
    ('tx_pin_function', 0x3D, 1, partial(bit_range, 0, 3)),
    ('tx_enable_analog', 0x3D, 1, partial(boolean, 6)),
    ('tx_active_high', 0x36, 1, partial(boolean, 2)),
    ('tx_kill_switch', 0x5D, 1, partial(boolean, 2)),
    ('tx_limit_switch_forward', 0x5F, 1, partial(boolean, 2)),
    ('tx_limit_switch_reverse', 0x60, 1, partial(boolean, 2)),
    # RX
    ('rx_config', 0x3E, 1, None),
    ('rx_pin_function', 0x3E, 1, partial(bit_range, 0, 3)),
    ('rx_enable_analog', 0x3E, 1, partial(boolean, 6)),
    ('rx_active_high', 0x36, 1, partial(boolean, 3)),
    ('rx_kill_switch', 0x5D, 1, partial(boolean, 3)),
    ('rx_limit_switch_forward', 0x5F, 1, partial(boolean, 3)),
    ('rx_limit_switch_reverse', 0x60, 1, partial(boolean, 3)),
    # RC
    ('rc_config', 0x3F, 1, None),
    ('rc_active_high', 0x36, 1, partial(boolean, 4)),
    ('rc_kill_switch', 0x5D, 1, partial(boolean, 4)),
    ('rc_limit_switch_forward', 0x5F, 1, partial(boolean, 4)),
    ('rc_limit_switch_reverse', 0x60, 1, partial(boolean, 4)),

    # Motor ---------------------------------------------------------
    ('invert_motor_direction', 0x1B, 1, partial(boolean, 0)),
    ('max_speed', 0x47, 4, unsigned_int),
    ('starting_speed', 0x43, 4, unsigned_int),
    ('max_acceleration', 0x4F, 4, unsigned_int),
    ('max_deceleration', 0x4B, 4, unsigned_int),
    ('step_mode', 0x41, 1, unsigned_int),
    ('current_limit', 0x40, 1, unsigned_int),
    ('decay_mode', 0x42, 1, unsigned_int),

    # Homing --------------------------------------------------------
    ('auto_homing', 0x02, 1, partial(boolean, 1)),
    ('auto_homing_forward', 0x03, 1, partial(boolean, 2)),
    ('homing_speed_towards', 0x61, 4, unsigned_int),
    ('homing_speed_away', 0x65, 4, unsigned_int),

    # T249-only -----------------------------------------------------
    ('agc_mode', 0x6C, 1, unsigned_int),
    ('agc_bottom_current_limit', 0x6D, 1, unsigned_int),
    ('agc_current_boost_steps', 0x6E, 1, unsigned_int),
    ('agc_frequency_limit', 0x6F, 1, unsigned_int),

    # 36v4-only -----------------------------------------------------
    ('hp_enable_unrestricted_current_limits', 0x6C, 1, partial(boolean, 0)),
    ('hp_fixed_off_time', 0xF6, 1, unsigned_int),
    ('hp_current_trip_blanking_time', 0xF8, 1, unsigned_int),
    ('hp_enable_adaptive_blanking_time', 0xF9, 1, partial(boolean, 0)),
    ('hp_mixed_decay_transition_time', 0xFA, 1, unsigned_int),
    ('hp_decay_mode', 0xFB, 1, unsigned_int),
]


class Settings(object):
    """
    Class used to manage the Tic's settings.
    """

    def __init__(self, tic):
        self.tic = tic
        for setting in SETTINGS:
            name, offset, length, format_response = setting
            setattr(
                self,
                'get_' + name,
                partial(self.tic._block_read, GET_SETTING_CMD, offset, length, format_response))

    def get_serial_device_number(self):
        """
        Gets the serial device number from two separate bytes in the Tic's settings.
        """
        lower = self.tic._block_read(GET_SETTING_CMD, 0x07, 1)
        upper = self.tic._block_read(GET_SETTING_CMD, 0x69, 1)
        lower = bit_range(0, 6, lower)
        upper = bit_range(0, 6, upper)
        return (lower & 0x7F) | ((upper & 0x7F) << 7)

    def get_serial_alt_device_number(self):
        """
        Gets the alternative serial device number from two separate bytes in the Tic's settings.
        """
        lower = self.tic._block_read(GET_SETTING_CMD, 0x6A, 1)
        upper = self.tic._block_read(GET_SETTING_CMD, 0x6B, 1)
        lower = bit_range(0, 6, lower)
        upper = bit_range(0, 6, upper)
        return (lower & 0x7F) | ((upper & 0x7F) << 7)

    def get_all(self):
        """
        Returns all of the Tic's settings and their values.
        """
        result = {}
        for setting in SETTINGS:
            name, _, _, _ = setting
            result[name] = getattr(self, 'get_' + name)()
        result['serial_device_number'] = self.get_serial_device_number()
        result['serial_alt_device_number'] = self.get_serial_alt_device_number()
        return result
    if TYPE_CHECKING:
        #
        # Typed stub methods for each dynamically added "get_<setting>()" method.
        #
        def get_control_mode(self) -> int:
            '''
            Offset: 0x01
            Type: unsigned 8-bit
            Data:
              0: Serial / I2C / USB
              1: STEP/DIR
              2: RC position
              3: RC speed
              4: Analog position
              5: Analog speed
              6: Encoder position
              7: Encoder speed
            Default: 0 (Serial / I2C / USB)

            Determines the Tic's control mode. See Section 6 for details.
            '''
            ...

        def get_disable_safe_start(self) -> bool:
            '''
            Offset: bit 0 of byte 0x03
            Type: boolean
            Default: false

            If set, disables the safe start feature (Section 5.4).
            '''
            ...

        def get_ignore_err_line_high(self) -> bool:
            '''
            Offset: bit 0 of byte 0x04
            Type: boolean
            Default: false

            Disables the "ERR line high" error if set.
            '''
            ...

        def get_auto_clear_driver_error(self) -> bool:
            '''
            Offset: bit 0 of byte 0x08
            Type: boolean
            Default: true

            When enabled, the Tic will periodically clear latched motor driver errors (Section 5.4).
            '''
            ...

        def get_never_sleep(self) -> bool:
            '''
            Offset: bit 0 of byte 0x02
            Type: boolean
            Default: false

            Prevents the Tic from sleeping if USB power is present but VIN is not.
            '''
            ...

        def get_vin_calibration(self) -> int:
            '''
            Offset: 0x14
            Type: signed 16-bit
            Default: 0
            Range: -500 to +500

            Adjusts the scaling of the Tic's VIN readings. Positive values increase VIN measurement,
            negative values decrease it. Section 6 has more info on typical scale factors.
            '''
            ...

        def get_soft_error_response(self) -> int:
            '''
            Offset: 0x53
            Type: unsigned 8-bit
            Data:
              0: De-energize
              1: Halt and hold
              2: Decelerate to hold
              3: Go to position
            Default: 2 (Decelerate to hold)

            Determines what the Tic does on a soft error (Section 5.4).
            '''
            ...

        def get_soft_error_position(self) -> int:
            '''
            Offset: 0x54
            Type: signed 32-bit
            Default: 0
            Range: -2,147,483,648 to 2,147,483,647

            If "soft error response" is "Go to position", this is the position used.
            '''
            ...

        def get_current_limit_during_error(self) -> int:
            '''
            Offset: 0x31
            Type: unsigned 8-bit or 0xFF to disable
            Default: 0
            Range: 0 to normal current limit, or disabled

            If not 0xFF, the Tic uses a different current limit when a soft error is active.
            '''
            ...

        def get_serial_baud_rate(self) -> int:
            '''
            Offset: 0x06
            Type: unsigned 16-bit
            Default: 9600
            Range: 200 to 115385 bps

            The serial baud rate in bits per second. This corresponds to a "baud rate generator"
            value internally. See Section 6 for details.
            '''
            ...

        def get_serial_enable_alt_device_number(self) -> bool:
            '''
            Offset: bit 7 of byte 0x6A
            Type: boolean
            Default: false

            If set, the Tic responds to an alternative Pololu Protocol device number in addition
            to the main device number.
            '''
            ...

        def get_serial_14bit_device_number(self) -> bool:
            '''
            Offset: bit 3 of byte 0x0B
            Type: boolean
            Default: false

            Allows device numbers up to 16383 in Pololu Protocol commands (Section 9).
            '''
            ...

        def get_serial_response_delay(self) -> int:
            '''
            Offset: 0x5E
            Type: unsigned 8-bit
            Default: 0
            Range: 0 to 255 (microseconds)

            Minimum amount of time to wait before sending a serial response or processing an I2C byte.
            '''
            ...

        def get_serial_command_timeout(self) -> int:
            '''
            Offset: 0x09
            Type: unsigned 16-bit
            Default: 1000 ms
            Range: 0 to 60000 ms

            Timeout in ms before the Tic flags a "command timeout" error if no valid commands
            have been received. 0 disables the feature.
            '''
            ...

        def get_serial_crc_for_commands(self) -> bool:
            '''
            Offset: bit 0 of byte 0x0B
            Type: boolean
            Default: false

            If set, the Tic requires a 7-bit CRC on every incoming serial command (Section 9).
            '''
            ...

        def get_serial_crc_for_responses(self) -> bool:
            '''
            Offset: bit 1 of byte 0x0B
            Type: boolean
            Default: false

            If set, the Tic appends a 7-bit CRC to its serial responses (up to 14 bytes).
            '''
            ...

        def get_serial_7bit_responses(self) -> bool:
            '''
            Offset: bit 2 of byte 0x0B
            Type: boolean
            Default: false

            If set, the Tic encodes its serial responses with 7-bit bytes only.
            '''
            ...

        def get_encoder_prescaler(self) -> int:
            '''
            Offset: 0x58
            Type: unsigned 32-bit
            Default: 1
            Range: 1 to 2,147,483,647

            For encoder modes, sets how many encoder counts correspond to one unit of stepper movement.
            '''
            ...

        def get_encoder_postscaler(self) -> int:
            '''
            Offset: 0x37
            Type: unsigned 32-bit
            Default: 1
            Range: 1 to 2,147,483,647

            For encoder modes, sets the size of each unit of stepper motor position/speed.
            '''
            ...

        def get_encoder_unlimited(self) -> bool:
            '''
            Offset: bit 0 of 0x5C
            Type: boolean
            Default: false

            Enables unbounded position control if set. See Section 5.3.
            '''
            ...

        def get_input_averaging_enabled(self) -> bool:
            '''
            Offset: bit 0 of 0x2E
            Type: boolean
            Default: true

            Enables averaging for RC/analog inputs (Section 5.2).
            '''
            ...

        def get_input_hysteresis(self) -> int:
            '''
            Offset: 0x2F
            Type: unsigned 16-bit
            Default: 0
            Range: 0 to 65535

            Amount of hysteresis to apply to RC/analog inputs.
            '''
            ...

        def get_input_invert(self) -> bool:
            '''
            Offset: 0x21
            Type: boolean
            Default: false

            If true, inverts direction for RC/analog inputs (Section 5.2).
            '''
            ...

        def get_input_max(self) -> int:
            '''
            Offset: 0x28
            Type: unsigned 16-bit
            Default: 4095
            Range: 0 to 4095

            One of the RC/analog input scaling parameters (Section 5.2).
            '''
            ...

        def get_output_max(self) -> int:
            '''
            Offset: 0x32
            Type: signed 32-bit
            Default: 200
            Range: 0 to 2,147,483,647

            One of the RC/analog input scaling parameters (Section 5.2).
            '''
            ...

        def get_input_neutral_max(self) -> int:
            '''
            Offset: 0x26
            Type: unsigned 16-bit
            Default: 2080
            Range: 0 to 4095

            One of the RC/analog input scaling parameters (neutral zone upper bound).
            '''
            ...

        def get_input_neutral_min(self) -> int:
            '''
            Offset: 0x24
            Type: unsigned 16-bit
            Default: 2015
            Range: 0 to 4095

            One of the RC/analog input scaling parameters (neutral zone lower bound).
            '''
            ...

        def get_input_min(self) -> int:
            '''
            Offset: 0x22
            Type: unsigned 16-bit
            Default: 0
            Range: 0 to 4095

            One of the RC/analog input scaling parameters.
            '''
            ...

        def get_output_min(self) -> int:
            '''
            Offset: 0x2A
            Type: signed 32-bit
            Default: -200
            Range: -2,147,483,647 to 0

            One of the RC/analog input scaling parameters (target minimum).
            '''
            ...

        def get_input_scaling_degree(self) -> int:
            '''
            Offset: 0x20
            Type: unsigned 8-bit
            Data:
              0: linear
              1: quadratic
              2: cubic
            Default: 0 (linear)

            Determines polynomial degree for scaling RC/analog inputs (Section 5.2).
            '''
            ...

        def get_scl_config(self) -> int:
            '''
            Offset: 0x3B
            Type: 8-bit
            Default: 0

            Pin configuration for the SCL pin (I2C clock), including function, pull-up, analog mode, etc.
            '''
            ...

        def get_scl_pin_function(self) -> int:
            '''
            Offset: 0x3B
            Type: bits [0..3]
            Default: 0

            The pin function extracted from scl_config:
              0 = Default
              1 = User I/O
              2 = User input
              3 = Pot power
              4 = SCL
              7 = Kill switch
              8 = Limit switch forward
              9 = Limit switch reverse
            '''
            ...

        def get_scl_enable_analog(self) -> bool:
            '''
            Offset: bit 6 of 0x3B
            Type: boolean
            Default: false
            '''
            ...

        def get_scl_enable_pull_up(self) -> bool:
            '''
            Offset: bit 7 of 0x3B
            Type: boolean
            Default: false
            '''
            ...

        def get_scl_active_high(self) -> bool:
            '''
            Offset: bit 0 of 0x36
            Type: boolean
            Default: false

            If the SCL pin is a switch, determines if it is active high.
            '''
            ...

        def get_scl_kill_switch(self) -> bool:
            '''
            Offset: bit 0 of 0x5D
            Type: boolean
            Default: false

            If set, the SCL pin is mapped as a kill switch.
            '''
            ...

        def get_scl_limit_switch_forward(self) -> bool:
            '''
            Offset: bit 0 of 0x5F
            Type: boolean
            Default: false

            If set, the SCL pin is mapped as a forward limit switch.
            '''
            ...

        def get_scl_limit_switch_reverse(self) -> bool:
            '''
            Offset: bit 0 of 0x60
            Type: boolean
            Default: false

            If set, the SCL pin is mapped as a reverse limit switch.
            '''
            ...

        def get_sda_config(self) -> int:
            '''
            Offset: 0x3C
            Type: 8-bit
            Default: 0

            Pin configuration for the SDA pin (I2C data line).
            '''
            ...

        def get_sda_pin_function(self) -> int:
            '''
            Offset: 0x3C
            Type: bits [0..3]
            Default: 0

            Pin function for the SDA pin. See doc for values.
            '''
            ...

        def get_sda_enable_analog(self) -> bool:
            '''
            Offset: bit 6 of 0x3C
            Type: boolean
            Default: false
            '''
            ...

        def get_sda_enable_pull_up(self) -> bool:
            '''
            Offset: bit 7 of 0x3C
            Type: boolean
            Default: false
            '''
            ...

        def get_sda_active_high(self) -> bool:
            '''
            Offset: bit 1 of 0x36
            Type: boolean
            Default: false

            If the SDA pin is a switch, determines if it is active high.
            '''
            ...

        def get_sda_kill_switch(self) -> bool:
            '''
            Offset: bit 1 of 0x5D
            Type: boolean
            Default: false
            '''
            ...

        def get_sda_limit_switch_forward(self) -> bool:
            '''
            Offset: bit 1 of 0x5F
            Type: boolean
            Default: false
            '''
            ...

        def get_sda_limit_switch_reverse(self) -> bool:
            '''
            Offset: bit 1 of 0x60
            Type: boolean
            Default: false
            '''
            ...

        def get_tx_config(self) -> int:
            '''
            Offset: 0x3D
            Type: 8-bit
            Default: 0

            Pin configuration for the TX pin (serial transmit).
            '''
            ...

        def get_tx_pin_function(self) -> int:
            '''
            Offset: 0x3D
            Type: bits [0..3]
            Default: 0

            Pin function for the TX pin. See doc for values.
            '''
            ...

        def get_tx_enable_analog(self) -> bool:
            '''
            Offset: bit 6 of 0x3D
            Type: boolean
            Default: false
            '''
            ...

        def get_tx_active_high(self) -> bool:
            '''
            Offset: bit 2 of 0x36
            Type: boolean
            Default: false
            '''
            ...

        def get_tx_kill_switch(self) -> bool:
            '''
            Offset: bit 2 of 0x5D
            Type: boolean
            Default: false
            '''
            ...

        def get_tx_limit_switch_forward(self) -> bool:
            '''
            Offset: bit 2 of 0x5F
            Type: boolean
            Default: false
            '''
            ...

        def get_tx_limit_switch_reverse(self) -> bool:
            '''
            Offset: bit 2 of 0x60
            Type: boolean
            Default: false
            '''
            ...

        def get_rx_config(self) -> int:
            '''
            Offset: 0x3E
            Type: 8-bit
            Default: 0

            Pin configuration for the RX pin (serial receive).
            '''
            ...

        def get_rx_pin_function(self) -> int:
            '''
            Offset: 0x3E
            Type: bits [0..3]
            Default: 0

            Pin function for the RX pin. See doc for values.
            '''
            ...

        def get_rx_enable_analog(self) -> bool:
            '''
            Offset: bit 6 of 0x3E
            Type: boolean
            Default: false
            '''
            ...

        def get_rx_active_high(self) -> bool:
            '''
            Offset: bit 3 of 0x36
            Type: boolean
            Default: false
            '''
            ...

        def get_rx_kill_switch(self) -> bool:
            '''
            Offset: bit 3 of 0x5D
            Type: boolean
            Default: false
            '''
            ...

        def get_rx_limit_switch_forward(self) -> bool:
            '''
            Offset: bit 3 of 0x5F
            Type: boolean
            Default: false
            '''
            ...

        def get_rx_limit_switch_reverse(self) -> bool:
            '''
            Offset: bit 3 of 0x60
            Type: boolean
            Default: false
            '''
            ...

        def get_rc_config(self) -> int:
            '''
            Offset: 0x3F
            Type: 8-bit
            Default: 0

            Pin configuration for the RC pin (RC pulse input).
            '''
            ...

        def get_rc_active_high(self) -> bool:
            '''
            Offset: bit 4 of 0x36
            Type: boolean
            Default: false
            '''
            ...

        def get_rc_kill_switch(self) -> bool:
            '''
            Offset: bit 4 of 0x5D
            Type: boolean
            Default: false
            '''
            ...

        def get_rc_limit_switch_forward(self) -> bool:
            '''
            Offset: bit 4 of 0x5F
            Type: boolean
            Default: false
            '''
            ...

        def get_rc_limit_switch_reverse(self) -> bool:
            '''
            Offset: bit 4 of 0x60
            Type: boolean
            Default: false
            '''
            ...

        def get_invert_motor_direction(self) -> bool:
            '''
            Offset: bit 0 of 0x1B
            Type: boolean
            Default: false

            Reverses the motor direction if set.
            '''
            ...

        def get_max_speed(self) -> int:
            '''
            Offset: 0x47
            Type: unsigned 32-bit
            Default: 2000000
            Range: 0 to 500000000
            Units: microsteps per 10000 s

            Default maximum motor speed. Can be overridden at runtime.
            '''
            ...

        def get_starting_speed(self) -> int:
            '''
            Offset: 0x43
            Type: unsigned 32-bit
            Default: 0
            Range: 0 to 500000000
            Units: microsteps per 10000 s

            Speed below which instant acceleration/deceleration is allowed.
            '''
            ...

        def get_max_acceleration(self) -> int:
            '''
            Offset: 0x4F
            Type: unsigned 32-bit
            Default: 40000
            Range: 100 to 2147483647
            Units: microsteps per 100 s^2

            Default max acceleration. Can be overridden at runtime.
            '''
            ...

        def get_max_deceleration(self) -> int:
            '''
            Offset: 0x4B
            Type: unsigned 32-bit
            Default: 0 (uses max accel)
            Range: 100 to 2147483647
            Units: microsteps per 100 s^2

            Default max deceleration. 0 means it uses the max acceleration value.
            '''
            ...

        def get_step_mode(self) -> int:
            '''
            Offset: 0x41
            Type: unsigned 8-bit
            Data:
              0: Full step
              1: 1/2 step
              2: 1/4 step
              3: 1/8 step
              4: 1/16 step
              5: 1/32 step
              6: 1/2 step 100% (T249 only)
              7: 1/64 step  (36v4)
              8: 1/128 step (36v4)
              9: 1/256 step (36v4)
            Default: 0 (Full step)

            The default microstepping mode, which can be overridden by a runtime command.
            '''
            ...

        def get_current_limit(self) -> int:
            '''
            Offset: 0x40
            Type: unsigned 8-bit

            The default coil current limit for the driver. Scale/units depend on the Tic model
            (see Section 6). This can be overridden by the "Set current limit" command.
            '''
            ...

        def get_decay_mode(self) -> int:
            '''
            Offset: 0x42
            Type: unsigned 8-bit
            Non-HP Tics only:
              Tic T500: 0 = Automatic
              Tic T825: 0 = Mixed, 1 = Slow, 2 = Fast
              Tic T834: 0 = Mixed 50%, 1 = Slow, 2 = Fast, 3 = Mixed 25%, 4 = Mixed 75%
              Tic T249: 0 = ADMD
            Default: 0

            Not used by Tic 36v4 (it has a separate HP decay mode).
            '''
            ...

        def get_auto_homing(self) -> bool:
            '''
            Offset: bit 1 of 0x02
            Type: boolean
            Default: false

            Enables automatic homing feature (Section 5.6).
            '''
            ...

        def get_auto_homing_forward(self) -> bool:
            '''
            Offset: bit 2 of 0x02
            Type: boolean
            Default: false

            Determines the direction (forward or reverse) for automatic homing.
            '''
            ...

        def get_homing_speed_towards(self) -> int:
            '''
            Offset: 0x61
            Type: unsigned 32-bit
            Default: 1000000
            Range: 0 to 500000000
            Units: microsteps per 10000 s

            Speed used by the homing procedure when traveling toward the limit switch.
            '''
            ...

        def get_homing_speed_away(self) -> int:
            '''
            Offset: 0x65
            Type: unsigned 32-bit
            Default: 1000000
            Range: 0 to 500000000
            Units: microsteps per 10000 s

            Speed used by the homing procedure when traveling away from the limit switch.
            '''
            ...

        def get_agc_mode(self) -> int:
            '''
            Offset: 0x6C
            Type: unsigned 8-bit
            (T249 only)
            Data:
              0: Off
              1: On
              2: Active off
            Default: 0 (Off)

            The default Active Gain Control mode on the Tic T249.
            '''
            ...

        def get_agc_bottom_current_limit(self) -> int:
            '''
            Offset: 0x6D
            Type: unsigned 8-bit
            (T249 only)
            Data:
              0 = 45%
              1 = 50%
              2 = 55%
              3 = 60%
              4 = 65%
              5 = 70%
              6 = 75%
              7 = 80%
            Default: 7 (80%)

            Controls how far AGC can reduce coil current on the Tic T249.
            '''
            ...

        def get_agc_current_boost_steps(self) -> int:
            '''
            Offset: 0x6E
            Type: unsigned 8-bit
            (T249 only)
            Data:
              0 = 5 steps
              1 = 7 steps
              2 = 9 steps
              3 = 11 steps
            Default: 0 (5 steps)

            AGC boost step setting on the Tic T249.
            '''
            ...

        def get_agc_frequency_limit(self) -> int:
            '''
            Offset: 0x6F
            Type: unsigned 8-bit
            (T249 only)
            Data:
              0 = Off
              1 = 225 Hz
              2 = 450 Hz
              3 = 675 Hz
            Default: 0 (Off)

            AGC frequency limit on the Tic T249.
            '''
            ...

        def get_hp_enable_unrestricted_current_limits(self) -> bool:
            '''
            Offset: bit 0 of 0x6C
            Type: boolean
            (36v4 only)
            Default: false

            Enables allowing current limits above ~4000 mA on the Tic 36v4. Use with caution.
            '''
            ...

        def get_hp_fixed_off_time(self) -> int:
            '''
            Offset: 0xF6
            Type: unsigned 8-bit
            (36v4 only)
            Default: 25.5 us
            Range: 0.5 us to 128.0 us

            "Fixed off time" for the DRV8711-based driver on Tic 36v4.
            '''
            ...

        def get_hp_current_trip_blanking_time(self) -> int:
            '''
            Offset: 0xF8
            Type: unsigned 8-bit
            (36v4 only)
            Default: 1.00 us
            Range: 1.00 us to 5.10 us

            The minimum on-time in each PWM cycle for the Tic 36v4 driver.
            '''
            ...

        def get_hp_enable_adaptive_blanking_time(self) -> bool:
            '''
            Offset: bit 0 of 0xF9
            Type: boolean
            (36v4 only)
            Default: true

            Reduces blanking time for low-current steps if enabled (DRV8711 setting).
            '''
            ...

        def get_hp_mixed_decay_transition_time(self) -> int:
            '''
            Offset: 0xFA
            Type: unsigned 8-bit
            (36v4 only)
            Default: 8.0 us
            Range: 0.0 us to 127.5 us

            The time after which the driver switches from fast to slow decay in mixed mode.
            '''
            ...

        def get_hp_decay_mode(self) -> int:
            '''
            Offset: 0xFB
            Type: unsigned 8-bit
            (36v4 only)

            The decay mode for high-power Tics (36v4). For example: slow, slow_mixed, fast, mixed, etc.
            '''
            ...

# Main classes -----------------------------------------------

class TicBase(object):

    def __init__(self):
        self._define_commands()
        self._define_variables()
        self.settings = Settings(self)

    def _send_command(self, command_code, format, value=None):
        """
        Sends command to the Tic. Must be defined by child classes.
        """
        raise NotImplementedError

    def _block_read(self, command_code, offset, length, format_response=None):
        """
        Returns the value of the specified variable or setting. Must be defined by child classes.
        """
        raise NotImplementedError

    def _define_commands(self):
        """
        Defines methods for all Tic commands.
        """
        for command in COMMANDS:
            name, code, format = command
            setattr(self, name, partial(self._send_command, code, format))

    def _define_variables(self):
        """
        Defines methods for all Tic variables.
        """
        self.variables = {}
        for variable in VARIABLES:
            name, offset, length, format_response = variable
            setattr(
                self,
                'get_' + name,
                partial(self._block_read, GET_VARIABLE_CMD, offset, length, format_response))

    def get_variables(self):
        """
        Returns all Tic variables and their values.
        """
        result = {}
        for variable in VARIABLES:
            name, _, _, _ = variable
            result[name] = getattr(self, 'get_' + name)()
        return result
    
    if TYPE_CHECKING:
        #
        # Below are typed stub methods for each dynamically-added command.
        # They are never actually called at runtime, but help with type checking and documentation.
        #
        # --- Command stubs --- 
        #
        def set_target_position(self, value: int) -> None:
            """
            Command: 0xE0
            Format: 32-bit write
            Data: target position, signed 32-bit
            Range: -2,147,483,648 to +2,147,483,647 (-0x8000_0000 to +0x7FFF_FFFF)
            Units: microsteps

            This command sets the target position of the Tic in microsteps.

            If the control mode is set to Serial / I²C / USB, the Tic will start moving the motor 
            to reach the target position. If the control mode is something other than 
            Serial / I²C / USB, this command is silently ignored.
            """
            ...

        def set_target_velocity(self, value: int) -> None:
            """
            Command: 0xE3
            Format: 32-bit write
            Data: target velocity, signed 32-bit
            Range: -500,000,000 to +500,000,000
            Units: microsteps per 10,000 s

            This command sets the target velocity of the Tic in microsteps per 10,000 seconds.

            If the control mode is Serial / I²C / USB, the Tic will start accelerating or 
            decelerating the motor to reach the target velocity. Otherwise, it is ignored.
            """
            ...

        def halt_and_set_position(self, value: int) -> None:
            """
            Command: 0xEC
            Format: 32-bit write
            Data: current position, signed 32-bit
            Range: -2,147,483,648 to +2,147,483,647 (-0x8000_0000 to +0x7FFF_FFFF)
            Units: microsteps

            This command stops the motor abruptly (without respecting deceleration limits) 
            and sets the “Current position” variable to the specified value. 
            It also clears the “position uncertain” flag, sets the input state to “halt,” 
            and clears “input after scaling.”
            """
            ...

        def halt_and_hold(self) -> None:
            """
            Command: 0x89
            Format: Quick command
            Data: none

            This command abruptly stops the motor (without respecting deceleration limits),
            sets the “position uncertain” flag, sets the input state to “halt,” 
            and clears “input after scaling.”
            """
            ...

        def go_home(self, value: int) -> None:
            """
            Command: 0x97
            Format: 7-bit write
            Data: 
                0 = Go home in the reverse direction
                1 = Go home in the forward direction

            This command starts the Tic's homing procedure in the specified direction.
            """
            ...

        def reset_command_timeout(self) -> None:
            """
            Command: 0x8C
            Format: Quick command
            Data: none

            This command resets the command timeout so that the “command timeout” error
            does not occur for some time. If command timeout is enabled, be sure to call
            this command regularly or disable the timeout in settings.
            """
            ...

        def deenergize(self) -> None:
            """
            Command: 0x86
            Format: Quick command
            Data: none

            This command disables the stepper driver, causing the motor coils to be de-energized.
            The “position uncertain” flag is set, and the Tic sets the “intentionally de-energized” 
            error bit, turning on the red LED and driving ERR high.
            """
            ...

        def energize(self) -> None:
            """
            Command: 0x85
            Format: Quick command
            Data: none

            This command is a request to enable the stepper driver and energize the motor coils.
            It clears the “intentionally de-energized” error bit and, if there are no other errors, 
            allows the system to start up again.
            """
            ...

        def exit_safe_start(self) -> None:
            """
            Command: 0x83
            Format: Quick command
            Data: none

            In Serial/I²C/USB control mode, this command clears the “safe start violation” error 
            for 200 ms, allowing the motor to start if there are no other errors.
            """
            ...

        def enter_safe_start(self) -> None:
            """
            Command: 0x8F
            Format: Quick command
            Data: none

            If safe start is enabled and the control mode is one that supports it, this command 
            stops the motor using the configured soft error response and sets the “safe start 
            violation” error bit.
            """
            ...

        def reset(self) -> None:
            """
            Command: 0xB0
            Format: Quick command
            Data: none

            This command causes the Tic to:
             - Reload settings from non-volatile memory,
             - Abruptly halt the motor,
             - Reset the motor driver,
             - Clear certain errors,
             - And enter safe start if configured.

            It is not a full microcontroller reset (the “up time” variable is not reset).
            """
            ...

        def clear_driver_error(self) -> None:
            """
            Command: 0x8A
            Format: Quick command
            Data: none

            This command attempts to clear a motor driver error (e.g., over-current or 
            over-temperature) if the “Automatically clear driver errors” setting is disabled. 
            If automatic clearing is enabled, this command has no effect because the driver 
            error will be cleared automatically once the fault condition goes away.
            """
            ...

        def set_max_speed(self, value: int) -> None:
            """
            Command: 0xE6
            Format: 32-bit write
            Data: max speed, unsigned 32-bit
            Range: 0 to 500,000,000
            Units: microsteps per 10,000 s

            Temporarily sets the Tic's maximum allowed speed (until reset or reinitialize).
            """
            ...

        def set_starting_speed(self, value: int) -> None:
            """
            Command: 0xE5
            Format: 32-bit write
            Data: starting speed, unsigned 32-bit
            Range: 0 to 500,000,000
            Units: microsteps per 10,000 s

            Temporarily sets the Tic's starting speed (the maximum speed at which it can 
            instantly accelerate from a stop) until reset or reinitialize.
            """
            ...

        def set_max_acceleration(self, value: int) -> None:
            """
            Command: 0xEA
            Format: 32-bit write
            Data: max acceleration, unsigned 32-bit
            Range: 100 to 2,147,483,647 (0x64 to 0x7FFF_FFFF)
            Units: microsteps per 100 s²

            Temporarily sets the Tic's maximum allowed acceleration until reset or reinitialize.
            If the provided value is between 0 and 99, it is treated as 100.
            """
            ...

        def set_max_deceleration(self, value: int) -> None:
            """
            Command: 0xE9
            Format: 32-bit write
            Data: max deceleration, unsigned 32-bit
            Range: 100 to 2,147,483,647 (0x64 to 0x7FFF_FFFF)
            Units: microsteps per 100 s²

            Temporarily sets the Tic's maximum allowed deceleration until reset or reinitialize.
            If the provided value is 0, it is set to the current max acceleration.
            If the provided value is between 1 and 99, it is treated as 100.
            """
            ...

        def set_step_mode(self, value: int) -> None:
            """
            Command: 0x94
            Format: 7-bit write
            Data: step mode, unsigned 7-bit
              0: Full step
              1: 1/2 step
              2: 1/4 step
              3: 1/8 step
              4: 1/16 step (Tic T834, T825, 36v4)
              5: 1/32 step (Tic T834, T825, 36v4)
              6: 1/2 step 100% (Tic T249)
              7: 1/64 step  (Tic 36v4)
              8: 1/128 step (Tic 36v4)
              9: 1/256 step (Tic 36v4)

            Temporarily sets the step (microstepping) mode of the driver until reset or 
            reinitialize.
            """
            ...

        def set_current_limit(self, value: int) -> None:
            """
            Command: 0x91
            Format: 7-bit write (per official docs)
            Data: current limit, unsigned 7-bit
            Range: depends on Tic model; see user's guide
            Units: nominally milliamps (though the raw command is 7 bits)

            Temporarily sets the coil current limit for the stepper driver until reset or 
            reinitialize.
            """
            ...

        def set_decay_mode(self, value: int) -> None:
            """
            Command: 0x92
            Format: 7-bit write
            Data: decay mode, unsigned 7-bit

            Example mappings:
              Tic T500: 
                0 = Automatic
              Tic T834:
                0 = Mixed 50%, 1 = Slow, 2 = Fast, 3 = Mixed 25%, 4 = Mixed 75%
              Tic T825:
                0 = Mixed, 1 = Slow, 2 = Fast
              Tic T249:
                0 = Mixed

            Temporarily sets the decay mode of the driver until reset or reinitialize. 
            (For models without adjustable decay mode, this is accepted but has no effect.)
            """
            ...

        def set_agc_option(self, value: int) -> None:
            """
            Command: 0x98
            Format: 7-bit write
            Data: upper 3 bits = AGC option, lower 4 bits = new value
              0: AGC mode
              1: AGC bottom current limit
              2: AGC current boost steps
              3: AGC frequency limit

            This command is only valid for the Tic T249. It temporarily changes one of the 
            Active Gain Control (AGC) configuration options until reset or reinitialize.
            """
            ...

        # --- Variable stubs ---

        def get_operation_state(self) -> int:
            """
            Offset: 0x00
            Type: unsigned 8-bit

            Describes the Tic's high-level operation state (see Section 5.4). 
            Possible values include:
              0 = Reset
              2 = De-energized
              4 = Soft error
              6 = Waiting for ERR line
              8 = Starting up
              10 = Normal
            """
            ...

        def get_misc_flags(self) -> int:
            """
            Offset: 0x01
            Type: unsigned 8-bit

            A bit mask providing additional status information:
              Bit 0: Energized
              Bit 1: Position uncertain
              Bit 2: Forward limit active
              Bit 3: Reverse limit active
              Bit 4: Homing active
            """
            ...

        def get_error_status(self) -> int:
            """
            Offset: 0x02
            Type: unsigned 16-bit

            A bit mask indicating which errors are currently stopping the motor (0 = no errors).
            For example:
              Bit 0: Intentionally de-energized
              Bit 1: Motor driver error
              Bit 2: Low VIN
              Bit 3: Kill switch active
              Bit 4: Required input invalid
              Bit 5: Serial error
              Bit 6: Command timeout
              Bit 7: Safe start violation
              Bit 8: ERR line high
            """
            ...

        def get_error_occured(self) -> int:
            """
            Offset: 0x04
            Type: unsigned 32-bit

            A bit mask of all errors that have occurred since this variable was last cleared.
            The bits correspond to the same errors as “error_status” (bits 0-15),
            plus additional bits for serial framing, RX overrun, format, CRC, etc.
            """
            ...

        def get_planning_mode(self) -> int:
            """
            Offset: 0x09
            Type: unsigned 8-bit

            Indicates which step-planning algorithm is currently in use:
              0 = Off (no target)
              1 = Target position
              2 = Target velocity
            """
            ...

        def get_target_position(self) -> int:
            """
            Offset: 0x0A
            Type: signed 32-bit
            Range: -2,147,483,648 to +2,147,483,647
            Units: microsteps

            The motor's target position. Meaningful only if planning mode = 1 (target position).
            """
            ...

        def get_target_velocity(self) -> int:
            """
            Offset: 0x0E
            Type: signed 32-bit
            Range: -500,000,000 to +500,000,000
            Units: microsteps per 10,000 s

            The motor's target velocity. Meaningful only if planning mode = 2 (target velocity).
            """
            ...

        def get_starting_speed(self) -> int:
            """
            Offset: 0x12
            Type: unsigned 32-bit
            Range: 0 to 500,000,000
            Units: microsteps per 10,000 s

            The maximum speed at which instant acceleration/deceleration is allowed.
            """
            ...

        def get_max_speed(self) -> int:
            """
            Offset: 0x16
            Type: unsigned 32-bit
            Range: 0 to 500,000,000
            Units: microsteps per 10,000 s

            The Tic's maximum allowed motor speed.
            """
            ...

        def get_max_deceleration(self) -> int:
            """
            Offset: 0x1A
            Type: unsigned 32-bit
            Range: 100 to 2,147,483,647
            Units: microsteps per 100 s²

            The Tic's maximum allowed motor deceleration.
            """
            ...

        def get_max_acceleration(self) -> int:
            """
            Offset: 0x1E
            Type: unsigned 32-bit
            Range: 100 to 2,147,483,647
            Units: microsteps per 100 s²

            The Tic's maximum allowed motor acceleration.
            """
            ...

        def get_current_position(self) -> int:
            """
            Offset: 0x22
            Type: signed 32-bit
            Range: -2,147,483,648 to +2,147,483,647
            Units: microsteps

            The current position (accumulated steps commanded by the Tic).
            """
            ...

        def get_current_velocity(self) -> int:
            """
            Offset: 0x26
            Type: signed 32-bit
            Range: -500,000,000 to +500,000,000
            Units: microsteps per 10,000 s

            The current velocity (step rate) being sent to the motor driver.
            """
            ...

        def get_acting_target_position(self) -> int:
            """
            Offset: 0x2A
            Type: signed 32-bit
            Units: microsteps

            An internal variable used in the target position step-planning algorithm.
            """
            ...

        def get_time_since_last_step(self) -> int:
            """
            Offset: 0x2E
            Type: unsigned 32-bit
            Units: 1/3 microseconds

            An internal variable used by the step-planning algorithms to time steps.
            """
            ...

        def get_device_reset(self) -> int:
            """
            Offset: 0x32
            Type: unsigned 8-bit

            The cause of the last full microcontroller reset:
              0 = Power up
              1 = Brown-out reset
              2 = External reset
              4 = Watchdog timer reset (unexpected)
              8 = Software reset (firmware upgrade)
              16 = Stack overflow
              32 = Stack underflow
            """
            ...

        def get_vin_voltage(self) -> int:
            """
            Offset: 0x33
            Type: unsigned 16-bit
            Units: millivolts

            The measured voltage on the VIN pin.
            """
            ...

        def get_uptime(self) -> int:
            """
            Offset: 0x35
            Type: unsigned 32-bit
            Units: milliseconds

            The time since the Tic's microcontroller last experienced a full reset.
            A “reset” command does not affect this variable.
            """
            ...

        def get_encoder_position(self) -> int:
            """
            Offset: 0x39
            Type: signed 32-bit
            Units: encoder ticks

            The raw quadrature encoder count from the TX/RX pins.
            """
            ...

        def get_rc_pulse(self) -> int:
            """
            Offset: 0x3D
            Type: unsigned 16-bit
            Units: 1/12 microseconds

            The measured width of the RC pulse on the “RC” pin. 0xFFFF indicates an invalid reading.
            """
            ...

        def get_analog_reading_scl(self) -> int:
            """
            Offset: 0x3F
            Type: unsigned 16-bit
            Range: 0 to 0xFFFE (approx)
            Units: ~0 = 0 V; ~0xFFFE = 5 V

            The analog reading from the SCL pin (if enabled). 0xFFFF if not available.
            """
            ...

        def get_analog_reading_sda(self) -> int:
            """
            Offset: 0x41
            Type: unsigned 16-bit
            Range: 0 to 0xFFFE
            Units: ~0 = 0 V; ~0xFFFE = 5 V

            The analog reading from the SDA pin (if enabled). 0xFFFF if not available.
            """
            ...

        def get_analog_reading_tx(self) -> int:
            """
            Offset: 0x43
            Type: unsigned 16-bit
            Range: 0 to 0xFFFE
            Units: ~0 = 0 V; ~0xFFFE = 5 V

            The analog reading from the TX pin (if enabled). 0xFFFF if not available.
            """
            ...

        def get_analog_reading_rx(self) -> int:
            """
            Offset: 0x45
            Type: unsigned 16-bit
            Range: 0 to 0xFFFE
            Units: ~0 = 0 V; ~0xFFFE = 5 V

            The analog reading from the RX pin (if enabled). 0xFFFF if not available.
            """
            ...

        def get_digital_readings(self) -> int:
            """
            Offset: 0x47
            Type: unsigned 8-bit

            A bit mask of the digital readings from the Tic’s control pins:
              Bit 0: SCL
              Bit 1: SDA
              Bit 2: TX
              Bit 3: RX
              Bit 4: RC
            """
            ...

        def get_pin_states(self) -> int:
            """
            Offset: 0x48
            Type: unsigned 8-bit

            Each pair of bits encodes the state of the corresponding pin:
              0 = High impedance
              1 = Pulled up
              2 = Output low
              3 = Output high
            Bits [0..1]: SCL, [2..3]: SDA, [4..5]: TX, [6..7]: RX
            """
            ...

        def get_step_mode(self) -> int:
            """
            Offset: 0x49
            Type: unsigned 8-bit

            The currently used step/microstepping mode of the driver:
              0 = Full step
              1 = 1/2 step
              2 = 1/4 step
              3 = 1/8 step
              4 = 1/16 step
              5 = 1/32 step
              6 = 1/2 step 100%
              7 = 1/64 step
              8 = 1/128 step
              9 = 1/256 step
            """
            ...

        def get_current_limit(self) -> int:
            """
            Offset: 0x4A
            Type: unsigned 8-bit

            The current limit (in driver-specific units) for the stepper driver.
            """
            ...

        def get_decay_mode(self) -> int:
            """
            Offset: 0x4B
            Type: unsigned 8-bit
            (Not valid for 36v4)

            The decay mode of the driver, if applicable. For example:
              Tic T500: 0 = Automatic
              Tic T825: 0 = Mixed, 1 = Slow, 2 = Fast
              Tic T834: 0 = Mixed 50%, 1 = Slow, ...
              Tic T249: 0 = ADMD
            """
            ...

        def get_input_state(self) -> int:
            """
            Offset: 0x4C
            Type: unsigned 8-bit

            The main input state:
              0 = Not ready
              1 = Invalid
              2 = Halt
              3 = Target position
              4 = Target velocity
            """
            ...

        def get_input_after_averaging(self) -> int:
            """
            Offset: 0x4D
            Type: unsigned 16-bit

            An intermediate value used in the process of converting analog or RC inputs to
            a final target value.
            """
            ...

        def get_input_after_hysteresis(self) -> int:
            """
            Offset: 0x4F
            Type: unsigned 16-bit

            Another intermediate value used in processing inputs. 0xFFFF if not available.
            """
            ...

        def get_input_after_scaling(self) -> int:
            """
            Offset: 0x51
            Type: signed 32-bit

            The main input value after all scaling. If valid, this number is the target 
            position or velocity (depending on the control mode).
            """
            ...

        def get_last_motor_driver_error(self) -> int:
            """
            Offset: 0x55
            Type: unsigned 8-bit
            (Tic T249 only)

            The cause of the last motor driver error on the Tic T249:
              0 = None
              1 = Over-current
              2 = Over-temperature
            """
            ...

        def get_agc_mode(self) -> int:
            """
            Offset: 0x56
            Type: unsigned 8-bit
            (Tic T249 only)

            Current AGC mode. See Section 6 for details.
            """
            ...

        def get_agc_bottom_current_limit(self) -> int:
            """
            Offset: 0x57
            Type: unsigned 8-bit
            (Tic T249 only)

            The AGC bottom current limit setting.
            """
            ...

        def get_agc_current_boost_steps(self) -> int:
            """
            Offset: 0x58
            Type: unsigned 8-bit
            (Tic T249 only)

            The AGC current boost steps setting.
            """
            ...

        def get_agc_frequency_limit(self) -> int:
            """
            Offset: 0x59
            Type: unsigned 8-bit
            (Tic T249 only)

            The AGC frequency limit setting.
            """
            ...

        def get_last_hp_driver_errors(self) -> int:
            """
            Offset: 0xFF
            Type: unsigned 8-bit
            (Tic 36v4 only)

            A bit mask indicating the cause(s) of the last driver error on the Tic 36v4:
              Bit 0: Overtemperature
              Bit 1: Overcurrent A
              Bit 2: Overcurrent B
              Bit 3: Predriver fault A
              Bit 4: Predriver fault B
              Bit 5: Undervoltage
              Bit 7: Verification failure
            """
            ...

def _get_crc_7(message):
    """
    Calculates and returns the integrity verification byte for the given message. Used only by the serial controller.
    For more details, see section "Cyclic Redundancy Check (CRC) error detection" at https://www.pololu.com/docs/0J71/9
    """
    crc = 0
    for i in range(len(message)):
        crc ^= message[i]
        for j in range(8):
            if crc & 1:
                crc ^= 0x91
            crc >>= 1
    return crc.to_bytes(1, 'little')


class TicSerial(TicBase):
    """
    Serial driver for Tic stepper motor controllers.
    Reference: https://www.pololu.com/docs/0J71/9
    """

    def __init__(self, port, device_number=None, crc_for_commands=False, crc_for_responses=False):
        self.port = port
        self.device_number = device_number
        self.crc_for_commands = crc_for_commands
        self.crc_for_responses = crc_for_responses
        super().__init__()

    def _send_command(self, command_code, format, value=None):
        """
        Sends command to the Tic.
        """
        if self.device_number is None:
            # Compact protocol
            serialized = bytes([command_code])
        else:
            # Pololu protocol
            serialized = bytes([0xAA, self.device_number, command_code & 0x7F])

        # Format the command parameter
        if format == SEVEN_BITS:
            serialized += bytes([value])
        elif format == THIRTY_TWO_BITS:
            serialized += bytes([
                ((value >> 7) & 1) | ((value >> 14) & 2) | ((value >> 21) & 4) | ((value >> 28) & 8),
                value >> 0 & 0x7F,
                value >> 8 & 0x7F,
                value >> 16 & 0x7F,
                value >> 24 & 0x7F
            ])
        elif format == BLOCK_READ:
            serialized += value

        # Add CRC byte if required
        if self.crc_for_commands:
            serialized += _get_crc_7(serialized)

        # Write command to the bus
        self.port.write(serialized)

    def _block_read(self, command_code, offset, length, format_response=None):
        """
        Returns the value of the specified variable or setting from the Tic.
        """
        # Send command requesting the value
        if offset >= 128:
            # To access offsets between 128 and 255, we must set bit 6 of the length byte.
            # See https://www.pololu.com/docs/0J71/9 for more details
            self._send_command(command_code, BLOCK_READ, bytes([offset - 128, length + 64]))
        else:
            self._send_command(command_code, BLOCK_READ, bytes([offset, length]))
        # Read the returned value
        result = self._read_response(length)
        # Verify and format the returned value
        if result is None:
            raise RuntimeError("Read response returned 'None', read likely timed out")
        elif len(result) != length:
            raise RuntimeError("Expected to read {} bytes, got {}.".format(length, len(result)))
        if format_response is None:
            return result
        else:
            return format_response(result)

    def _read_response(self, length):
        """
        Reads and returns the variable or setting returned by the Tic.
        """
        if self.crc_for_responses:
            # Read extra byte at the end of the response
            response = self.port.read(length + 1)
            if len(response) != length + 1:
                raise RuntimeError("Response does not contain CRC byte")
            # Extract the main message and CRC from the response
            message = response[0:length]
            # Oddly, response[-1] returns an int instead of a byte, so we use this more convoluted notation:
            crc = int.to_bytes(
                response[-1], 1, 'little')
            # Verify that the CRC byte returned by the Tic is correct
            if crc == _get_crc_7(message):
                # Success: the CRC byte is correct
                return message
            else:
                raise RuntimeError("Response CRC check failed")
        else:
            return self.port.read(length)


class TicI2C(TicBase):
    """
    I2C driver for Tic stepper motor controllers.
    Reference: https://www.pololu.com/docs/0J71/10
    """

    def __init__(self, backend):
        self.backend = backend
        super().__init__()

    def _send_command(self, command_code, format, value=None):
        """
        Sends command to the Tic.
        """
        serialized = bytes([command_code])
        # Format the command parameter
        if format == SEVEN_BITS:
            serialized += bytes([value])
        elif format == THIRTY_TWO_BITS:
            serialized += bytes([
                value >> 0 & 0xFF,
                value >> 8 & 0xFF,
                value >> 16 & 0xFF,
                value >> 24 & 0xFF
            ])
        elif format == BLOCK_READ:
            serialized += value
        # Write command to the bus
        self.backend.write(serialized)

    def _block_read(self, command_code, offset, length, format_response=None):
        """
        Returns the value of the specified variable or setting from the Tic.
        """
        self._send_command(command_code, BLOCK_READ, bytes([offset, length]))
        result = self.backend.read(length)
        if len(result) != length:
            raise RuntimeError("Expected to read {} bytes, got {}.".format(length, len(result)))
        if format_response is None:
            return result
        else:
            return format_response(result)


class TicUSB(TicBase):
    """
    USB driver for Tic stepper motor controllers.
    Reference: https://www.pololu.com/docs/0J71/11
    """

    def __init__(self, product=None, serial_number=None):
        if usb_core is None:
            raise Exception("Missing dependency: pyusb")
        params = dict(idVendor=VENDOR)
        if product is not None:
            params['idProduct'] = product
        if serial_number is not None:
            params['serial_number'] = serial_number
        self.usb = usb_core.find(**params)
        if self.usb is None:
            raise Exception('USB device not found')
        self.usb.set_configuration()
        super().__init__()

    def _send_command(self, command_code, format, value=None):
        """
        Sends command to the Tic.
        """
        if format == QUICK:
            self.usb.ctrl_transfer(0x40, command_code, 0, 0, 0)
        elif format == SEVEN_BITS:
            self.usb.ctrl_transfer(0x40, command_code, value, 0, 0)
        elif format == THIRTY_TWO_BITS:
            self.usb.ctrl_transfer(0x40, command_code, value & 0xFFFF, value >> 16 & 0xFFFF, 0)

    def _block_read(self, command_code, offset, length, format_response=None):
        """
        Returns the value of the specified variable or setting from the Tic.
        """
        result = self.usb.ctrl_transfer(0xC0, command_code, 0, offset, length)
        if len(result) != length:
            raise RuntimeError("Expected to read {} bytes, got {}.".format(length, len(result)))
        if format_response is None:
            return result
        else:
            return format_response(result)
