from src.analytics import pca, tears
import datetime
from dateutil.relativedelta import relativedelta
import pandas as pd

def test_create_returns_tear_sheet():
    pcae = pca.engine()
    benchmark_rets = pcae.get_percent_daily_returns(['idx_us_gspc']).tz_localize(None)
    number_of_years_back = 10
    benchmark_rets = benchmark_rets[benchmark_rets.index > datetime.datetime.now() - relativedelta(years=number_of_years_back)]
    dfs = []
    for sravzid in ['fut_us_gc', 'fut_us_cl']:
        stock_rets = pcae.get_percent_daily_returns([sravzid]).tz_localize(None)
        stock_rets = stock_rets[stock_rets.index > (datetime.datetime.now() - relativedelta(years=number_of_years_back))]
        dfs.append(tears.get_perf_stats(stock_rets.squeeze(), benchmark_rets=benchmark_rets.squeeze(), bootstrap=False, sravzid=sravzid))
    df = pd.concat(dfs)
    assert not df.empty, "DataFrame should not be empty"