# BSD 2-Clause License
#
# Copyright (c) 2021, Julien Phalip
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
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

from typing import Any, Optional, Dict

__all__ = [
    "TicSerial", "TicI2C", "TicUSB",
    "SMBus2Backend", "MachineI2CBackend",
    "TIC_T825", "TIC_T834", "TIC_T500", "TIC_N825", "TIC_T249", "TIC_36v4"
]

VENDOR: int
TIC_T825: int
TIC_T834: int
TIC_T500: int
TIC_N825: int
TIC_T249: int
TIC_36v4: int

QUICK: str
THIRTY_TWO_BITS: str
SEVEN_BITS: str
BLOCK_READ: str

COMMANDS: list[tuple[str, int, str]]
VARIABLES: list[tuple[str, int, int, Any]]
SETTINGS: list[tuple[str, int, int, Any]]

GET_VARIABLE_CMD: int
GET_SETTING_CMD: int


def partial(function: Any, *args: Any) -> Any:
    """
    **Description**: MicroPython fallback for functools.partial.
    """
    ...


def boolean(bit_index: int, value: bytes) -> bool:
    """
    **Description**: Returns True if the bit located at `bit_index` in `value` is set.

    The least-significant bit is index 0.
    """
    ...


def bit_range(start: int, end: int, value: bytes) -> int:
    """
    **Description**: Returns the bits between `start` and `end` in `value`.
    """
    ...


def signed_int(value: bytes) -> int:
    """
    **Description**: Interprets `value` (in little-endian order) as a signed integer.
    """
    ...


def unsigned_int(value: bytes) -> int:
    """
    **Description**: Interprets `value` (in little-endian order) as an unsigned integer.
    """
    ...


def _get_crc_7(message: bytes) -> bytes:
    """
    **Description**: Calculates the 7-bit CRC for `message` per Pololu's documentation.
    """
    ...


class MachineI2CBackend:
    """
    **Description**: I2C backend that wraps `machine.I2C`.
    """

    def __init__(self, i2c: Any, address: int) -> None: ...
    def read(self, length: int) -> bytes: ...
    def write(self, serialized: bytes) -> None: ...


class SMBus2Backend:
    """
    **Description**: I2C backend that uses the smbus2 library.
    """

    def __init__(self, bus: Any, address: int) -> None: ...
    def read(self, length: int) -> bytes: ...
    def write(self, serialized: bytes) -> None: ...


