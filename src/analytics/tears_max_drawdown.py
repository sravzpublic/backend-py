#
# Copyright 2016 Quantopian, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from __future__ import division
from src.analytics import pca
from src.util import helper, logger, settings
from time import time
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from pyfolio import plotting, timeseries
# from pyfolio.plotting import plotting_context
from pyfolio.utils import (APPROX_BDAYS_PER_MONTH, MM_DISPLAY_UNIT)
import datetime
import warnings
import os
import matplotlib
import empyrical as ep
from dateutil.relativedelta import relativedelta
if os.environ.get('DISPLAY', '') == '':
    print('no display found. Using non-interactive Agg backend')
    matplotlib.use('Agg')
#from dask.distributed import Client

STAT_FUNCS_PCT = [
    'Annual return',
    'Cumulative returns',
    'Annual volatility',
    'Max drawdown',
    'Daily value at risk',
    'Daily turnover'
]

logger = logger.RotatingLogger(__name__).getLogger()

@helper.save_file_to_contabo
@helper.empty_cache
@plotting.customize
def create_returns_tear_sheet(sravzid = None,
                              upload_to_s3 = True):
    """
    Generate a number of plots for analyzing a strategy's returns.

    - Fetches benchmarks, then creates the plots on a single figure.
    - Plots: rolling returns (with cone), rolling beta, rolling sharpe,
        rolling Fama-French risk factors, drawdowns, underwater plot, monthly
        and annual return plots, daily similarity plots,
        and return quantile box plot.
    - Will also print the start and end dates of the strategy,
        performance statistics, drawdown periods, and the return range.

    Parameters
    ----------
    returns : pd.Series
        Daily returns of the strategy, noncumulative.
         - See full explanation in create_full_tear_sheet.
    positions : pd.DataFrame, optional
        Daily net position values.
         - See full explanation in create_full_tear_sheet.
    live_start_date : datetime, optional
        The point in time when the strategy began live trading,
        after its backtest period.
    cone_std : float, or tuple, optional
        If float, The standard deviation to use for the cone plots.
        If tuple, Tuple of standard deviation values to use for the cone plots
         - The cone is a normal distribution with this standard deviation
             centered around a linear regression.
    benchmark_rets : pd.Series, optional
        Daily noncumulative returns of the benchmark.
         - This is in the same style as returns.
    bootstrap : boolean (optional)
        Whether to perform bootstrap analysis for the performance
        metrics. Takes a few minutes longer.
    return_fig : boolean, optional
        If True, returns the figure that was plotted on.
    set_context : boolean, optional
        If True, set default plotting style context.
    """
    pcae = pca.engine()
    returns = pcae.get_percent_daily_returns([sravzid]).tz_localize(None)
    returns = returns[returns.index > (datetime.datetime.now() - relativedelta(years=10))]
    returns = returns.squeeze()
    logger.info("Entire data start date: %s" % returns.index[0].strftime('%Y-%m-%d'))
    logger.info("Entire data end date: %s" % returns.index[-1].strftime('%Y-%m-%d'))

    vertical_sections = 3

    widthInch = 25
    heightInch = vertical_sections * 10
    fig = plt.figure(figsize=(widthInch, heightInch), constrained_layout=True)

    gs = gridspec.GridSpec(vertical_sections, 3, wspace=1, hspace=0.5)
    # gs.update(left=0.1, right=0.9, top=0.965, bottom=0.03)

    plt.suptitle('%s Worst Drawdown Statistics %s. Start date %s End date %s.'%(sravzid,
    datetime.datetime.now().strftime("%m/%d/%Y"),
    returns.index[0].strftime('%Y-%m-%d'),
    returns.index[-1].strftime('%Y-%m-%d')))
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    i = 0
    bbox = [0, 0, 1, 1]
    ax_drawdown_stats = plt.subplot(gs[i, :])
    i += 1
    ax_drawdown = plt.subplot(gs[i, :], sharex=ax_drawdown_stats)
    i += 1
    ax_underwater = plt.subplot(gs[i, :], sharex=ax_drawdown_stats)
    drawdown_stats = timeseries.gen_drawdown_table(returns, top=5).round(3)
    drawdown_stats['Net drawdown in %'] = drawdown_stats['Net drawdown in %'].astype('float').round(2)
    ax_drawdown_stats.axis('off')
    mpl_table = ax_drawdown_stats.table(
        cellText=drawdown_stats.values, rowLabels=drawdown_stats.index, bbox=bbox, colLabels=drawdown_stats.columns)
    mpl_table.auto_set_font_size(True)
    ax_drawdown_stats.set_title("Worst Drawdown Statistics")


    plotting.plot_drawdown_periods(
        returns, top=5, ax=ax_drawdown)

    plotting.plot_drawdown_underwater(
        returns=returns, ax=ax_underwater)

    plotting.show_worst_drawdown_periods(returns)

    if upload_to_s3:
        return fig, f'{settings.constants.CONTABO_BUCKET_PREFIX}/assets/{sravzid}_worst_drawdown_statistics.jpg'
    helper.save_plt(fig)
    return None, None


if __name__ == '__main__':
    # create_returns_tear_sheet(sravzid='fut_us_gc')
    #client = Client(f'{settings.constants.DASK_SCHEDULER_HOST_NAME}:8786')
    #logger.info(f"Connected to Dask Scheduler at {settings.constants.DASK_SCHEDULER_HOST_NAME}")
    logger.info(f"Processing {settings.constants.SRAVZ_MONTHLY_RETURNS_TICKERS} tickers")
    #for ticker in settings.constants.SRAVZ_MONTHLY_RETURNS_TICKERS:
    #    create_returns_tear_sheet(ticker)
    [create_returns_tear_sheet(ticker) for ticker in settings.constants.SRAVZ_MONTHLY_RETURNS_TICKERS]
    #future = client.map(create_returns_tear_sheet, settings.constants.SRAVZ_MONTHLY_RETURNS_TICKERS)
    #result = client.gather(future)
    #logger.info(f"Processed {settings.constants.SRAVZ_MONTHLY_RETURNS_TICKERS} tickers: {result}")