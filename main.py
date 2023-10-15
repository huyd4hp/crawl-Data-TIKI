from tiki.tiki import crawlTiki
import pandas as pd
import time
import os
from sqlalchemy.engine.base import Engine
import app.settings as settings
from app.utils import initDATABASE,statusDATABASE

def main():
    if statusDATABASE():
        initDATABASE()
        tiki = crawlTiki(
            headers = settings.headers,
            proxies = settings.proxies
        )
    else:
        return
    tiki.run()

if __name__ == '__main__':
    main()