#
# Settings class – for reading non-volatile settings.
#
class Settings:
    """
    **Description**: Class used to manage the Tic's settings.
    Dynamically adds `get_<setting>()` methods using partial().
    """

    def __init__(self, tic: Any) -> None:
        """
        **Description**: For each setting in SETTINGS, sets an attribute
        `get_<name>` that calls `tic._block_read(...)`.
        """
        ...

    def get_serial_device_number(self) -> int:
        """
        **Description**: Retrieves the serial device number from two separate bytes.
        """
        ...

    def get_serial_alt_device_number(self) -> int:
        """
        **Description**: Retrieves the alternative serial device number from two separate bytes.
        """
        ...

    def get_all(self) -> dict[str, Any]:
        """
        **Description**: Returns a dictionary of all settings (name -> value).
        """
        ...

    def get_control_mode(self) -> int:
        """
        **Description**: Determines the Tic's control mode.

        **Offset**: 0x01

        **Type**: unsigned 8-bit

        **Data**:
            0: Serial / I2C / USB  
            1: STEP/DIR  
            2: RC position  
            3: RC speed  
            4: Analog position  
            5: Analog speed  
            6: Encoder position  
            7: Encoder speed

        **Default**: 0 (Serial / I2C / USB)
        """
        ...

    def get_disable_safe_start(self) -> bool:
        """
        **Description**: Disables the safe start feature if set.

        **Offset**: Bit 0 of byte 0x03

        **Type**: boolean

        **Default**: false
        """
        ...

    def get_ignore_err_line_high(self) -> bool:
        """
        **Description**: Disables the "ERR line high" error if set.

        **Offset**: Bit 0 of byte 0x04

        **Type**: boolean

        **Default**: false
        """
        ...

    def get_auto_clear_driver_error(self) -> bool:
        """
        **Description**: When enabled, the Tic periodically clears latched driver errors.

        **Offset**: Bit 0 of byte 0x08

        **Type**: boolean

        **Default**: true
        """
        ...

    def get_never_sleep(self) -> bool:
        """
        **Description**: Prevents the Tic from sleeping if USB power is present but VIN is not.

        **Offset**: Bit 0 of byte 0x02

        **Type**: boolean

        **Default**: false
        """
        ...

    def get_vin_calibration(self) -> int:
        """
        **Description**: Adjusts scaling of VIN readings (positive increases, negative decreases).

        **Offset**: 0x14

        **Type**: signed 16-bit

        **Default**: 0

        **Range**: -500 to +500
        """
        ...

    def get_soft_error_response(self) -> int:
        """
        **Description**: Sets the soft error response behavior.

        **Offset**: 0x53

        **Type**: unsigned 8-bit

        **Data**:
            0: De-energize  
            1: Halt and hold  
            2: Decelerate to hold  
            3: Go to position

        **Default**: 2 (Decelerate to hold)
        """
        ...

    def get_soft_error_position(self) -> int:
        """
        **Description**: Position to move to if soft error response is "Go to position".

        **Offset**: 0x54

        **Type**: signed 32-bit

        **Default**: 0

        **Range**: -2,147,483,648 to 2,147,483,647
        """
        ...

    def get_current_limit_during_error(self) -> int:
        """
        **Description**: Uses a different current limit during errors, unless set to 0xFF.

        **Offset**: 0x31

        **Type**: unsigned 8-bit (or 0xFF to disable)

        **Default**: 0

        **Range**: 0 to the normal current limit (or disabled)
        """
        ...

    def get_serial_baud_rate(self) -> int:
        """
        **Description**: The serial baud rate (in bits per second), stored as a 16-bit generator value.

        **Offset**: 0x06

        **Type**: unsigned 16-bit

        **Default**: 9600

        **Range**: 200 to 115385
        """
        ...

    def get_serial_enable_alt_device_number(self) -> bool:
        """
        **Description**: If set, the Tic listens to an alternate device number.

        **Offset**: Bit 7 of byte 0x6A

        **Type**: boolean

        **Default**: false
        """
        ...

    def get_serial_14bit_device_number(self) -> bool:
        """
        **Description**: Allows device numbers up to 16383 when enabled.

        **Offset**: Bit 3 of byte 0x0B

        **Type**: boolean

        **Default**: false
        """
        ...

    def get_serial_response_delay(self) -> int:
        """
        **Description**: Minimum delay (in microseconds) before a serial response or I2C processing.

        **Offset**: 0x5E

        **Type**: unsigned 8-bit

        **Default**: 0

        **Range**: 0 to 255
        """
        ...

    def get_serial_command_timeout(self) -> int:
        """
        **Description**: Timeout (in ms) before a "command timeout" error is flagged.

        **Offset**: 0x09

        **Type**: unsigned 16-bit

        **Default**: 1000

        **Range**: 0 to 60000
        """
        ...

    def get_serial_crc_for_commands(self) -> bool:
        """
        **Description**: Requires a 7-bit CRC on incoming serial commands if true.

        **Offset**: Bit 0 of byte 0x0B

        **Type**: boolean

        **Default**: false
        """
        ...

    def get_serial_crc_for_responses(self) -> bool:
        """
        **Description**: Appends a 7-bit CRC to serial responses if true.

        **Offset**: Bit 1 of byte 0x0B

        **Type**: boolean

        **Default**: false
        """
        ...

    def get_serial_7bit_responses(self) -> bool:
        """
        **Description**: Encodes serial responses with 7-bit bytes only if true.

        **Offset**: Bit 2 of byte 0x0B

        **Type**: boolean

        **Default**: false
        """
        ...

    def get_encoder_prescaler(self) -> int:
        """
        **Description**: For encoder modes, number of encoder counts per stepper unit.

        **Offset**: 0x58

        **Type**: unsigned 32-bit

        **Default**: 1

        **Range**: 1 to 2,147,483,647
        """
        ...

    def get_encoder_postscaler(self) -> int:
        """
        **Description**: For encoder modes, size of each stepper unit.

        **Offset**: 0x37

        **Type**: unsigned 32-bit

        **Default**: 1

        **Range**: 1 to 2,147,483,647
        """
        ...

    def get_encoder_unlimited(self) -> bool:
        """
        **Description**: Enables unbounded position control if set.

        **Offset**: Bit 0 of 0x5C

        **Type**: boolean

        **Default**: false
        """
        ...

    def get_input_averaging_enabled(self) -> bool:
        """
        **Description**: Enables averaging for RC/analog inputs.

        **Offset**: Bit 0 of 0x2E

        **Type**: boolean

        **Default**: true
        """
        ...

    def get_input_hysteresis(self) -> int:
        """
        **Description**: Amount of hysteresis to apply to RC/analog inputs.

        **Offset**: 0x2F

        **Type**: unsigned 16-bit

        **Default**: 0

        **Range**: 0 to 65535
        """
        ...

    def get_input_invert(self) -> bool:
        """
        **Description**: Inverts input direction for RC/analog modes if true.

        **Offset**: 0x21

        **Type**: boolean

        **Default**: false
        """
        ...

    def get_input_max(self) -> int:
        """
        **Description**: Maximum value for RC/analog input scaling.

        **Offset**: 0x28

        **Type**: unsigned 16-bit

        **Default**: 4095

        **Range**: 0 to 4095
        """
        ...

    def get_output_max(self) -> int:
        """
        **Description**: Maximum target value for RC/analog scaling.

        **Offset**: 0x32

        **Type**: signed 32-bit

        **Default**: 200

        **Range**: 0 to 2,147,483,647
        """
        ...

    def get_input_neutral_max(self) -> int:
        """
        **Description**: Neutral zone upper bound for RC/analog inputs.

        **Offset**: 0x26

        **Type**: unsigned 16-bit

        **Default**: 2080

        **Range**: 0 to 4095
        """
        ...

    def get_input_neutral_min(self) -> int:
        """
        **Description**: Neutral zone lower bound for RC/analog inputs.

        **Offset**: 0x24

        **Type**: unsigned 16-bit

        **Default**: 2015

        **Range**: 0 to 4095
        """
        ...

    def get_input_min(self) -> int:
        """
        **Description**: Minimum value for RC/analog input scaling.

        **Offset**: 0x22

        **Type**: unsigned 16-bit

        **Default**: 0

        **Range**: 0 to 4095
        """
        ...

    def get_output_min(self) -> int:
        """
        **Description**: Minimum target value for RC/analog scaling.

        **Offset**: 0x2A

        **Type**: signed 32-bit

        **Default**: -200

        **Range**: -2,147,483,647 to 0
        """
        ...

    def get_input_scaling_degree(self) -> int:
        """
        **Description**: Determines the polynomial degree for scaling RC/analog inputs.

        **Offset**: 0x20

        **Type**: unsigned 8-bit

        **Data**:
            0: linear  
            1: quadratic  
            2: cubic

        **Default**: 0 (linear)
        """
        ...

    def get_scl_config(self) -> int:
        """
        **Description**: Pin configuration for the SCL line.

        **Offset**: 0x3B

        **Type**: 8-bit

        **Default**: 0
        """
        ...

    def get_scl_pin_function(self) -> int:
        """
        **Description**: Extracted pin function from SCL configuration.

        **Offset**: 0x3B

        **Type**: bits [0..3]

        **Default**: 0

        **Data**:
            0: Default  
            1: User I/O  
            2: User input  
            3: Potentiometer power  
            4: SCL  
            7: Kill switch  
            8: Limit switch forward  
            9: Limit switch reverse
        """
        ...

    def get_scl_enable_analog(self) -> bool:
        """
        **Description**: Whether analog readings are enabled on SCL.

        **Offset**: Bit 6 of 0x3B

        **Type**: boolean

        **Default**: false
        """
        ...

    def get_scl_enable_pull_up(self) -> bool:
        """
        **Description**: Whether internal pull-up is enabled on SCL.

        **Offset**: Bit 7 of 0x3B

        **Type**: boolean

        **Default**: false
        """
        ...

    def get_scl_active_high(self) -> bool:
        """
        **Description**: Determines if SCL switch is active high.

        **Offset**: Bit 0 of 0x36

        **Type**: boolean

        **Default**: false
        """
        ...

    def get_scl_kill_switch(self) -> bool:
        """
        **Description**: Indicates if SCL is mapped as a kill switch.

        **Offset**: Bit 0 of 0x5D

        **Type**: boolean

        **Default**: false
        """
        ...

    def get_scl_limit_switch_forward(self) -> bool:
        """
        **Description**: Indicates if SCL is used as a forward limit switch.

        **Offset**: Bit 0 of 0x5F

        **Type**: boolean

        **Default**: false
        """
        ...

    def get_scl_limit_switch_reverse(self) -> bool:
        """
        **Description**: Indicates if SCL is used as a reverse limit switch.

        **Offset**: Bit 0 of 0x60

        **Type**: boolean

        **Default**: false
        """
        ...

    def get_sda_config(self) -> int:
        """
        **Description**: Pin configuration for the SDA line.

        **Offset**: 0x3C

        **Type**: 8-bit

        **Default**: 0
        """
        ...

    def get_sda_pin_function(self) -> int:
        """
        **Description**: Extracted pin function for SDA.

        **Offset**: 0x3C

        **Type**: bits [0..3]

        **Default**: 0
        """
        ...

    def get_sda_enable_analog(self) -> bool:
        """
        **Description**: Whether analog readings are enabled on SDA.

        **Offset**: Bit 6 of 0x3C

        **Type**: boolean

        **Default**: false
        """
        ...

    def get_sda_enable_pull_up(self) -> bool:
        """
        **Description**: Whether internal pull-up is enabled on SDA.

        **Offset**: Bit 7 of 0x3C

        **Type**: boolean

        **Default**: false
        """
        ...

    def get_sda_active_high(self) -> bool:
        """
        **Description**: Determines if SDA switch is active high.

        **Offset**: Bit 1 of 0x36

        **Type**: boolean

        **Default**: false
        """
        ...

    def get_sda_kill_switch(self) -> bool:
        """
        **Description**: Indicates if SDA is mapped as a kill switch.

        **Offset**: Bit 1 of 0x5D

        **Type**: boolean

        **Default**: false
        """
        ...

    def get_sda_limit_switch_forward(self) -> bool:
        """
        **Description**: Indicates if SDA is used as a forward limit switch.

        **Offset**: Bit 1 of 0x5F

        **Type**: boolean

        **Default**: false
        """
        ...

    def get_sda_limit_switch_reverse(self) -> bool:
        """
        **Description**: Indicates if SDA is used as a reverse limit switch.

        **Offset**: Bit 1 of 0x60

        **Type**: boolean

        **Default**: false
        """
        ...

    def get_tx_config(self) -> int:
        """
        **Description**: Pin configuration for the TX line.

        **Offset**: 0x3D

        **Type**: 8-bit

        **Default**: 0
        """
        ...

    def get_tx_pin_function(self) -> int:
        """
        **Description**: Extracted pin function for TX.

        **Offset**: 0x3D

        **Type**: bits [0..3]

        **Default**: 0
        """
        ...

    def get_tx_enable_analog(self) -> bool:
        """
        **Description**: Whether analog readings are enabled on TX.

        **Offset**: Bit 6 of 0x3D

        **Type**: boolean

        **Default**: false
        """
        ...

    def get_tx_active_high(self) -> bool:
        """
        **Description**: Determines if TX switch is active high.

        **Offset**: Bit 2 of 0x36

        **Type**: boolean

        **Default**: false
        """
        ...

    def get_tx_kill_switch(self) -> bool:
        """
        **Description**: Indicates if TX is mapped as a kill switch.

        **Offset**: Bit 2 of 0x5D

        **Type**: boolean

        **Default**: false
        """
        ...

    def get_tx_limit_switch_forward(self) -> bool:
        """
        **Description**: Indicates if TX is used as a forward limit switch.

        **Offset**: Bit 2 of 0x5F

        **Type**: boolean

        **Default**: false
        """
        ...

    def get_tx_limit_switch_reverse(self) -> bool:
        """
        **Description**: Indicates if TX is used as a reverse limit switch.

        **Offset**: Bit 2 of 0x60

        **Type**: boolean

        **Default**: false
        """
        ...

    def get_rx_config(self) -> int:
        """
        **Description**: Pin configuration for the RX line.

        **Offset**: 0x3E

        **Type**: 8-bit

        **Default**: 0
        """
        ...

    def get_rx_pin_function(self) -> int:
        """
        **Description**: Extracted pin function for RX.

        **Offset**: 0x3E

        **Type**: bits [0..3]

        **Default**: 0
        """
        ...

    def get_rx_enable_analog(self) -> bool:
        """
        **Description**: Whether analog readings are enabled on RX.

        **Offset**: Bit 6 of 0x3E

        **Type**: boolean

        **Default**: false
        """
        ...

    def get_rx_active_high(self) -> bool:
        """
        **Description**: Determines if RX switch is active high.

        **Offset**: Bit 3 of 0x36

        **Type**: boolean

        **Default**: false
        """
        ...

    def get_rx_kill_switch(self) -> bool:
        """
        **Description**: Indicates if RX is mapped as a kill switch.

        **Offset**: Bit 3 of 0x5D

        **Type**: boolean

        **Default**: false
        """
        ...

    def get_rx_limit_switch_forward(self) -> bool:
        """
        **Description**: Indicates if RX is used as a forward limit switch.

        **Offset**: Bit 3 of 0x5F

        **Type**: boolean

        **Default**: false
        """
        ...

    def get_rx_limit_switch_reverse(self) -> bool:
        """
        **Description**: Indicates if RX is used as a reverse limit switch.

        **Offset**: Bit 3 of 0x60

        **Type**: boolean

        **Default**: false
        """
        ...

    def get_rc_config(self) -> int:
        """
        **Description**: Pin configuration for the RC line (pulse input).

        **Offset**: 0x3F

        **Type**: 8-bit

        **Default**: 0
        """
        ...

    def get_rc_active_high(self) -> bool:
        """
        **Description**: Determines if RC switch is active high.

        **Offset**: Bit 4 of 0x36

        **Type**: boolean

        **Default**: false
        """
        ...

    def get_rc_kill_switch(self) -> bool:
        """
        **Description**: Indicates if RC is mapped as a kill switch.

        **Offset**: Bit 4 of 0x5D

        **Type**: boolean

        **Default**: false
        """
        ...

    def get_rc_limit_switch_forward(self) -> bool:
        """
        **Description**: Indicates if RC is used as a forward limit switch.

        **Offset**: Bit 4 of 0x5F

        **Type**: boolean

        **Default**: false
        """
        ...

    def get_rc_limit_switch_reverse(self) -> bool:
        """
        **Description**: Indicates if RC is used as a reverse limit switch.

        **Offset**: Bit 4 of 0x60

        **Type**: boolean

        **Default**: false
        """
        ...

    def get_invert_motor_direction(self) -> bool:
        """
        **Description**: Reverses the motor direction if set.

        **Offset**: Bit 0 of 0x1B

        **Type**: boolean

        **Default**: false
        """
        ...

    def get_max_speed(self) -> int:
        """
        **Description**: The default maximum motor speed, which can be overridden.

        **Offset**: 0x47

        **Type**: unsigned 32-bit

        **Default**: 2000000

        **Range**: 0 to 500000000

        **Units**: microsteps per 10000 s
        """
        ...

    def get_starting_speed(self) -> int:
        """
        **Description**: The default starting speed; instant acceleration/deceleration is allowed below this value.

        **Offset**: 0x43

        **Type**: unsigned 32-bit

        **Default**: 0

        **Range**: 0 to 500000000

        **Units**: microsteps per 10000 s
        """
        ...

    def get_max_acceleration(self) -> int:
        """
        **Description**: The default maximum acceleration; can be overridden at runtime.

        **Offset**: 0x4F

        **Type**: unsigned 32-bit

        **Default**: 40000

        **Range**: 100 to 2147483647

        **Units**: microsteps per 100 s^2
        """
        ...

    def get_max_deceleration(self) -> int:
        """
        **Description**: The default maximum deceleration. A value of 0 means the max acceleration is used;
        values below 100 are treated as 100.

        **Offset**: 0x4B

        **Type**: unsigned 32-bit

        **Default**: 0 (uses max accel)

        **Range**: 100 to 2147483647

        **Units**: microsteps per 100 s^2
        """
        ...

    def get_step_mode(self) -> int:
        """
        **Description**: The default microstepping mode for settings. This value may be overridden at runtime.

        **Offset**: 0x41

        **Type**: unsigned 8-bit

        **Data**:
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

        **Default**: 0 (Full step)
        """
        ...

    def get_current_limit(self) -> int:
        """
        **Description**: The default coil current limit in driver-specific units.
        
        **Offset**: 0x40

        **Type**: unsigned 8-bit
        """
        ...

    def get_decay_mode(self) -> int:
        """
        **Description**: The default decay mode for non-HP Tics; not used for Tic 36v4.

        **Offset**: 0x42

        **Type**: unsigned 8-bit

        **Data**:
            Tic T500: 0 = Automatic  
            Tic T825: 0 = Mixed, 1 = Slow, 2 = Fast  
            Tic T834: 0 = Mixed 50%, 1 = Slow, 2 = Fast, 3 = Mixed 25%, 4 = Mixed 75%  
            Tic T249: 0 = Mixed

        **Default**: 0
        """
        ...

    def get_auto_homing(self) -> bool:
        """
        **Description**: Enables automatic homing when the position is uncertain.

        **Offset**: Bit 1 of byte 0x02

        **Type**: boolean

        **Default**: false
        """
        ...

    def get_auto_homing_forward(self) -> bool:
        """
        **Description**: Determines if automatic homing is performed in the forward direction.

        **Offset**: Bit 2 of byte 0x02

        **Type**: boolean

        **Default**: false
        """
        ...

    def get_homing_speed_towards(self) -> int:
        """
        **Description**: The speed used when homing toward the limit switch.

        **Offset**: 0x61

        **Type**: unsigned 32-bit

        **Default**: 1000000

        **Range**: 0 to 500000000

        **Units**: microsteps per 10000 s
        """
        ...

    def get_homing_speed_away(self) -> int:
        """
        **Description**: The speed used briefly when homing away from the limit switch.

        **Offset**: 0x65

        **Type**: unsigned 32-bit

        **Default**: 1000000

        **Range**: 0 to 500000000

        **Units**: microsteps per 10000 s
        """
        ...

    def get_agc_mode(self) -> int:
        """
        **Description**: The default AGC mode for Tic T249.

        **Offset**: 0x6C

        **Type**: unsigned 8-bit

        **Data**:
            0: Off  
            1: On  
            2: Active off

        **Default**: 0 (Off)
        """
        ...

    def get_agc_bottom_current_limit(self) -> int:
        """
        **Description**: The default AGC bottom current limit for Tic T249.

        **Offset**: 0x6D

        **Type**: unsigned 8-bit

        **Data**:
            0: 45%  
            1: 50%  
            2: 55%  
            3: 60%  
            4: 65%  
            5: 70%  
            6: 75%  
            7: 80%

        **Default**: 7 (80%)
        """
        ...

    def get_agc_current_boost_steps(self) -> int:
        """
        **Description**: The default AGC current boost steps for Tic T249.

        **Offset**: 0x6E

        **Type**: unsigned 8-bit

        **Data**:
            0: 5 steps  
            1: 7 steps  
            2: 9 steps  
            3: 11 steps

        **Default**: 0 (5 steps)
        """
        ...

    def get_agc_frequency_limit(self) -> int:
        """
        **Description**: The default AGC frequency limit for Tic T249.

        **Offset**: 0x6F

        **Type**: unsigned 8-bit

        **Data**:
            0: Off  
            1: 225 Hz  
            2: 450 Hz  
            3: 675 Hz

        **Default**: 0 (Off)
        """
        ...

    def get_hp_enable_unrestricted_current_limits(self) -> bool:
        """
        **Description**: Enables current limits above ~4000 mA on Tic 36v4 if set.

        **Offset**: Bit 0 of byte 0x6C

        **Type**: boolean

        **Default**: false
        """
        ...

    def get_hp_fixed_off_time(self) -> int:
        """
        **Description**: "Fixed off time" for the DRV8711-based driver on Tic 36v4.

        **Offset**: 0xF6

        **Type**: unsigned 8-bit

        **Default**: 25.5 us

        **Range**: 0.5 us to 128.0 us
        """
        ...

    def get_hp_current_trip_blanking_time(self) -> int:
        """
        **Description**: Minimum on-time for each PWM cycle on Tic 36v4.

        **Offset**: 0xF8

        **Type**: unsigned 8-bit

        **Default**: 1.00 us

        **Range**: 1.00 us to 5.10 us
        """
        ...

    def get_hp_enable_adaptive_blanking_time(self) -> bool:
        """
        **Description**: Enables adaptive blanking time on Tic 36v4 for low-current steps.

        **Offset**: Bit 0 of byte 0xF9

        **Type**: boolean

        **Default**: true
        """
        ...

    def get_hp_mixed_decay_transition_time(self) -> int:
        """
        **Description**: Time after which the driver on Tic 36v4 switches from fast to slow decay in mixed mode.

        **Offset**: 0xFA

        **Type**: unsigned 8-bit

        **Default**: 8.0 us

        **Range**: 0.0 us to 127.5 us
        """
        ...

    def get_hp_decay_mode(self) -> int:
        """
        **Description**: The decay mode for high-power Tic 36v4.

        **Offset**: 0xFB

        **Type**: unsigned 8-bit
        """
        ...


