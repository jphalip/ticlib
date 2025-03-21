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
    MicroPython fallback for functools.partial.
    """
    ...

def boolean(bit_index: int, value: bytes) -> bool:
    """
    Returns True if the bit located at 'bit_index' in the given 'value' is set.
    The least-significant bit is index 0.
    """
    ...

def bit_range(start: int, end: int, value: bytes) -> int:
    """
    Returns the bits between 'start' and 'end' in 'value'.
    """
    ...

def signed_int(value: bytes) -> int:
    """
    Interprets 'value' (little-endian) as a signed integer.
    """
    ...

def unsigned_int(value: bytes) -> int:
    """
    Interprets 'value' (little-endian) as an unsigned integer.
    """
    ...

def _get_crc_7(message: bytes) -> bytes:
    """
    Calculates the 7-bit CRC for 'message' per Pololu's documentation.
    """
    ...

class MachineI2CBackend:
    """
    I2C backend that wraps 'machine.I2C'.
    """

    def __init__(self, i2c: Any, address: int) -> None: ...
    def read(self, length: int) -> bytes: ...
    def write(self, serialized: bytes) -> None: ...

class SMBus2Backend:
    """
    I2C backend that uses smbus2.
    """

    def __init__(self, bus: Any, address: int) -> None: ...
    def read(self, length: int) -> bytes: ...
    def write(self, serialized: bytes) -> None: ...

#
# TicBase merges commands, variable getters, and settings
#
class TicBase:
    """
    Base class for Pololu Tic controllers. Dynamically defines:
    - Commands (e.g. set_target_position)
    - Variable getters (e.g. get_operation_state)
    - Setting getters (e.g. get_control_mode)
    """

    def __init__(self) -> None: ...

    def _send_command(self, command_code: int, format: str,
                      value: Optional[int] = None) -> None: ...
    def _block_read(self, command_code: int, offset: int, length: int,
                    format_response: Any = None) -> Any: ...
    def _define_commands(self) -> None: ...
    def _define_variables(self) -> None: ...

    def get_variables(self) -> Dict[str, Any]:
        """
        Returns a dictionary of all Tic variables (name -> value).
        """
        ...

    #
    # ---------------------------
    # Command stubs
    # ---------------------------
    #
    def set_target_position(self, value: int) -> None:
        """
        Command: 0xE0

        Format: 32-bit write

        Data: target position, signed 32-bit

        Range: -2,147,483,648 to +2,147,483,647

        Units: microsteps

        This sets the Tic's target position in microsteps.
        If control mode is Serial/I2C/USB, it moves the motor accordingly.
        Otherwise, silently ignored.
        """
        ...

    def set_target_velocity(self, value: int) -> None:
        """
        Command: 0xE3

        Format: 32-bit write

        Data: target velocity, signed 32-bit

        Range: -500,000,000 to +500,000,000

        Units: microsteps per 10,000 s

        This sets the Tic's target velocity. If control mode = Serial/I2C/USB,
        the motor accelerates or decelerates to that velocity.
        """
        ...

    def halt_and_set_position(self, value: int) -> None:
        """
        Command: 0xEC

        Format: 32-bit write

        Data: current position, signed 32-bit

        Range: -2,147,483,648 to +2,147,483,647

        Units: microsteps

        Abruptly halts the motor (ignoring deceleration) and sets 'Current position'.
        Clears 'position uncertain', sets input state to 'halt', clears 'input after scaling'.
        """
        ...

    def halt_and_hold(self) -> None:
        """
        Command: 0x89

        Format: Quick

        Abruptly halts the motor, sets 'position uncertain' = True, input state = 'halt',
        and clears 'input after scaling'.
        """
        ...

    def go_home(self, value: int) -> None:
        """
        Command: 0x97

        Format: 7-bit write

        Data:
          0 = Home in reverse direction
          1 = Home in forward direction

        Starts the homing procedure in the chosen direction.
        """
        ...

    def reset_command_timeout(self) -> None:
        """
        Command: 0x8C

        Format: Quick

        Resets the command timeout to prevent 'command timeout' errors.
        """
        ...

    def deenergize(self) -> None:
        """
        Command: 0x86

        Format: Quick

        Disables the driver, de-energizing coils. Sets 'position uncertain'
        and 'intentionally de-energized' error bit.
        """
        ...

    def energize(self) -> None:
        """
        Command: 0x85

        Format: Quick

        Requests enabling the stepper driver if no other errors exist,
        clearing 'intentionally de-energized'.
        """
        ...

    def exit_safe_start(self) -> None:
        """
        Command: 0x83

        Format: Quick

        Clears the 'safe start violation' error for ~200 ms (if control mode = Serial/I2C/USB).
        """
        ...

    def enter_safe_start(self) -> None:
        """
        Command: 0x8F

        Format: Quick

        Triggers safe start if enabled, halting motor with the soft error response.
        """
        ...

    def reset(self) -> None:
        """
        Command: 0xB0

        Format: Quick

        Reloads settings from non-volatile memory, abruptly halts motor,
        resets driver, clears certain errors, enters safe start if configured.
        Not a full microcontroller reset (uptime unaffected).
        """
        ...

    def clear_driver_error(self) -> None:
        """
        Command: 0x8A

        Format: Quick

        Clears a latched driver error if 'auto_clear_driver_error' is off.
        Otherwise, no effect.
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

        Sets the speed below which instant acceleration/deceleration is allowed,
        overriding the default until reset.
        """
        ...

    def set_max_acceleration(self, value: int) -> None:
        """
        Command: 0xEA

        Format: 32-bit write

        Data: max acceleration, unsigned 32-bit

        Range: 100 to 2,147,483,647

        Units: microsteps per 100 s^2

        Temporarily sets the Tic's max acceleration until reset.
        If <100, it is treated as 100.
        """
        ...

    def set_max_deceleration(self, value: int) -> None:
        """
        Command: 0xE9

        Format: 32-bit write

        Data: max deceleration, unsigned 32-bit

        Range: 100 to 2,147,483,647

        Units: microsteps per 100 s^2

        Temporarily sets the Tic's max deceleration until reset.
        If 0, it is set = current max acceleration.
        If <100, it is treated as 100.
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
        4: 1/16 step (T834, T825, 36v4)
        5: 1/32 step (T834, T825, 36v4)
        6: 1/2 step 100% (T249)
        7: 1/64 (36v4)
        8: 1/128 (36v4)
        9: 1/256 (36v4)

        Temporarily sets the microstepping mode until reset or reinit.
        """
        ...

    def set_current_limit(self, value: int) -> None:
        """
        Command: 0x91

        Format: 7-bit write

        Data: current limit, unsigned 7-bit
        (range depends on Tic model, typically in mA)

        Temporarily sets coil current limit until reset.
        """
        ...

    def set_decay_mode(self, value: int) -> None:
        """
        Command: 0x92

        Format: 7-bit write

        Data: decay mode, unsigned 7-bit

        Examples:
          Tic T500: 0=Automatic
          Tic T834: 0=Mixed50%,1=Slow,2=Fast,3=Mixed25%,4=Mixed75%
          Tic T825: 0=Mixed,1=Slow,2=Fast
          Tic T249: 0=Mixed

        Temporarily sets driver decay mode (no effect on 36v4).
        """
        ...

    def set_agc_option(self, value: int) -> None:
        """
        Command: 0x98

        Format: 7-bit write

        Data: upper 3 bits = AGC option, lower 4 bits = new value
             0=AGC mode
             1=AGC bottom current limit
             2=AGC current boost steps
             3=AGC frequency limit

        Valid only on Tic T249. Temporarily changes AGC config until reset.
        """
        ...

    #
    # --------------------------------
    # Variable stubs 
    # --------------------------------
    #
    def get_operation_state(self) -> int:
        """
        Offset: 0x00

        Type: unsigned 8-bit

        Describes the Tic's high-level operation state (Section 5.4).

        Possible values:
          0=Reset,2=De-energized,4=Soft error,6=Wait ERR,
          8=Starting up,10=Normal
        """
        ...

    def get_misc_flags(self) -> int:
        """
        Offset: 0x01

        Type: unsigned 8-bit

        Bitmask for additional status:
          Bit0=Energized,Bit1=Position uncertain,
          Bit2=Forward limit,Bit3=Reverse limit,
          Bit4=Homing active
        """
        ...

    def get_error_status(self) -> int:
        """
        Offset: 0x02

        Type: unsigned 16-bit

        Errors currently stopping motor (bitmask).
          Bit0=Intentionally de-energized,
          Bit1=Motor driver error,
          Bit2=Low VIN,
          Bit3=Kill switch,
          Bit4=Input invalid,
          Bit5=Serial error,
          Bit6=Command timeout,
          Bit7=Safe start violation,
          Bit8=ERR line high
        """
        ...

    def get_error_occured(self) -> int:
        """
        Offset: 0x04

        Type: unsigned 32-bit

        Bitmask of all errors that have occurred since last clear,
        including bits for framing, overrun, CRC, etc.
        """
        ...

    def get_planning_mode(self) -> int:
        """
        Offset: 0x09

        Type: unsigned 8-bit

        0=Off,1=Target position,2=Target velocity
        """
        ...

    def get_target_position(self) -> int:
        """
        Offset: 0x0A

        Type: signed 32-bit

        Range: -2,147,483,648 to +2,147,483,647

        Units: microsteps

        If planning mode=Target position, this is the commanded position.
        """
        ...

    def get_target_velocity(self) -> int:
        """
        Offset: 0x0E

        Type: signed 32-bit

        Range: -500,000,000 to +500,000,000

        Units: microsteps per 10,000 s

        If planning mode=Target velocity, this is the commanded velocity.
        """
        ...

    def get_starting_speed(self) -> int:
        """
        Offset: 0x12

        Type: unsigned 32-bit

        Range: 0 to 500,000,000

        Units: microsteps per 10,000 s

        The speed below which instant acceleration is allowed.
        """
        ...

    def get_max_speed(self) -> int:
        """
        Offset: 0x16

        Type: unsigned 32-bit

        Range: 0 to 500,000,000

        Units: microsteps per 10,000 s

        The Tic's maximum allowed speed.
        """
        ...

    def get_max_deceleration(self) -> int:
        """
        Offset: 0x1A

        Type: unsigned 32-bit

        Range: 100 to 2,147,483,647

        Units: microsteps per 100 s^2

        The Tic's maximum allowed deceleration.
        """
        ...

    def get_max_acceleration(self) -> int:
        """
        Offset: 0x1E

        Type: unsigned 32-bit

        Range: 100 to 2,147,483,647

        Units: microsteps per 100 s^2

        The Tic's maximum allowed acceleration.
        """
        ...

    def get_current_position(self) -> int:
        """
        Offset: 0x22

        Type: signed 32-bit

        Range: -2,147,483,648 to +2,147,483,647

        Units: microsteps

        The current position (accumulated commanded steps).
        """
        ...

    def get_current_velocity(self) -> int:
        """
        Offset: 0x26

        Type: signed 32-bit

        Range: -500,000,000 to +500,000,000

        Units: microsteps per 10,000 s

        The current commanded velocity.
        """
        ...

    def get_acting_target_position(self) -> int:
        """
        Offset: 0x2A

        Type: signed 32-bit

        Units: microsteps

        Internal variable used in target position step planning.
        """
        ...

    def get_time_since_last_step(self) -> int:
        """
        Offset: 0x2E

        Type: unsigned 32-bit

        Units: 1/3 microseconds

        Internal timer for step planning.
        """
        ...

    def get_device_reset(self) -> int:
        """
        Offset: 0x32

        Type: unsigned 8-bit

        Last full microcontroller reset cause:
          0=Power up,1=Brown-out,2=Ext reset,
          4=Watchdog,8=Software,16=Stack overflow,32=Stack underflow
        """
        ...

    def get_vin_voltage(self) -> int:
        """
        Offset: 0x33

        Type: unsigned 16-bit

        Units: millivolts

        The measured VIN voltage.
        """
        ...

    def get_uptime(self) -> int:
        """
        Offset: 0x35

        Type: unsigned 32-bit

        Units: milliseconds

        Time since the controller's last full reset (not changed by 'reset' command).
        """
        ...

    def get_encoder_position(self) -> int:
        """
        Offset: 0x39

        Type: signed 32-bit

        Units: encoder ticks

        Raw quadrature encoder count from TX/RX pins.
        """
        ...

    def get_rc_pulse(self) -> int:
        """
        Offset: 0x3D

        Type: unsigned 16-bit

        Units: 1/12 microseconds

        The measured width of the RC pulse. 0xFFFF if invalid.
        """
        ...

    def get_analog_reading_scl(self) -> int:
        """
        Offset: 0x3F

        Type: unsigned 16-bit

        Default: not applicable

        Range: 0 to 0xFFFE

        Units: ~0=0V, ~0xFFFE=5V

        The analog reading on SCL if enabled. 0xFFFF if not available.
        """
        ...

    def get_analog_reading_sda(self) -> int:
        """
        Offset: 0x41

        Type: unsigned 16-bit

        Default: not applicable

        Range: 0 to 0xFFFE

        Units: ~0=0V, ~0xFFFE=5V

        The analog reading on SDA if enabled. 0xFFFF if not available.
        """
        ...

    def get_analog_reading_tx(self) -> int:
        """
        Offset: 0x43

        Type: unsigned 16-bit

        Default: not applicable

        Range: 0 to 0xFFFE

        Units: ~0=0V, ~0xFFFE=5V

        The analog reading on TX if enabled. 0xFFFF if not available.
        """
        ...

    def get_analog_reading_rx(self) -> int:
        """
        Offset: 0x45

        Type: unsigned 16-bit

        Default: not applicable

        Range: 0 to 0xFFFE

        Units: ~0=0V, ~0xFFFE=5V

        The analog reading on RX if enabled. 0xFFFF if not available.
        """
        ...

    def get_digital_readings(self) -> int:
        """
        Offset: 0x47

        Type: unsigned 8-bit

        Bitmask of digital reads:
          Bit0=SCL,Bit1=SDA,Bit2=TX,Bit3=RX,Bit4=RC
        """
        ...

    def get_pin_states(self) -> int:
        """
        Offset: 0x48

        Type: unsigned 8-bit

        Each pair of bits = pin state:
          0=Hi-Z,1=Pullup,2=Low,3=High
        Groups: [0..1]=SCL,[2..3]=SDA,[4..5]=TX,[6..7]=RX
        """
        ...

    def get_step_mode(self) -> int:
        """
        Offset: 0x49

        Type: unsigned 8-bit

        Current driver microstepping mode:
          0=Full,1=1/2,2=1/4,3=1/8,4=1/16,
          5=1/32,6=1/2(100%),7=1/64,8=1/128,9=1/256
        """
        ...

    def get_current_limit(self) -> int:
        """
        Offset: 0x4A

        Type: unsigned 8-bit

        The coil current limit in driver-specific units.
        """
        ...

    def get_decay_mode(self) -> int:
        """
        Offset: 0x4B

        Type: unsigned 8-bit

        (Not valid for 36v4)

        Driver decay mode if applicable (auto, mixed, slow, fast...).
        """
        ...

    def get_input_state(self) -> int:
        """
        Offset: 0x4C

        Type: unsigned 8-bit

        The main input state:
          0=Not ready,1=Invalid,2=Halt,3=Target pos,4=Target velocity
        """
        ...

    def get_input_after_averaging(self) -> int:
        """
        Offset: 0x4D

        Type: unsigned 16-bit

        Intermediate analog/RC reading after averaging. 0xFFFF if not available.
        """
        ...

    def get_input_after_hysteresis(self) -> int:
        """
        Offset: 0x4F

        Type: unsigned 16-bit

        Intermediate reading after hysteresis. 0xFFFF if not available.
        """
        ...

    def get_input_after_scaling(self) -> int:
        """
        Offset: 0x51

        Type: signed 32-bit

        The final scaled input value (target position or velocity).
        """
        ...

    def get_last_motor_driver_error(self) -> int:
        """
        Offset: 0x55

        Type: unsigned 8-bit

        (Tic T249 only)

        Last driver error cause:
          0=None,1=Overcurrent,2=Overtemp
        """
        ...

    def get_agc_mode(self) -> int:
        """
        Offset: 0x56

        Type: unsigned 8-bit

        (T249 only)

        The AGC mode: 0=Off,1=On,2=ActiveOff
        """
        ...

    def get_agc_bottom_current_limit(self) -> int:
        """
        Offset: 0x57

        Type: unsigned 8-bit

        (T249 only)

        The bottom current limit: 0=45%,1=50%,2=55%,3=60%,4=65%,5=70%,6=75%,7=80%
        """
        ...

    def get_agc_current_boost_steps(self) -> int:
        """
        Offset: 0x58

        Type: unsigned 8-bit

        (T249 only)

        The AGC current boost steps: 0=5,1=7,2=9,3=11
        """
        ...

    def get_agc_frequency_limit(self) -> int:
        """
        Offset: 0x59

        Type: unsigned 8-bit

        (T249 only)

        The AGC frequency limit: 0=Off,1=225Hz,2=450Hz,3=675Hz
        """
        ...

    def get_last_hp_driver_errors(self) -> int:
        """
        Offset: 0xFF

        Type: unsigned 8-bit

        (36v4 only)

        Bitmask of last high-power driver errors:
          Bit0=Overtemp,Bit1=OvercurrentA,Bit2=OvercurrentB,
          Bit3=PredriverA,Bit4=PredriverB,Bit5=Undervoltage,
          Bit7=Verification fail
        """
        ...



class Settings:
    """
    Class used to manage the Tic's settings.
    Dynamically adds get_<setting>() methods using partial().
    """

    def __init__(self, tic: Any) -> None:
        """
        For each setting in SETTINGS, sets an attribute 'get_<name>' that calls tic._block_read(...).
        """
        ...

    def get_serial_device_number(self) -> int:
        """
        Gets the serial device number from two separate bytes in the Tic's settings.
        """
        ...

    def get_serial_alt_device_number(self) -> int:
        """
        Gets the alternative serial device number from two separate bytes in the Tic's settings.
        """
        ...

    def get_all(self) -> dict[str, Any]:
        """
        Returns all of the Tic's settings and their values.
        """
        ...

    # Stubs for each get_<setting>() method with docstrings

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


class TicSerial(TicBase):
    """
    Serial driver for Tic stepper motor controllers.
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
    I2C driver for Tic stepper motor controllers.
    Reference: https://www.pololu.com/docs/0J71/10
    """

    def __init__(self, backend: Any) -> None: ...
    def _send_command(self, command_code: int, format: str, value: Optional[int] = None) -> None: ...
    def _block_read(self, command_code: int, offset: int, length: int, format_response: Any = None) -> Any: ...

class TicUSB(TicBase):
    """
    USB driver for Tic stepper motor controllers.
    Reference: https://www.pololu.com/docs/0J71/11
    """

    def __init__(
        self,
        product: Optional[int] = None,
        serial_number: Optional[str] = None
    ) -> None: ...
    def _send_command(self, command_code: int, format: str, value: Optional[int] = None) -> None: ...
    def _block_read(self, command_code: int, offset: int, length: int, format_response: Any = None) -> Any: ...
