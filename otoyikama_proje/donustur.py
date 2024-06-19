# -*- coding: utf-8 -*-
from PyQt5 import uic

with open("widgets.py", "w", encoding="utf-8") as fout:
    uic.compileUi("main.ui",fout)
