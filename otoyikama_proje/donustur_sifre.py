# -*- coding: utf-8 -*-
from PyQt5 import uic

with open("Sifre.py", "w", encoding="utf-8") as fout:
    uic.compileUi("Sifre.ui",fout)
