#!/usr/bin/env python
from src.analytics import pnl

def update():
    pnl_engine = pnl.engine()
    pnl_engine.update()

if __name__ == '__main__':
    update()
