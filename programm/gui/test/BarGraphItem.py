

import pandas as pd


res = {1: [5, 1], 2: [3, 2], 3: [4, 3]}
r = [[k] + v for k, v in res.items()]
print(r)

df = pd.DataFrame(r, columns=["x", "y", "z"])
print(df["z"].mean())
print(pd.NaT)