#
# TicBase merges commands, variable getters, and settings.
#
class TicBase:
    """
    **Description**: Base class for Pololu Tic controllers.
    Dynamically defines:
      - Commands (e.g. `set_target_position`)
      - Variable getters (e.g. `get_operation_state`)
      - Setting getters (e.g. `get_control_mode`)
    """

    settings: Settings

    def __init__(self) -> None: ...

    def _send_command(self, command_code: int, format: str, value: Optional[int] = None) -> None: ...
    def _block_read(self, command_code: int, offset: int, length: int,
                    format_response: Any = None) -> Any: ...
    def _define_commands(self) -> None: ...
    def _define_variables(self) -> None: ...

    def get_variables(self) -> Dict[str, Any]:
        """
        **Description**: Returns a dictionary mapping each variable name to its value.
        """
        ...

    #
    # ---------------------------
    # Command stubs
    # ---------------------------
    #
    def set_target_position(self, value: int) -> None:
        """
        **Description**: Sets the Tic's target position in microsteps.
        If control mode is Serial/I2C/USB, the motor moves to the specified position.
        Otherwise, the command is silently ignored.

        **Command**: 0xE0

        **Format**: 32-bit write

        **Data**: target position, signed 32-bit

        **Range**: -2,147,483,648 to +2,147,483,647

        **Units**: microsteps
        """
        ...

    def set_target_velocity(self, value: int) -> None:
        """
        **Description**: Sets the Tic's target velocity.
        If control mode is Serial/I2C/USB, the motor accelerates or decelerates to reach this velocity.

        **Command**: 0xE3

        **Format**: 32-bit write

        **Data**: target velocity, signed 32-bit

        **Range**: -500,000,000 to +500,000,000

        **Units**: microsteps per 10,000 s
        """
        ...

    def halt_and_set_position(self, value: int) -> None:
        """
        **Description**: Abruptly halts the motor (ignoring deceleration) and sets the 'Current position'.
        Also clears the 'position uncertain' flag, sets input state to 'halt', and clears 'input after scaling'.

        **Command**: 0xEC

        **Format**: 32-bit write

        **Data**: current position, signed 32-bit

        **Range**: -2,147,483,648 to +2,147,483,647

        **Units**: microsteps
        """
        ...

    def halt_and_hold(self) -> None:
        """
        **Description**: Abruptly stops the motor, sets 'position uncertain' and input state to 'halt',
        and clears the 'input after scaling' variable.

        **Command**: 0x89

        **Format**: Quick
        """
        ...

    def go_home(self, value: int) -> None:
        """
        **Description**: Initiates the homing procedure in the specified direction.

        **Command**: 0x97

        **Format**: 7-bit write

        **Data**:
            0: Home in reverse direction  
            1: Home in forward direction
        """
        ...

    def reset_command_timeout(self) -> None:
        """
        **Description**: Resets the command timeout to prevent 'command timeout' errors.

        **Command**: 0x8C

        **Format**: Quick
        """
        ...

    def deenergize(self) -> None:
        """
        **Description**: Disables the driver, de-energizing the motor coils.
        Sets the 'position uncertain' flag and the 'intentionally de-energized' error bit.
        
        **Command**: 0x86

        **Format**: Quick
        """
        ...

    def energize(self) -> None:
        """
        **Description**: Requests enabling the stepper driver and energizing the motor coils.
        Clears the 'intentionally de-energized' error bit if no other errors exist.
        
        **Command**: 0x85

        **Format**: Quick
        """
        ...

    def exit_safe_start(self) -> None:
        """
        **Description**: Clears the 'safe start violation' error for approximately 200 ms,
        allowing the motor to resume if control mode is Serial/I2C/USB.
        
        **Command**: 0x83

        **Format**: Quick
        """
        ...

    def enter_safe_start(self) -> None:
        """
        **Description**: Triggers safe start; if enabled, stops the motor using the soft error response.

        **Command**: 0x8F

        **Format**: Quick
        """
        ...

    def reset(self) -> None:
        """
        **Description**: Reloads settings from non-volatile memory, abruptly halts the motor,
        resets the driver, clears errors, and enters safe start if configured.
        (Note: This is not a full microcontroller reset; uptime is unaffected.)

        **Command**: 0xB0

        **Format**: Quick
        """
        ...

    def clear_driver_error(self) -> None:
        """
        **Description**: Clears a latched motor driver error if 'auto_clear_driver_error' is disabled.
        Otherwise, it has no effect.

        **Command**: 0x8A

        **Format**: Quick
        """
        ...

    def set_max_speed(self, value: int) -> None:
        """
        **Description**: Temporarily sets the maximum allowed motor speed.

        **Command**: 0xE6

        **Format**: 32-bit write

        **Data**: max speed, unsigned 32-bit

        **Range**: 0 to 500,000,000

        **Units**: microsteps per 10,000 s
        """
        ...

    def set_starting_speed(self, value: int) -> None:
        """
        **Description**: Temporarily sets the starting speed (the speed below which instant
        acceleration/deceleration is allowed).

        **Command**: 0xE5

        **Format**: 32-bit write

        **Data**: starting speed, unsigned 32-bit

        **Range**: 0 to 500,000,000

        **Units**: microsteps per 10,000 s
        """
        ...

    def set_max_acceleration(self, value: int) -> None:
        """
        **Description**: Temporarily sets the maximum allowed acceleration.
        If the provided value is less than 100, it is treated as 100.

        **Command**: 0xEA

        **Format**: 32-bit write

        **Data**: max acceleration, unsigned 32-bit

        **Range**: 100 to 2,147,483,647

        **Units**: microsteps per 100 s^2
        """
        ...

    def set_max_deceleration(self, value: int) -> None:
        """
        **Description**: Temporarily sets the maximum allowed deceleration.
        If 0, it is set equal to the current max acceleration; values below 100 are treated as 100.

        **Command**: 0xE9

        **Format**: 32-bit write

        **Data**: max deceleration, unsigned 32-bit

        **Range**: 100 to 2,147,483,647

        **Units**: microsteps per 100 s^2
        """
        ...

    def set_step_mode(self, value: int) -> None:
        """
        **Description**: Temporarily sets the microstepping mode.

        **Command**: 0x94

        **Format**: 7-bit write

        **Data**: step mode, unsigned 7-bit

        **Data Options**:
            0: Full step  
            1: 1/2 step  
            2: 1/4 step  
            3: 1/8 step  
            4: 1/16 step (Tic T834, Tic T825, and Tic 36v4 only)  
            5: 1/32 step (Tic T834, Tic T825, and Tic 36v4 only)  
            6: 1/2 step 100% (Tic T249 only)  
            7: 1/64 step (Tic 36v4 only)  
            8: 1/128 step (Tic 36v4 only)  
            9: 1/256 step (Tic 36v4 only)
        """
        ...

    def set_current_limit(self, value: int) -> None:
        """
        **Description**: Temporarily sets the coil current limit.
        The value is a 7-bit unsigned integer whose meaning depends on the Tic model.

        **Command**: 0x91

        **Format**: 7-bit write

        **Data**: current limit (in model-specific units, typically mA)
        """
        ...

    def set_decay_mode(self, value: int) -> None:
        """
        **Description**: Temporarily sets the driver decay mode.
        (Note: This has no effect on Tic 36v4.)

        **Command**: 0x92

        **Format**: 7-bit write

        **Data**: decay mode, unsigned 7-bit

        **Data Options**:
            Tic T500: 0 = Automatic  
            Tic T834: 0 = Mixed 50%, 1 = Slow, 2 = Fast, 3 = Mixed 25%, 4 = Mixed 75%  
            Tic T825: 0 = Mixed, 1 = Slow, 2 = Fast  
            Tic T249: 0 = Mixed
        """
        ...

    def set_agc_option(self, value: int) -> None:
        """
        **Description**: Temporarily changes an AGC option (only valid on Tic T249).
        The upper 3 bits specify which AGC option; the lower 4 bits specify the new value.

        **Command**: 0x98

        **Format**: 7-bit write

        **Data**: upper 3 bits = AGC option, lower 4 bits = new value
        """
        ...

    #
    # ---------------------------
    # Variable stubs (real-time variables)
    # ---------------------------
    #
    def get_operation_state(self) -> int:
        """
        **Description**: Returns the Tic's current operation state.

        **Offset**: 0x00

        **Type**: unsigned 8-bit

        Possible values:
            0: Reset  
            2: De-energized  
            4: Soft error  
            6: Waiting for ERR line  
            8: Starting up  
            10: Normal
        """
        ...

    def get_misc_flags(self) -> int:
        """
        **Description**: Returns a bitmask of additional status flags.

        **Offset**: 0x01

        **Type**: unsigned 8-bit

        Bits:
            Bit 0: Energized  
            Bit 1: Position uncertain  
            Bit 2: Forward limit active  
            Bit 3: Reverse limit active  
            Bit 4: Homing active
        """
        ...

    def get_error_status(self) -> int:
        """
        **Description**: Returns a bitmask of errors currently stopping the motor.

        **Offset**: 0x02

        **Type**: unsigned 16-bit

        Bits:
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
        **Description**: Returns a bitmask of errors that have occurred since the last clear.
        
        **Offset**: 0x04

        **Type**: unsigned 32-bit

        Includes additional bits for serial framing, overrun, CRC, etc.
        """
        ...

    def get_planning_mode(self) -> int:
        """
        **Description**: Returns the current step planning mode.

        **Offset**: 0x09

        **Type**: unsigned 8-bit

        Data:
            0: Off (no target)  
            1: Target position  
            2: Target velocity
        """
        ...

    def get_target_position(self) -> int:
        """
        **Description**: Returns the motor's target position (only valid if planning mode is Target position).

        **Offset**: 0x0A

        **Type**: signed 32-bit

        **Range**: -2,147,483,648 to +2,147,483,647

        **Units**: microsteps
        """
        ...

    def get_target_velocity(self) -> int:
        """
        **Description**: Returns the motor's target velocity (only valid if planning mode is Target velocity).

        **Offset**: 0x0E

        **Type**: signed 32-bit

        **Range**: -500,000,000 to +500,000,000

        **Units**: microsteps per 10,000 s
        """
        ...

    def get_starting_speed(self) -> int:
        """
        **Description**: Returns the starting speed—the maximum speed at which instant acceleration is allowed.

        **Offset**: 0x12

        **Type**: unsigned 32-bit

        **Range**: 0 to 500,000,000

        **Units**: microsteps per 10,000 s
        """
        ...

    def get_max_speed(self) -> int:
        """
        **Description**: Returns the maximum allowed motor speed.

        **Offset**: 0x16

        **Type**: unsigned 32-bit

        **Range**: 0 to 500,000,000

        **Units**: microsteps per 10,000 s
        """
        ...

    def get_max_deceleration(self) -> int:
        """
        **Description**: Returns the maximum allowed deceleration.

        **Offset**: 0x1A

        **Type**: unsigned 32-bit

        **Range**: 100 to 2,147,483,647

        **Units**: microsteps per 100 s^2
        """
        ...

    def get_max_acceleration(self) -> int:
        """
        **Description**: Returns the maximum allowed acceleration.

        **Offset**: 0x1E

        **Type**: unsigned 32-bit

        **Range**: 100 to 2,147,483,647

        **Units**: microsteps per 100 s^2
        """
        ...

    def get_current_position(self) -> int:
        """
        **Description**: Returns the current position (accumulated commanded steps).

        **Offset**: 0x22

        **Type**: signed 32-bit

        **Range**: -2,147,483,648 to +2,147,483,647

        **Units**: microsteps
        """
        ...

    def get_current_velocity(self) -> int:
        """
        **Description**: Returns the current commanded velocity.

        **Offset**: 0x26

        **Type**: signed 32-bit

        **Range**: -500,000,000 to +500,000,000

        **Units**: microsteps per 10,000 s
        """
        ...

    def get_acting_target_position(self) -> int:
        """
        **Description**: Returns an internal variable used in target-position step planning.

        **Offset**: 0x2A

        **Type**: signed 32-bit

        **Units**: microsteps
        """
        ...

    def get_time_since_last_step(self) -> int:
        """
        **Description**: Returns the time since the last step (used for planning).

        **Offset**: 0x2E

        **Type**: unsigned 32-bit

        **Units**: 1/3 microseconds
        """
        ...

    def get_device_reset(self) -> int:
        """
        **Description**: Returns the cause of the last full microcontroller reset.

        **Offset**: 0x32

        **Type**: unsigned 8-bit

        Possible values:
            0: Power up  
            1: Brown-out reset  
            2: External reset  
            4: Watchdog timer reset  
            8: Software reset  
            16: Stack overflow  
            32: Stack underflow
        """
        ...

    def get_vin_voltage(self) -> int:
        """
        **Description**: Returns the measured VIN voltage.

        **Offset**: 0x33

        **Type**: unsigned 16-bit

        **Units**: millivolts
        """
        ...

    def get_uptime(self) -> int:
        """
        **Description**: Returns the time since the last full microcontroller reset.
        (Note: This value is not affected by a 'reset' command.)
        
        **Offset**: 0x35

        **Type**: unsigned 32-bit

        **Units**: milliseconds
        """
        ...

    def get_encoder_position(self) -> int:
        """
        **Description**: Returns the raw quadrature encoder count from the TX/RX pins.

        **Offset**: 0x39

        **Type**: signed 32-bit

        **Units**: ticks
        """
        ...

    def get_rc_pulse(self) -> int:
        """
        **Description**: Returns the measured RC pulse width.
        A value of 0xFFFF indicates an invalid reading.

        **Offset**: 0x3D

        **Type**: unsigned 16-bit

        **Units**: 1/12 microseconds
        """
        ...

    def get_analog_reading_scl(self) -> int:
        """
        **Description**: Returns the analog reading from SCL if enabled.
        A value of 0xFFFF indicates unavailability.

        **Offset**: 0x3F

        **Type**: unsigned 16-bit

        **Range**: 0 to 0xFFFE

        **Units**: ~0 = 0 V, ~0xFFFE ≈ 5 V
        """
        ...

    def get_analog_reading_sda(self) -> int:
        """
        **Description**: Returns the analog reading from SDA if enabled.
        A value of 0xFFFF indicates unavailability.

        **Offset**: 0x41

        **Type**: unsigned 16-bit

        **Range**: 0 to 0xFFFE

        **Units**: ~0 = 0 V, ~0xFFFE ≈ 5 V
        """
        ...

    def get_analog_reading_tx(self) -> int:
        """
        **Description**: Returns the analog reading from TX if enabled.
        A value of 0xFFFF indicates unavailability.

        **Offset**: 0x43

        **Type**: unsigned 16-bit

        **Range**: 0 to 0xFFFE

        **Units**: ~0 = 0 V, ~0xFFFE ≈ 5 V
        """
        ...

    def get_analog_reading_rx(self) -> int:
        """
        **Description**: Returns the analog reading from RX if enabled.
        A value of 0xFFFF indicates unavailability.

        **Offset**: 0x45

        **Type**: unsigned 16-bit

        **Range**: 0 to 0xFFFE

        **Units**: ~0 = 0 V, ~0xFFFE ≈ 5 V
        """
        ...

    def get_digital_readings(self) -> int:
        """
        **Description**: Returns a bitmask of digital readings from the control pins.

        **Offset**: 0x47

        **Type**: unsigned 8-bit

        Bits:
            Bit 0: SCL  
            Bit 1: SDA  
            Bit 2: TX  
            Bit 3: RX  
            Bit 4: RC
        """
        ...

    def get_pin_states(self) -> int:
        """
        **Description**: Returns the state of the control pins.
        Each pair of bits represents the state:
            0: High impedance  
            1: Pulled up  
            2: Output low  
            3: Output high

        **Offset**: 0x48

        **Type**: unsigned 8-bit
        """
        ...

    def get_step_mode(self) -> int:
        """
        **Description**: Returns the current driver microstepping mode.

        **Offset**: 0x49

        **Type**: unsigned 8-bit

        Data Options:
            0: Full step  
            1: 1/2 step  
            2: 1/4 step  
            3: 1/8 step  
            4: 1/16 step  
            5: 1/32 step  
            6: 1/2 step 100%  
            7: 1/64 step  
            8: 1/128 step  
            9: 1/256 step
        """
        ...

    def get_current_limit(self) -> int:
        """
        **Description**: Returns the coil current limit in driver-specific units.

        **Offset**: 0x4A

        **Type**: unsigned 8-bit
        """
        ...

    def get_decay_mode(self) -> int:
        """
        **Description**: Returns the driver decay mode.
        (Note: This variable is not valid for Tic 36v4.)

        **Offset**: 0x4B

        **Type**: unsigned 8-bit
        """
        ...

    def get_input_state(self) -> int:
        """
        **Description**: Returns the current input state.

        **Offset**: 0x4C

        **Type**: unsigned 8-bit

        Possible states:
            0: Not ready  
            1: Invalid  
            2: Halt  
            3: Target position  
            4: Target velocity
        """
        ...

    def get_input_after_averaging(self) -> int:
        """
        **Description**: Returns the intermediate RC/analog reading after averaging.
        A value of 0xFFFF indicates unavailability.

        **Offset**: 0x4D

        **Type**: unsigned 16-bit
        """
        ...

    def get_input_after_hysteresis(self) -> int:
        """
        **Description**: Returns the intermediate reading after hysteresis.
        A value of 0xFFFF indicates unavailability.

        **Offset**: 0x4F

        **Type**: unsigned 16-bit
        """
        ...

    def get_input_after_scaling(self) -> int:
        """
        **Description**: Returns the final scaled input value (target position or velocity).
        
        **Offset**: 0x51

        **Type**: signed 32-bit
        """
        ...

    def get_last_motor_driver_error(self) -> int:
        """
        **Description**: Returns the cause of the last motor driver error (Tic T249 only).

        **Offset**: 0x55

        **Type**: unsigned 8-bit

        Data Options:
            0: None  
            1: Over-current  
            2: Over-temperature
        """
        ...

    def get_agc_mode(self) -> int:
        """
        **Description**: Returns the current AGC mode (Tic T249 only).

        **Offset**: 0x56

        **Type**: unsigned 8-bit

        Data Options:
            0: Off  
            1: On  
            2: Active off
        """
        ...

    def get_agc_bottom_current_limit(self) -> int:
        """
        **Description**: Returns the AGC bottom current limit (Tic T249 only).

        **Offset**: 0x57

        **Type**: unsigned 8-bit

        Data Options:
            0: 45%  
            1: 50%  
            2: 55%  
            3: 60%  
            4: 65%  
            5: 70%  
            6: 75%  
            7: 80%
        """
        ...

    def get_agc_current_boost_steps(self) -> int:
        """
        **Description**: Returns the AGC current boost steps (Tic T249 only).

        **Offset**: 0x58

        **Type**: unsigned 8-bit

        Data Options:
            0: 5 steps  
            1: 7 steps  
            2: 9 steps  
            3: 11 steps
        """
        ...

    def get_agc_frequency_limit(self) -> int:
        """
        **Description**: Returns the AGC frequency limit (Tic T249 only).

        **Offset**: 0x6F

        **Type**: unsigned 8-bit

        Data Options:
            0: Off  
            1: 225 Hz  
            2: 450 Hz  
            3: 675 Hz
        """
        ...

    def get_last_hp_driver_errors(self) -> int:
        """
        **Description**: Returns a bitmask indicating the cause(s) of the last high-power driver error (Tic 36v4 only).

        **Offset**: 0xFF

        **Type**: unsigned 8-bit

        Bits:
            Bit 0: Overtemperature  
            Bit 1: Overcurrent A  
            Bit 2: Overcurrent B  
            Bit 3: Predriver fault A  
            Bit 4: Predriver fault B  
            Bit 5: Undervoltage  
            Bit 7: Verification failure
        """
        ...


