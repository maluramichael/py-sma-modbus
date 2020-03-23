# py-sma-modbus

## Installation

```sh
git clone git@github.com:maluramichael/py-sma-modbus.git
cd py-sma-modbus
pip install -r requirements.txt
```

## Usage

```sh
usage: main.py [-h] [-d] [-i INTERVAL] -a ADDRESS -p PORT -u UNIT
               registers [registers ...]

Gather data of your sma inverter

positional arguments:
  registers             list of register numbers

optional arguments:
  -h, --help            show this help message and exit
  -d, --daemon          keep polling
  -i INTERVAL, --interval INTERVAL
                        time between polls
  -a ADDRESS, --address ADDRESS
                        modbus ip
  -p PORT, --port PORT  modbus port
  -u UNIT, --unit UNIT  modbus unit
```

## Examples

```sh
$ python main.py -i10 -a"192.168.178.46" -p502 -u3 30775
Namespace(address='192.168.178.46', daemon=False, interval=10, port=502, registers=[30775], unit=3)
30775 GridMs.TotW (Leistung) added
30775 GridMs.TotW (Leistung) => 4186
```

```sh
$ python main.py -d -i1 -a"192.168.178.46" -p502 -u3 30775
Namespace(address='192.168.178.46', daemon=True, interval=1, port=502, registers=[30775], unit=3)
30775 GridMs.TotW (Leistung) added
30775 GridMs.TotW (Leistung) => 4193
30775 GridMs.TotW (Leistung) => 4194
30775 GridMs.TotW (Leistung) => 4194
30775 GridMs.TotW (Leistung) => 4193
30775 GridMs.TotW (Leistung) => 4194
30775 GridMs.TotW (Leistung) => 4190
```

```sh
$ python main.py -d -i5 -a"192.168.178.46" -p502 -u3 30775 30529
Namespace(address='192.168.178.46', daemon=True, interval=5, port=502, registers=[30775, 30529], unit=3)
30775 GridMs.TotW (Leistung) added
30529 Metering.TotWhOut (Gesamtertrag Wh) added
30529 Metering.TotWhOut (Gesamtertrag Wh) => 2410952
30775 GridMs.TotW (Leistung) => 4190
30529 Metering.TotWhOut (Gesamtertrag Wh) => 2410958
30775 GridMs.TotW (Leistung) => 4186
30529 Metering.TotWhOut (Gesamtertrag Wh) => 2410964
30775 GridMs.TotW (Leistung) => 4189
```
