

import pyqtgraph as pg

## Switch to using white background and black foreground
pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')

## The following plot has inverted colors
pg.plot([1,4,2,3,5])
