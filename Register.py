from datetime import datetime

from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder


class Value:
    def __init__(self, value):
        self.date = datetime.timestamp(datetime.now())
        self.value = value


class Register:
    def __init__(self, id, name, description, length):
        self.id = id
        self.name = name
        self.description = description
        self.length = length
        self.value = None
        self.registers = []

    def __str__(self):
        return f"{self.id} {self.name} ({self.description})"

    def set_registers(self, registers):
        self.registers = registers

    def is_null(self):
        return None

    def get_value(self):
        return None


class S16(Register):
    def __init__(self, register_id, name, description, length=1):
        Register.__init__(self, register_id, name, description, length)

    def get_value(self):
        return BinaryPayloadDecoder.fromRegisters(self.registers, byteorder=Endian.Big).decode_16bit_int()

    def is_null(self):
        return self.get_value() == 0x8000


class S32(Register):
    def __init__(self, register_id, name, description, length=2):
        Register.__init__(self, register_id, name, description, length)

    def get_value(self):
        return BinaryPayloadDecoder.fromRegisters(self.registers, byteorder=Endian.Big).decode_32bit_int()

    def is_null(self):
        return self.get_value() == 0x80000000


class U16(Register):
    def __init__(self, register_id, name, description, length=1):
        Register.__init__(self, register_id, name, description, length)

    def get_value(self):
        return BinaryPayloadDecoder.fromRegisters(self.registers, byteorder=Endian.Big).decode_16bit_uint()

    def is_null(self):
        return self.get_value() == 0xFFFF


class U32(Register):
    def __init__(self, register_id, name, description, length=2):
        Register.__init__(self, register_id, name, description, length)

    def get_value(self):
        return BinaryPayloadDecoder.fromRegisters(self.registers, byteorder=Endian.Big).decode_32bit_uint()

    def is_null(self):
        return self.get_value() == 0xFFFFFFFF or self.get_value() == 0xFFFFFD


class U64(Register):
    def __init__(self, register_id, name, description, length=4):
        Register.__init__(self, register_id, name, description, length)

    def get_value(self):
        return BinaryPayloadDecoder.fromRegisters(self.registers, byteorder=Endian.Big).decode_64bit_uint()

    def is_null(self):
        return self.get_value() == 0xFFFFFFFFFFFFFFFF


class STR32(Register):
    def __init__(self, register_id, name, description, length=8):
        Register.__init__(self, register_id, name, description, length)

    def get_value(self):
        return BinaryPayloadDecoder.fromRegisters(self.registers, byteorder=Endian.Big).decode_string()

    def is_null(self):
        return self.get_value() == ""
