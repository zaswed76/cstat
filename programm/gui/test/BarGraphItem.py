
from itertools import zip_longest
from collections.abc import Container

# class ProTimeVis(Container):
#     def __init__(self, time, visitor):
#         self.data = list(zip(time, visitor))
#         self.res = []
#
#     def __contains__(self, n):
#         for t, v in self.data:
#             if t == n:
#                 self.res.append(v)
#                 return True
#             else:
#                 self.res.append(None)
#                 return False

time = [9, 10, 11, 12, 13]
pro_time = [10, 13]

pro_vis =[1, 3]
rs = [0, 1, 0, 0, 3]

rst = [0]* len(time)

for n, t in enumerate(time):
    if t in pro_time:
        i = pro_time.index(t)
        rst[n] = pro_vis[i]


print(rst)


