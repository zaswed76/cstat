
from programm.libs import config

d = config.get_cfg("test.yaml")
for k, v in d.get("clubs").items():
    print(k, v, sep=" = ")

