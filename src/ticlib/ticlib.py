from functools import partial

__all__ = ['TicSerial', 'TicI2C', 'TicUSB', 'TIC_T825', 'TIC_T834', 'TIC_T500', 'TIC_N825', 'TIC_T249', 'TIC_36v4']

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
    bits = binary[::-1][start:end + 1][::-1]
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
                self.__class__,
                'get_' + name,
                partial(self.tic._block_read, GET_SETTING_CMD, offset, length, format_response))

    def get_serial_device_number(self):
        """
        Gets the serial device number from two separate bytes in the Tic's settings.
        """
        first = self.tic._block_read(GET_SETTING_CMD, 0x07, 1)
        second = self.tic._block_read(GET_SETTING_CMD, 0x69, 1)
        first = bit_range(0, 6, first)
        second = bit_range(0, 6, second)
        return first + (second << 7)

    def get_serial_alt_device_number(self):
        """
        Gets the alternative serial device number from two separate bytes in the Tic's settings.
        """
        first = self.tic._block_read(GET_SETTING_CMD, 0x6A, 1)
        second = self.tic._block_read(GET_SETTING_CMD, 0x6B, 1)
        first = bit_range(0, 6, first)
        second = bit_range(0, 6, second)
        return first + (second << 7)

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
        for command in COMMANDS:
            name, code, format = command
            setattr(self.__class__, name, partial(self._send_command, code, format))

    def _define_variables(self):
        self.variables = {}
        for variable in VARIABLES:
            name, offset, length, format_response = variable
            setattr(
                self.__class__,
                'get_' + name,
                partial(self._block_read, GET_VARIABLE_CMD, offset, length, format_response))

    def get_variables(self):
        """
        Returns all of the Tic's variables and their values.
        """
        result = {}
        for variable in VARIABLES:
            name, _, _, _ = variable
            result[name] = getattr(self, 'get_' + name)()
        return result


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
    return crc.to_bytes(1, "little")


class TicSerial(TicBase):
    """
    Serial driver for Tic stepper motor controllers.
    Reference: https://www.pololu.com/docs/0J71/9
    """

    def __init__(self, port, device_number=None, crc_for_commands=False, crc_for_responses=False):
        if serial is None:
            raise Exception("Missing dependency: pyserial")
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
        if len(result) != length:
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
                response[-1], 1, "little")
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

    def __init__(self, bus, address):
        if i2c_msg is None:
            raise Exception("Missing dependency: smbus2")
        self.bus = bus
        self.address = address
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
        self._write(serialized)

    def _block_read(self, command_code, offset, length, format_response=None):
        """
        Returns the value of the specified variable or setting from the Tic.
        """
        self._send_command(command_code, BLOCK_READ, bytes([offset, length]))
        result = self._read(length)
        if len(result) != length:
            raise RuntimeError("Expected to read {} bytes, got {}.".format(length, len(result)))
        if format_response is None:
            return result
        else:
            return format_response(result)

    def _read(self, length):
        read = i2c_msg.read(self.address, length)
        self.bus.i2c_rdwr(read)
        return read.__bytes__()[0: length]

    def _write(self, serialized):
        write = i2c_msg.write(self.address, serialized)
        self.bus.i2c_rdwr(write)


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
            return result.tobytes()
        else:
            return format_response(result)
