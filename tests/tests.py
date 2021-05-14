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

import sys

# Add the `ticlib` package to the system path
sys.path.append('/'.join(__file__.split('/')[0:-2]) + '/src')

from ticlib import *


def int_to_bytes(value, length):
    if value < 0:
        value = value + 2**32
    return value.to_bytes(length, 'little')


class Tests(object):

    def test_multiple_tics(self):
        """
        Ensure that multiple Tics can be used at the same time.
        See: https://github.com/jphalip/ticlib/issues/1
        """
        tic1 = TicUSB()
        tic1.usb.set_returned_values([int_to_bytes(1, 4)])
        tic2 = TicUSB()
        tic2.usb.set_returned_values([int_to_bytes(2, 4)])
        assert tic1.get_current_position() == 1
        assert tic2.get_current_position() == 2

    def test_usb_commands(self):
        tic = TicUSB()
        # 32-bit parameter
        tic.set_target_position(-99)
        assert tic.usb.calls[-1] == (0x40, 0xE0, 65437, 65535, 0)
        # 7-bit parameter
        tic.go_home(1)
        assert tic.usb.calls[-1] == (0x40, 0x97, 1, 0, 0)
        # Quick command (no parameters)
        tic.energize()
        assert tic.usb.calls[-1] == (0x40, 0x85, 0, 0, 0)

    def test_variable_incorrect_length(self):
        tic = TicUSB()
        tic.usb.set_returned_values([int_to_bytes(42, 2)])
        try:
            tic.get_current_position()
        except RuntimeError as excinfo:
            assert str(excinfo) == "Expected to read 4 bytes, got 2."
        else:
            raise Exception()

    def test_variable_success(self):
        tic = TicUSB()
        tic.usb.set_returned_values([int_to_bytes(42, 4)])
        assert tic.get_current_position() == 42

    def test_boolean(self):
        """
        Ensure that indexed booleans are correctly read from bytes.
        """
        tic = TicUSB()
        tic.usb.set_returned_values([int_to_bytes(0b00000100, 1)])
        assert tic.settings.get_serial_14bit_device_number() is False
        tic.usb.set_returned_values([int_to_bytes(0b00001000, 1)])
        assert tic.settings.get_serial_14bit_device_number() is True

    def test_signed_int(self):
        tic = TicUSB()
        tic.usb.set_returned_values([int_to_bytes(-99, 4)])
        assert tic.get_target_position() == -99

    def test_unsigned_int(self):
        tic = TicUSB()
        tic.usb.set_returned_values([int_to_bytes(-99, 4)])
        assert tic.get_max_speed() == 4294967197

    def test_get_serial_device_number(self):
        tic = TicUSB()
        tic.usb.set_returned_values([int_to_bytes(0b00000010, 1), int_to_bytes(0b00000100, 1)])
        assert tic.settings.get_serial_device_number() == 0b00001000000010

    def test_get_serial_alt_device_number(self):
        tic = TicUSB()
        tic.usb.set_returned_values([int_to_bytes(0b00000010, 1), int_to_bytes(0b00000100, 1)])
        assert tic.settings.get_serial_alt_device_number() == 0b00001000000010


if __name__ == '__main__':
    tests = Tests()
    for method in dir(tests):
        if method.startswith('test_'):
            getattr(tests, method)()
            print(method + " ... ok")
