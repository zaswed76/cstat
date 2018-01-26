
import pandas as pd

fr = pd.DataFrame(columns=["a", "b", "c"])
ser = [2, 3]
ser2 = [5, 6]
fr.loc[0] = ser
fr.loc[1] = ser2
print(fr)



