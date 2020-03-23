
from pymodbus.client.sync import ModbusTcpClient
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder
import time
from threading import Thread, Lock

from Register import Value, Register, U32, U64, STR32, S32, S16, U16


class Modbus:
    def __init__(self, ip, port, unit):
        self.thread = Thread(target=self._polling_thread)
        self.register_lock = Lock()
        self.registers: [int] = []
        self.available_registers: Dict[int, Register] = {}
        self.unit = unit
        self.client = ModbusTcpClient(ip, port=port, timeout=10)
        self.polling_groups = []

    def __del__(self):
        self.client.close()

    def connect(self):
        self.client.connect()

    def poll_register(self, register_id: int):
        if not register_id in self.registers:
            if not register_id in self.available_registers:
                print(f"Register with the id {register_id} does not exist")
            else:
                register = self.available_registers[register_id]
                print(f"{register} added")
                self.registers.append(register_id)

    def add_register(self, register: Register):
        self.available_registers[register.id] = register

    def start(self, args):
        self._group_register()
        self.interval = args.interval

        self.connect()

        if args.daemon:
            self.thread.daemon = True
            self.thread.start()
            while True:
                time.sleep(10)
        else:
            self._poll()

    def _poll(self):
        for group in self.polling_groups:
            start_id = group[0].id
            length = self._length_of_group(group)
            first_register = group[0]

            response = self.client.read_holding_registers(
                start_id,
                length,
                unit=self.unit
            )

            if response:
                for index in range(len(group)):
                    register = group[index]
                    start_index = sum(
                        register.length for register in group[0:index]
                    )

                    chunk = response.registers[
                        start_index:start_index + register.length
                    ]
                    register.set_registers(chunk)
                    value = register.get_value()

                    if register.is_null():
                        value = "NAN"

                    print(f"{register} => {value}")

    def _length_of_group(self, group):
        return sum(reg.length for reg in group)

    def _polling_thread(self):
        while True:
            with self.register_lock:
                self._poll()
                time.sleep(self.interval)

    def _group_register(self):
        if len(self.registers) == 0:
            return

        self.registers.sort()

        polling_groups = [[]]

        next_id = self.registers[0]
        for id in self.registers:
            register = self.available_registers[id]

            if register == None:
                continue

            if next_id != id:
                polling_groups.append([])

            current_group = polling_groups[len(polling_groups) - 1]
            current_group.append(register)
            next_id = register.id + register.length

        self.polling_groups = polling_groups
