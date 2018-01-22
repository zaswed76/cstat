


import pandas as pd


d = dict(vis=[1,2,3,4], load=[7,8,9,6], rrr=['a', 'b', 'c', 'd'])

tab = pd.DataFrame(d)
print(tab)
print("----------------")
print(
    tab[
        (tab["load"]>7) &
        (tab["rrr"]=="b")
    ]
)