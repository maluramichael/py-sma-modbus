import argparse

from modbus import Modbus
from sma import add_tripower_register

parser = argparse.ArgumentParser(description='Gather data of your sma inverter')
parser.add_argument('registers', type=int, nargs='+',
                    help='list of register numbers')
parser.add_argument('-d', '--daemon', action='store_true',
                    help='keep polling')
parser.add_argument('-i', '--interval', type=int,
                    default=1, help='time between polls')
parser.add_argument('-a', '--address', type=str,
                    required=True, help='modbus ip')
parser.add_argument('-p', '--port', type=int,
                    required=True, help='modbus port')
parser.add_argument('-u', '--unit', type=int,
                    required=True, help='modbus unit')

args = parser.parse_args()

print(args)

wr = Modbus(args.address, args.port, args.unit)

add_tripower_register(wr)

for register in args.registers:
    wr.poll_register(register)

wr.start(args)
