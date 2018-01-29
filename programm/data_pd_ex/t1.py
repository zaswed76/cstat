
import pandas as pd


d = {14: 1.83, 15: 2.17, 16: 0.17}
r = [d.keys(), d.values()]

pd.Series

df1 = pd.DataFrame(list(d.items()))
print(df1)
