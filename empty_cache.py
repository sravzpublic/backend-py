#!/usr/bin/env python
from src.services.cache import Cache

if __name__ == '__main__':
    c = Cache.Instance()
    c.remove_all()
    
