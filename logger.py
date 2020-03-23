import json

from Register import Register, Value


class ResultLogger:
    def __init__(self):
        pass

    def log(self, results):
        print(results)


class JsonLogger(ResultLogger):
    def __init__(self):
        ResultLogger.__init__(self)

    def log(self, results):
        pass


class KeyValueLogger(ResultLogger):
    def __init__(self):
        ResultLogger.__init__(self)

    def log(self, results):
        for register, value in results.items():
            print(f"{register.name}={value}")


class TableLogger(ResultLogger):
    def __init__(self):
        ResultLogger.__init__(self)

    def log(self, results):
        max_len = max([len(key.name) for key in results.keys()])
        row_format = f"{{:>{max_len}}} = {{}}"
        for register, value in results.items():
            print(row_format.format(register.name, value))
