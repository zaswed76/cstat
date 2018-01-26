
import pandas as pd

fr = pd.DataFrame()
ser = pd.Series([1, 2, 3])
ser2 = pd.Series([4, 5, 6])
fr.append(ser, ignore_index=True)
fr.append(ser2, ignore_index=True)
print(fr)