class TicSerial(TicBase):
    """
    **Description**: Serial driver for Tic stepper motor controllers.
    Reference: https://www.pololu.com/docs/0J71/9
    """

    def __init__(
        self,
        port: Any,
        device_number: Optional[int] = None,
        crc_for_commands: bool = False,
        crc_for_responses: bool = False
    ) -> None: ...
    def _send_command(self, command_code: int, format: str, value: Optional[int] = None) -> None: ...
    def _block_read(self, command_code: int, offset: int, length: int, format_response: Any = None) -> Any: ...
    def _read_response(self, length: int) -> bytes: ...


class TicI2C(TicBase):
    """
    **Description**: I2C driver for Tic stepper motor controllers.
    Reference: https://www.pololu.com/docs/0J71/10
    """

    def __init__(self, backend: Any) -> None: ...
    def _send_command(self, command_code: int, format: str, value: Optional[int] = None) -> None: ...
    def _block_read(self, command_code: int, offset: int, length: int, format_response: Any = None) -> Any: ...


class TicUSB(TicBase):
    """
    **Description**: USB driver for Tic stepper motor controllers.
    Reference: https://www.pololu.com/docs/0J71/11
    """

    def __init__(
        self,
        product: Optional[int] = None,
        serial_number: Optional[str] = None
    ) -> None: ...
    def _send_command(self, command_code: int, format: str, value: Optional[int] = None) -> None: ...
    def _block_read(self, command_code: int, offset: int, length: int, format_response: Any = None) -> Any: ...
