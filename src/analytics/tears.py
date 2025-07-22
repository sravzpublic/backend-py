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
from statsmodels.tsa.stattools import adfuller
from sklearn.decomposition import PCA
from src.analytics import pca, portfolio
from src.services import price_queries
from src.util import helper, settings, logger
from collections import OrderedDict
from time import time
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.colors as mcolors
import numpy as np
import scipy.stats
import pandas as pd
import seaborn as sns
from pyfolio import plotting, utils, timeseries
# from pyfolio.plotting import plotting_context
from pyfolio import _seaborn as sns
from pyfolio.utils import (APPROX_BDAYS_PER_MONTH, MM_DISPLAY_UNIT)
import empyrical
import warnings
import datetime
import os
import matplotlib
import uuid
import empyrical as ep
if os.environ.get('DISPLAY', '') == '':
    print('no display found. Using non-interactive Agg backend')
    matplotlib.use('Agg')
try:
    from pyfolio import bayesian
    have_bayesian = True
except ImportError:
    warnings.warn(
        "Could not import bayesian submodule due to missing pymc3 dependency.",
        ImportWarning)
    have_bayesian = False

STAT_FUNCS_PCT = [
    'Annual return',
    'Cumulative returns',
    'Annual volatility',
    'Max drawdown',
    'Daily value at risk',
    'Daily turnover'
]

logger = logger.RotatingLogger(__name__).getLogger()

def show_perf_stats(returns, factor_returns=None, positions=None,
                    transactions=None, turnover_denom='AGB',
                    live_start_date=None, bootstrap=False,
                    header_rows=None):
    """
    Prints some performance metrics of the strategy.
    - Shows amount of time the strategy has been run in backtest and
      out-of-sample (in live trading).
    - Shows Omega ratio, max drawdown, Calmar ratio, annual return,
      stability, Sharpe ratio, annual volatility, alpha, and beta.
    Parameters
    ----------
    returns : pd.Series
        Daily returns of the strategy, noncumulative.
         - See full explanation in tears.create_full_tear_sheet.
    factor_returns : pd.Series, optional
        Daily noncumulative returns of the benchmark factor to which betas are
        computed. Usually a benchmark such as market returns.
         - This is in the same style as returns.
    positions : pd.DataFrame, optional
        Daily net position values.
         - See full explanation in create_full_tear_sheet.
    transactions : pd.DataFrame, optional
        Prices and amounts of executed trades. One row per trade.
        - See full explanation in tears.create_full_tear_sheet
    turnover_denom : str, optional
        Either AGB or portfolio_value, default AGB.
        - See full explanation in txn.get_turnover.
    live_start_date : datetime, optional
        The point in time when the strategy began live trading, after
        its backtest period.
    bootstrap : boolean, optional
        Whether to perform bootstrap analysis for the performance
        metrics.
         - For more information, see timeseries.perf_stats_bootstrap
    header_rows : dict or OrderedDict, optional
        Extra rows to display at the top of the displayed table.
    """

    if bootstrap:
        perf_func = timeseries.perf_stats_bootstrap
    else:
        perf_func = timeseries.perf_stats

    perf_stats_all = perf_func(
        returns,
        factor_returns=factor_returns,
        positions=positions,
        transactions=transactions,
        turnover_denom=turnover_denom)

    date_rows = OrderedDict()
    if len(returns.index) > 0:
        date_rows['Start date'] = returns.index[0].strftime('%Y-%m-%d')
        date_rows['End date'] = returns.index[-1].strftime('%Y-%m-%d')

    if live_start_date is not None:
        live_start_date = ep.utils.get_utc_timestamp(live_start_date)
        returns_is = returns[returns.index < live_start_date]
        returns_oos = returns[returns.index >= live_start_date]

        positions_is = None
        positions_oos = None
        transactions_is = None
        transactions_oos = None

        if positions is not None:
            positions_is = positions[positions.index < live_start_date]
            positions_oos = positions[positions.index >= live_start_date]
            if transactions is not None:
                transactions_is = transactions[(transactions.index <
                                                live_start_date)]
                transactions_oos = transactions[(transactions.index >
                                                 live_start_date)]

        perf_stats_is = perf_func(
            returns_is,
            factor_returns=factor_returns,
            positions=positions_is,
            transactions=transactions_is,
            turnover_denom=turnover_denom)

        perf_stats_oos = perf_func(
            returns_oos,
            factor_returns=factor_returns,
            positions=positions_oos,
            transactions=transactions_oos,
            turnover_denom=turnover_denom)
        if len(returns.index) > 0:
            date_rows['In-sample months'] = int(len(returns_is) /
                                                APPROX_BDAYS_PER_MONTH)
            date_rows['Out-of-sample months'] = int(len(returns_oos) /
                                                    APPROX_BDAYS_PER_MONTH)

        perf_stats = pd.concat(OrderedDict([
            ('In-sample', perf_stats_is),
            ('Out-of-sample', perf_stats_oos),
            ('All', perf_stats_all),
        ]), axis=1)
    else:
        if len(returns.index) > 0:
            date_rows['Total months'] = int(len(returns) /
                                            APPROX_BDAYS_PER_MONTH)
        perf_stats = pd.DataFrame(perf_stats_all, columns=['Backtest'])

    for column in perf_stats.columns:
        for stat, value in perf_stats[column].items():
            if stat in STAT_FUNCS_PCT:
                # Deprecated will be in future, cannot assing string to float.
                # Keep it float.
                perf_stats.loc[stat, column] = np.round(value * 100, 3) #str(np.round(value * 100, 3)) + '%'
    if header_rows is None:
        header_rows = date_rows
    else:
        header_rows = OrderedDict(header_rows)
        header_rows.update(date_rows)

    return perf_stats
    
def get_perf_stats(returns, positions=None,
                              live_start_date=None,
                              cone_std=(1.0, 1.5, 2.0),
                              benchmark_rets=None,
                              bootstrap=False,
                              return_fig=False,
                              sravzid = None):
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

    if benchmark_rets is None:
        benchmark_rets = utils.get_symbol_rets('SPY')
        # If the strategy's history is longer than the benchmark's, limit
        # strategy
        if returns.index[0] < benchmark_rets.index[0]:
            returns = returns[returns.index > benchmark_rets.index[0]]

    logger.info("Entire data start date: %s" % returns.index[0].strftime('%Y-%m-%d'))
    logger.info("Entire data end date: %s" % returns.index[-1].strftime('%Y-%m-%d'))

    # If the strategy's history is longer than the benchmark's, limit strategy
    if returns.index[0] < benchmark_rets.index[0]:
        returns = returns[returns.index > benchmark_rets.index[0]]

    if not returns.index.difference(benchmark_rets.index).empty:
        # logger.info(f"Strategy has more indexes than benchmark - dropping ${returns.index.difference(benchmark_rets.index)}")
        returns = returns.loc[benchmark_rets.index.intersection(returns.index)]

    perf_stats = show_perf_stats(returns, benchmark_rets,
                             positions=positions,
                             bootstrap=bootstrap,
                             live_start_date=live_start_date)


    returns_stats = pd.DataFrame(returns.describe(), columns=['Backtest'])
    for i, v in returns.describe().items():
        perf_stats.at[i, 'Backtest'] = v
    perf_stats = perf_stats.T
    perf_stats['Start date'] = returns.index[0].strftime('%Y-%m-%d')
    perf_stats['End date'] = returns.index[-1].strftime('%Y-%m-%d')
    perf_stats = perf_stats.rename(index={'Backtest': sravzid})
    return perf_stats

@plotting.customize
def create_returns_tear_sheet(returns, positions=None,
                              live_start_date=None,
                              cone_std=(1.0, 1.5, 2.0),
                              benchmark_rets=None,
                              bootstrap=False,
                              return_fig=False,
                              sravzid = None):
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

    if benchmark_rets is None:
        benchmark_rets = utils.get_symbol_rets('SPY')
        # If the strategy's history is longer than the benchmark's, limit
        # strategy
        if returns.index[0] < benchmark_rets.index[0]:
            returns = returns[returns.index > benchmark_rets.index[0]]

    logger.info("Entire data start date: %s" % returns.index[0].strftime('%Y-%m-%d'))
    logger.info("Entire data end date: %s" % returns.index[-1].strftime('%Y-%m-%d'))

    # If the strategy's history is longer than the benchmark's, limit strategy
    if returns.index[0] < benchmark_rets.index[0]:
        returns = returns[returns.index > benchmark_rets.index[0]]

    if not returns.index.difference(benchmark_rets.index).empty:
        # logger.info(f"Strategy has more indexes than benchmark - dropping ${returns.index.difference(benchmark_rets.index)}")
        returns = returns.loc[benchmark_rets.index.intersection(returns.index)]

    vertical_sections = 14

    if live_start_date is not None:
        vertical_sections += 1
        live_start_date = utils.get_utc_timestamp(live_start_date)

    if bootstrap:
        vertical_sections += 1

    widthInch = 14
    heightInch = vertical_sections * 5
    fig = plt.figure(figsize=(widthInch, heightInch))

    gs = gridspec.GridSpec(vertical_sections, 3, wspace=1, hspace=0.5)
    gs.update(left=0.1, right=0.9, top=0.965, bottom=0.03)

    perf_stats = show_perf_stats(returns, benchmark_rets,
                             positions=positions,
                             bootstrap=bootstrap,
                             live_start_date=live_start_date)

    plt.suptitle('%s returns tearsheet as of %s. Start date %s End date %s.'%(sravzid,
    datetime.datetime.now().strftime("%m/%d/%Y"),
    returns.index[0].strftime('%Y-%m-%d'),
    returns.index[-1].strftime('%Y-%m-%d')))
    i = 0
    ax_perf_stats = plt.subplot(gs[i, 1:])
    bbox = [0, 0, 1, 1]
    ax_perf_stats.axis('off')
    mpl_table = ax_perf_stats.table(
        cellText=perf_stats.values, rowLabels=perf_stats.index, bbox=bbox, colLabels=perf_stats.columns)
    mpl_table.auto_set_font_size(True)
    ax_perf_stats.set_title("Perfomance statistics")


    i += 1
    ax_drawdown_stats = plt.subplot(gs[i, :])
    drawdown_stats = timeseries.gen_drawdown_table(returns, top=5).round(3)
    ax_drawdown_stats.axis('off')
    mpl_table = ax_drawdown_stats.table(
        cellText=drawdown_stats.values, rowLabels=drawdown_stats.index, bbox=bbox, colLabels=drawdown_stats.columns)
    mpl_table.auto_set_font_size(True)
    ax_drawdown_stats.set_title("Worst Drawdown Statistics")

    # Create axis for plots
    ax_rolling_returns = plt.subplot(gs[2:4, :])
    i += 3
    ax_rolling_returns_vol_match = plt.subplot(gs[i, :],
                                               sharex=ax_rolling_returns)
    i += 1
    ax_rolling_returns_log = plt.subplot(gs[i, :],
                                         sharex=ax_rolling_returns)
    i += 1
    ax_returns = plt.subplot(gs[i, :],
                             sharex=ax_rolling_returns)
    i += 1
    ax_rolling_beta = plt.subplot(gs[i, :], sharex=ax_rolling_returns)
    i += 1
    ax_rolling_sharpe = plt.subplot(gs[i, :], sharex=ax_rolling_returns)
    i += 1
    ax_rolling_risk = plt.subplot(gs[i, :], sharex=ax_rolling_returns)
    i += 1
    ax_drawdown = plt.subplot(gs[i, :], sharex=ax_rolling_returns)
    i += 1
    ax_underwater = plt.subplot(gs[i, :], sharex=ax_rolling_returns)
    i += 1
    ax_monthly_heatmap = plt.subplot(gs[i, 0])
    ax_annual_returns = plt.subplot(gs[i, 1])
    ax_monthly_dist = plt.subplot(gs[i, 2])
    i += 1
    ax_return_quantiles = plt.subplot(gs[i, :])
    i += 1

    # Genereate plots
    plotting.plot_rolling_returns(
        returns,
        factor_returns=benchmark_rets,
        live_start_date=live_start_date,
        cone_std=cone_std,
        ax=ax_rolling_returns)
    ax_rolling_returns.set_title(
        'Cumulative returns')

    plotting.plot_rolling_returns(
        returns,
        factor_returns=benchmark_rets,
        live_start_date=live_start_date,
        cone_std=None,
        volatility_match=True,
        legend_loc=None,
        ax=ax_rolling_returns_vol_match)
    ax_rolling_returns_vol_match.set_title(
        'Cumulative returns volatility matched to benchmark')

    plotting.plot_rolling_returns(
        returns,
        factor_returns=benchmark_rets,
        logy=True,
        live_start_date=live_start_date,
        cone_std=cone_std,
        ax=ax_rolling_returns_log)
    ax_rolling_returns_log.set_title(
        'Cumulative returns on logarithmic scale')

    plotting.plot_returns(
        returns,
        live_start_date=live_start_date,
        ax=ax_returns,
    )
    ax_returns.set_title(
        'Returns')

    plotting.plot_rolling_beta(
        returns, benchmark_rets, ax=ax_rolling_beta)

    plotting.plot_rolling_sharpe(
        returns, ax=ax_rolling_sharpe)

    plotting.plot_rolling_volatility(
        returns, factor_returns=benchmark_rets, ax=ax_rolling_risk)

    # try:
    #     returns = returns.tz_localize('UTC', level=0)
    #     plotting.plot_rolling_fama_french(
    #         returns, ax=ax_rolling_risk)
    # except:
    #     logger.exception("Error plot_rolling_fama_french for {0}".format(sravzid))
    # finally:
    #     # Remove tzaware
    #     returns = returns.tz_localize(None)
    # # Drawdowns
    plotting.plot_drawdown_periods(
        returns, top=5, ax=ax_drawdown)

    plotting.plot_drawdown_underwater(
        returns=returns, ax=ax_underwater)

    plotting.show_worst_drawdown_periods(returns)

    #plotting.show_return_range(returns)

    plotting.plot_monthly_returns_heatmap(returns, ax=ax_monthly_heatmap)
    plotting.plot_annual_returns(returns, ax=ax_annual_returns)
    plotting.plot_monthly_returns_dist(returns, ax=ax_monthly_dist)

    plotting.plot_return_quantiles(
        returns,
        live_start_date=live_start_date,
        ax=ax_return_quantiles)

    if bootstrap:
        ax_bootstrap = plt.subplot(gs[i, :])
        plotting.plot_perf_stats(returns, benchmark_rets,
                                 ax=ax_bootstrap)

    for ax in fig.axes:
        plt.setp(ax.get_xticklabels(), visible=True)

    # plt.show()
    if return_fig:
        return fig

def timer(msg_body, previous_time):
    current_time = time()
    run_time = current_time - previous_time
    message = "\nFinished " + msg_body + " (required {:.2f} seconds)."
    print(message.format(run_time))

    return current_time

def create_bayesian_tear_sheet(returns, benchmark_rets=None,
                               live_start_date=None, samples=10,
                               return_fig=False, stoch_vol=False,
                               progressbar=True):
    """
    Generate a number of Bayesian distributions and a Bayesian
    cone plot of returns.
    Plots: Sharpe distribution, annual volatility distribution,
    annual alpha distribution, beta distribution, predicted 1 and 5
    day returns distributions, and a cumulative returns cone plot.
    Parameters
    ----------
    returns : pd.Series
        Daily returns of the strategy, noncumulative.
         - See full explanation in create_full_tear_sheet.
    benchmark_rets : pd.Series, optional
        Daily noncumulative returns of the benchmark.
         - This is in the same style as returns.
    live_start_date : datetime, optional
        The point in time when the strategy began live
        trading, after its backtest period.
    samples : int, optional
        Number of posterior samples to draw.
    return_fig : boolean, optional
        If True, returns the figure that was plotted on.
    stoch_vol : boolean, optional
        If True, run and plot the stochastic volatility model
    progressbar : boolean, optional
        If True, show a progress bar
    """

    if not have_bayesian:
        raise NotImplementedError(
            "Bayesian tear sheet requirements not found.\n"
            "Run 'pip install pyfolio[bayesian]' to install "
            "bayesian requirements."
        )

    if live_start_date is None:
        raise NotImplementedError(
            'Bayesian tear sheet requires setting of live_start_date'
        )

    live_start_date = utils.get_utc_timestamp(live_start_date)
    df_train = returns.loc[returns.index < live_start_date]
    df_test = returns.loc[returns.index >= live_start_date]

    # Run T model with missing data
    print("Running T model")
    previous_time = time()
    # track the total run time of the Bayesian tear sheet
    start_time = previous_time

    trace_t, ppc_t = bayesian.run_model('t', df_train,
                                        returns_test=df_test,
                                        samples=samples, ppc=True)
    previous_time = timer("T model", previous_time)

    # Compute BEST model
    print("\nRunning BEST model")
    trace_best = bayesian.run_model('best', df_train,
                                    returns_test=df_test,
                                    samples=samples)
    previous_time = timer("BEST model", previous_time)

    # Plot results

    fig = plt.figure(figsize=(14, 10 * 2))
    gs = gridspec.GridSpec(9, 2, wspace=0.3, hspace=0.3)

    axs = []
    row = 0

    # Plot Bayesian cone
    ax_cone = plt.subplot(gs[row, :])
    bayesian.plot_bayes_cone(df_train, df_test, ppc_t, ax=ax_cone)
    previous_time = timer("plotting Bayesian cone", previous_time)

    # Plot BEST results
    row += 1
    axs.append(plt.subplot(gs[row, 0]))
    axs.append(plt.subplot(gs[row, 1]))
    row += 1
    axs.append(plt.subplot(gs[row, 0]))
    axs.append(plt.subplot(gs[row, 1]))
    row += 1
    axs.append(plt.subplot(gs[row, 0]))
    axs.append(plt.subplot(gs[row, 1]))
    row += 1
    # Effect size across two
    axs.append(plt.subplot(gs[row, :]))

    bayesian.plot_best(trace=trace_best, axs=axs)
    previous_time = timer("plotting BEST results", previous_time)

    # Compute Bayesian predictions
    row += 1
    ax_ret_pred_day = plt.subplot(gs[row, 0])
    ax_ret_pred_week = plt.subplot(gs[row, 1])
    day_pred = ppc_t[:, 0]
    p5 = scipy.stats.scoreatpercentile(day_pred, 5)
    sns.distplot(day_pred,
                 ax=ax_ret_pred_day
                 )
    ax_ret_pred_day.axvline(p5, linestyle='--', linewidth=3.)
    ax_ret_pred_day.set_xlabel('Predicted returns 1 day')
    ax_ret_pred_day.set_ylabel('Frequency')
    ax_ret_pred_day.text(0.4, 0.9, 'Bayesian VaR = %.2f' % p5,
                         verticalalignment='bottom',
                         horizontalalignment='right',
                         transform=ax_ret_pred_day.transAxes)
    previous_time = timer("computing Bayesian predictions", previous_time)

    # Plot Bayesian VaRs
    week_pred = (
        np.cumprod(ppc_t[:, :5] + 1, 1) - 1)[:, -1]
    p5 = scipy.stats.scoreatpercentile(week_pred, 5)
    sns.distplot(week_pred,
                 ax=ax_ret_pred_week
                 )
    ax_ret_pred_week.axvline(p5, linestyle='--', linewidth=3.)
    ax_ret_pred_week.set_xlabel('Predicted cum returns 5 days')
    ax_ret_pred_week.set_ylabel('Frequency')
    ax_ret_pred_week.text(0.4, 0.9, 'Bayesian VaR = %.2f' % p5,
                          verticalalignment='bottom',
                          horizontalalignment='right',
                          transform=ax_ret_pred_week.transAxes)
    previous_time = timer("plotting Bayesian VaRs estimate", previous_time)

    # Run alpha beta model
    if benchmark_rets is not None:
        print("\nRunning alpha beta model")
        benchmark_rets = benchmark_rets.loc[df_train.index]
        trace_alpha_beta = bayesian.run_model('alpha_beta', df_train,
                                              bmark=benchmark_rets,
                                              samples=samples)
        previous_time = timer("running alpha beta model", previous_time)

        # Plot alpha and beta
        row += 1
        ax_alpha = plt.subplot(gs[row, 0])
        ax_beta = plt.subplot(gs[row, 1])
        sns.distplot((1 + trace_alpha_beta['alpha'][100:])**252 - 1,
                     ax=ax_alpha)
        sns.distplot(trace_alpha_beta['beta'][100:], ax=ax_beta)
        ax_alpha.set_xlabel('Annual Alpha')
        ax_alpha.set_ylabel('Belief')
        ax_beta.set_xlabel('Beta')
        ax_beta.set_ylabel('Belief')
        previous_time = timer("plotting alpha beta model", previous_time)

    if stoch_vol:
        # run stochastic volatility model
        returns_cutoff = 400
        print(
            "\nRunning stochastic volatility model on "
            "most recent {} days of returns.".format(returns_cutoff)
        )
        if df_train.size > returns_cutoff:
            df_train_truncated = df_train[-returns_cutoff:]
        _, trace_stoch_vol = bayesian.model_stoch_vol(df_train_truncated)
        previous_time = timer(
            "running stochastic volatility model", previous_time)

        # plot latent volatility
        row += 1
        ax_volatility = plt.subplot(gs[row, :])
        bayesian.plot_stoch_vol(
            df_train_truncated, trace=trace_stoch_vol, ax=ax_volatility)
        previous_time = timer(
            "plotting stochastic volatility model", previous_time)

    total_time = time() - start_time
    print("\nTotal runtime was {:.2f} seconds.".format(total_time))

    gs.tight_layout(fig)

    if return_fig:
        return fig


@plotting.customize
def create_portfolio_pca_report(sravzids, index=settings.constants.BENCHMARK_INDEX, return_fig=False):
    pcae = pca.engine()
    pqe = price_queries.engine()
    pe = portfolio.engine()
    vertical_sections = 8
    widthInch = 10 + len(sravzids) * 3
    heightInch = vertical_sections * 5 + + len(sravzids) * 3
    fig = plt.figure(figsize=(widthInch, heightInch))

    gs = gridspec.GridSpec(vertical_sections, 4, wspace=1, hspace=0.5)
    gs.update(left=0.1, right=0.9, top=0.965, bottom=0.03)


    i = 0
    try:
        portfolio_returns = pe.get_portfolio_daily_returns(
            None, None, portfolio_assets=sravzids)
        ax_portfolio_returns = plt.subplot(gs[i, :])
        portfolio_returns.plot(
            title='Portfolio daily returns', ax=ax_portfolio_returns)
    except Exception:
        logger.exception('Error plotting portfolio daily returns')

    i = 1
    try:
        cumulative_portfolio_returns = pe.get_portfolio_cummulative_returns(
            None, None, portfolio_assets=sravzids)
        ax_portfolio_cummulative_returns = plt.subplot(gs[i, :])
        cumulative_portfolio_returns.plot(
            title='Portfolio cummulative returns', ax=ax_portfolio_cummulative_returns)
    except Exception:
        logger.exception('Error plotting cumulative portfolio returns')

    i = 2
    try:
        ax_scatter_plot = plt.subplot(gs[i, :])

        data_df = pcae.get_percent_daily_returns(sravzids)
        data_df.plot(ax=ax_scatter_plot)
        ax_scatter_plot.set_title('Scatter plot of daily asset returns')
    except Exception:
        logger.exception('Error plotting scatter plot of daily asset returns')

    try:
        scatter_plot_df = pcae.get_scatter_plot_daily_return(sravzids)
        scatter_plot_df = scatter_plot_df.replace(
            [np.inf, -np.inf], np.nan).fillna(0)
        n_components = len(sravzids)
        _p = PCA(n_components=n_components)
        pca_dat = _p.fit(scatter_plot_df)
    except Exception:
        logger.exception('Error plotting scatter plot of daily asset returns')

    i = 3
    try:
        cumulative_portfolio_assets_returns = pe.get_portfolio_assets_cummulative_daily_returns(
            None, None, portfolio_assets=sravzids)
        ax_portfolio_assets_cummulative_returns = plt.subplot(gs[i, :])
        cumulative_portfolio_assets_returns.plot(
            title='Portfolio assets cummulative returns', ax=ax_portfolio_assets_cummulative_returns)
    except Exception:
        logger.exception('Error plotting portfolio assets cummulative returns')

    i = 4
    try:
        ax_first_pc_variance_explanation = plt.subplot(
            gs[i, :])
        ax_first_pc_variance_explanation.bar(
            range(n_components), pca_dat.explained_variance_ratio_)
        ax_first_pc_variance_explanation.set_title(
            'Variance explained by first {0} principal components'.format(n_components))
    except Exception:
        logger.exception('Error plotting Variance explained by first principal components')

    i = 5
    try:
        pc_vs_index_returns_pc1 = plt.subplot(gs[i, :2])
        pc_vs_index_returns_index = plt.subplot(gs[i, 2:])
        first_pc = pca_dat.components_[0]
        first_pc_normalized_to_1 = np.asmatrix(first_pc/sum(first_pc)).T
        first_pc_portfolio_return = scatter_plot_df.values*first_pc_normalized_to_1
        pc_ret = pd.DataFrame(
            data=first_pc_portfolio_return, index=scatter_plot_df.index)
        pc_ret_idx = pc_ret+1
        pc_ret_idx = pc_ret_idx.cumprod()
        pc_ret_idx.columns = ['pc1']
        index_column = settings.constants.BENCHMARK_INDEX_COLUMN
        index_retruns_df = pqe.get_historical_price_df(index)[
            [index_column]]
        pc_ret_vs_idx_returns = pc_ret_idx.join(index_retruns_df)
        pc_ret_vs_idx_returns['pc1'].plot(
            title='First PC returns', ax=pc_vs_index_returns_pc1)
        pc_ret_vs_idx_returns[index_column].plot(title='Index {0} {1} price returns'.format(
            index, index_column), ax=pc_vs_index_returns_index)
    except Exception:
        logger.exception('Error plotting PC returns vs index returns')

    i = 6
    try:
        ax_cov_matrix = plt.subplot(gs[i, 1:])
        cov_matrix = scatter_plot_df.cov().round(5)
        #ax2 = fig.add_subplot(122)
        bbox = [0, 0, 1, 1]
        ax_cov_matrix.axis('off')
        mpl_table = ax_cov_matrix.table(
            cellText=cov_matrix.values, rowLabels=cov_matrix.index, bbox=bbox, colLabels=cov_matrix.columns)
        mpl_table.auto_set_font_size(True)
        ax_cov_matrix.set_title("Covariance matrix last % change price")
    except Exception:
        logger.exception('Error plotting Covariance matrix last % change price')

    i = 7
    try:
        ax_corr_matrix = plt.subplot(gs[i, 1:])
        corr_matrix = scatter_plot_df.corr().round(5)
        #ax2 = fig.add_subplot(122)
        bbox = [0, 0, 1, 1]
        ax_corr_matrix.axis('off')
        mpl_table = ax_corr_matrix.table(
            cellText=corr_matrix.values, rowLabels=corr_matrix.index, bbox=bbox, colLabels=corr_matrix.columns)
        #mpl_table.set_xticklabels(corr_matrix.index, rotation=45)
        mpl_table.auto_set_font_size(True)
        ax_corr_matrix.set_title("Correlation matrix last % change price")
    except Exception:
        logger.exception('Error plotting Correlation matrix last % change price')

    if return_fig:
        return fig


def get_combined_charts(sravzids, return_fig=True):
    pqe = price_queries.engine()
    firstDf = None
    firstSravzID = None
    for sravzid in sravzids:
        sravz_generic_id = helper.get_generic_sravz_id(sravzid)
        price_df = pqe.get_historical_price_df(sravz_generic_id)
        column_names = {}
        [column_names.update({name: "%s%s" % (name, sravz_generic_id)})
         for name in price_df.columns]
        price_df = price_df.rename(index=str, columns=column_names)
        if not firstSravzID:
            firstDf = price_df
            firstSravzID = sravzid
            continue
        else:
            firstDf = firstDf.join(price_df)

    firstDf.index = pd.to_datetime(firstDf.index)

    vertical_sections = len(
        settings.constants.ChartsToDisplayAndAcceptedColumns) * 3
    widthInch = 10
    heightInch = vertical_sections * 3
    fig = plt.figure(figsize=(widthInch, heightInch))
    fig.suptitle("Combined chart for {0} as of {1}".format(str(sravzids), datetime.datetime.now(datetime.UTC)))
    gs = gridspec.GridSpec(vertical_sections, 4, wspace=1, hspace=0.5)
    gs.update(left=0.1, right=0.9, top=0.965, bottom=0.03)

    i = 0
    for key, value in settings.constants.ChartsToDisplayAndAcceptedColumns.items():
        # Plot Settle for Futures and Last for Stocks on the same plot
        df_to_plot = firstDf[[x for x in firstDf.columns if any([y for y in value if y in x.lower()])]]
        if not df_to_plot.empty:
            try:
                ax_plot = plt.subplot(gs[i, :])
                df_to_plot.plot(kind='line', ax=ax_plot)
                i = i+1
                ax_head_df = plt.subplot(gs[i, 1:])
                df_head = df_to_plot.tail()
                bbox = [0, 0, 1, 1]
                ax_head_df.axis('off')
                mpl_table = ax_head_df.table(
                    cellText=df_head.values, rowLabels=df_head.index, bbox=bbox, colLabels=df_head.columns)
                mpl_table.auto_set_font_size(True)
                ax_head_df.set_title("Latest values")
                i = i+1
                ax_tail_df = plt.subplot(gs[i, 1:])
                df_tail = df_to_plot.head()
                bbox = [0, 0, 1, 1]
                ax_tail_df.axis('off')
                mpl_table = ax_tail_df.table(
                    cellText=df_tail.values, rowLabels=df_tail.index, bbox=bbox, colLabels=df_tail.columns)
                mpl_table.auto_set_font_size(True)
                ax_tail_df.set_title("Earliest values")
                i = i+1
            except Exception:
                logger.exception('Error plotting data for columns {0}'.format([
                    x for x in firstDf.columns if key in x.lower()]))

    if return_fig:
        return fig

def plot_multi(data, ax, cols=None, spacing=.1, **kwargs):

    # Get default color style from pandas - can be changed to any other color list
    if cols is None: cols = data.columns
    if len(cols) == 0: return
    #colors = getattr(getattr(pd.plotting, '_matplotlib').style, '_get_standard_colors')(num_colors=len(cols))
    # colors = list(mcolors.CSS4_COLORS.values())
    colors = ['r', 'b', 'g', 'c', 'm', 'y', 'k']

    # First axis
    data.loc[:, cols[0]].plot(ax=ax, label=cols[0], color=colors[0], **kwargs)
    ax.set_ylabel(ylabel=cols[0])
    lines, labels = ax.get_legend_handles_labels()

    for n in range(1, len(cols)):
        # Multiple y-axes
        ax_new = ax.twinx()
        ax_new.set_yscale('log')
        ax_new.spines['right'].set_position(('axes', 1 + spacing * (n - 1)))
        data.loc[:, cols[n]].plot(ax=ax_new, label=cols[n], color=colors[n % len(colors)])
        ax_new.set_ylabel(ylabel=cols[n])

        # Proper legend position
        line, label = ax_new.get_legend_handles_labels()
        lines += line
        labels += label

    ax.legend(lines, labels, loc=0)
    # return ax

def get_rolling_stats(sravzid, return_fig=True):
    pqe = price_queries.engine()
    sravz_generic_id = helper.get_generic_sravz_id(sravzid)
    price_df = pqe.get_historical_price_df(sravz_generic_id)

    price_df.columns = map(str.lower, price_df.columns)

    col = helper.get_price_column_to_use_for_the_asset(sravzid, price_df)

    vertical_sections = 9
    widthInch = 10
    heightInch = vertical_sections * 5
    fig = plt.figure(figsize=(widthInch, heightInch))
    gs = gridspec.GridSpec(vertical_sections, 4, wspace=1, hspace=0.5)
    gs.update(left=0.1, right=0.9, top=0.965, bottom=0.03)
    chart_index = 0
    ax_price_plot = plt.subplot(gs[chart_index, :])
    price_df[col].plot(label=col, ax=ax_price_plot)
    ax_price_plot.set_title(
        '{0} {1} Price'.format(sravzid, col))
    ax_price_plot.legend()

###
    # ax_price_all_columns_plot = plt.subplot(gs[1, 1:-1])
    # ax_price_all_columns_plot.set_yscale('log')
    # # price_df.plot(ax=ax_price_all_columns_plot)
    # plot_multi(price_df, ax_price_all_columns_plot)
    # ax_price_all_columns_plot.set_title(
    #     '{0} Available Data'.format(sravzid))
    # ax_price_all_columns_plot.legend()
    chart_index = chart_index + 1
    ax_describe = plt.subplot(gs[chart_index, :])
    ax_describe.axis('off')
    describe_df = price_df.describe().round(3)
    bbox = [0, 0, 1, 1]
    mpl_table = ax_describe.table(
        cellText=describe_df.values, rowLabels=describe_df.index, bbox=bbox, colLabels=describe_df.columns)
    mpl_table.auto_set_font_size(True)
    ax_describe.set_title("{0} Summary Statistics".format(sravzid))
###

    chart_index = chart_index + 1
    ax_rolling_mean_plot = plt.subplot(gs[chart_index, :])
    #price_df[col].plot(label=col, ax=ax_rolling_mean_plot)
    price_df[col].rolling(7).mean().plot(
        label="7 days MA", ax=ax_rolling_mean_plot)
    price_df[col].rolling(21).mean().plot(
        label="21 days MA", ax=ax_rolling_mean_plot)
    price_df[col].rolling(255).mean().plot(
        label="255 days MA", ax=ax_rolling_mean_plot)
    ax_rolling_mean_plot.set_title(
        '{0} {1} Rolling Moving Average'.format(sravzid, col))
    ax_rolling_mean_plot.legend()

    chart_index = chart_index + 1
    ax_rolling_std_plot = plt.subplot(gs[chart_index, :])
    #price_df[col].plot(label=col, ax=ax_rolling_std_plot)
    price_df[col].rolling(7).std().plot(
        label="7 days Std", ax=ax_rolling_std_plot)
    price_df[col].rolling(21).std().plot(
        label="21 days Std", ax=ax_rolling_std_plot)
    price_df[col].rolling(255).std().plot(
        label="255 days Std", ax=ax_rolling_std_plot)
    ax_rolling_std_plot.set_title(
        '{0} {1} Rolling Moving Std'.format(sravzid, col))
    ax_rolling_std_plot.legend()

    chart_index = chart_index + 1
    ax_df = plt.subplot(gs[chart_index, 1:])
    series = price_df[col].dropna()
    dftest = adfuller(series, autolag='AIC')
    dfoutput = pd.Series(dftest[0:4], index=[
                         'Test Statistic', 'p-value', '#Lags Used', 'Number of Observations Used'])
    for key, value in list(dftest[4].items()):
        dfoutput['Critical Value (%s)' % key] = value
    bbox = [0, 0, 1, 1]
    ax_df.axis('off')
    df_test_df = dfoutput.to_frame()
    mpl_table = ax_df.table(
        cellText=df_test_df.values, rowLabels=df_test_df.index, bbox=bbox, colLabels=df_test_df.index)
    #mpl_table.set_xticklabels(corr_matrix.index, rotation=45)
    mpl_table.auto_set_font_size(True)
    ax_df.set_title("{0} {1} Price - Dickey Fuller Test - Complete History".format(sravzid, col))

    for years in [10,5,2,1]:
        chart_index = chart_index + 1
        ax_df = plt.subplot(gs[chart_index, 1:])
        series = price_df[col].last(f"{years}Y").dropna()
        dftest = adfuller(series, regression='ctt', autolag='AIC')
        dfoutput = pd.Series(dftest[0:4], index=[
                            'Test Statistic', 'p-value', '#Lags Used', 'Number of Observations Used'])
        for key, value in list(dftest[4].items()):
            dfoutput['Critical Value (%s)' % key] = value
        font_size = 14
        bbox = [0, 0, 1, 1]
        ax_df.axis('off')
        df_test_df = dfoutput.to_frame()
        mpl_table = ax_df.table(
            cellText=df_test_df.values, rowLabels=df_test_df.index, bbox=bbox, colLabels=df_test_df.index)
        mpl_table.auto_set_font_size(False)
        mpl_table.set_fontsize(font_size)
        ax_df.set_title("{0} {1} Price - Augmented Dickey Fuller Test - Last {2}Yrs".format(sravzid, col, years), loc="left")

    if return_fig:
        return fig


def create_portfolio_correlation_report(portofolio_assets_daily_returns,
                                        portofolio_daily_returns,
                                        return_fig = False):
    vertical_sections = 5
    no_of_assets = len(portofolio_assets_daily_returns.columns)
    widthInch = 10 + no_of_assets * 3
    heightInch = vertical_sections * 5 + no_of_assets * 3
    fig = plt.figure(figsize=(widthInch, heightInch))

    gs = gridspec.GridSpec(vertical_sections, 4, wspace=1, hspace=0.5)
    gs.update(left=0.1, right=0.9, top=0.965, bottom=0.03)

    i = 0
    ax_cov_matrix = plt.subplot(gs[i, 1:])
    cov_matrix = portofolio_assets_daily_returns.cov().round(5)
    #ax2 = fig.add_subplot(122)
    bbox = [0, 0, 1, 1]
    ax_cov_matrix.axis('off')
    mpl_table = ax_cov_matrix.table(
        cellText=cov_matrix.values, rowLabels=cov_matrix.index, bbox=bbox, colLabels=cov_matrix.columns)
    mpl_table.auto_set_font_size(True)
    ax_cov_matrix.set_title("Covariance matrix last % daily returns")

    i = 1
    ax_corr_matrix = plt.subplot(gs[i, 1:])
    corr_matrix = portofolio_assets_daily_returns.corr().round(5)
    #ax2 = fig.add_subplot(122)
    bbox = [0, 0, 1, 1]
    ax_corr_matrix.axis('off')
    mpl_table = ax_corr_matrix.table(
        cellText=corr_matrix.values, rowLabels=corr_matrix.index, bbox=bbox, colLabels=corr_matrix.columns)
    #mpl_table.set_xticklabels(corr_matrix.index, rotation=45)
    mpl_table.auto_set_font_size(True)
    ax_corr_matrix.set_title("Correlation matrix last % daily returns")

    i = 2
    ax_corr_heat_map = plt.subplot(gs[i:4, :])
    ax_corr_heat_map.set_title("Correlation matrix heatmap last % daily returns")
    ax = sns.heatmap(
        corr_matrix,
        ax = ax_corr_heat_map,
        vmin=-1, vmax=1, center=0,
        cmap=sns.diverging_palette(20, 220, n=200),
        square=True
    )
    ax.set_xticklabels(
        ax.get_xticklabels(),
        rotation=45,
        horizontalalignment='right'
    )

    i = 4
    ax_expected_returns_vs_risk = plt.subplot(gs[i, :])
    ax_expected_returns_vs_risk.set_title("Expected Returns Vs Risk last % daily returns")
    ax_expected_returns_vs_risk.scatter(portofolio_assets_daily_returns.mean(),
                portofolio_assets_daily_returns.std())
    ax_expected_returns_vs_risk.set_xlabel('Expected returns')
    ax_expected_returns_vs_risk.set_ylabel('Risk')
    for label, x, y in zip(portofolio_assets_daily_returns.columns,
                           portofolio_assets_daily_returns.mean(),
                           portofolio_assets_daily_returns.std()):
        ax_expected_returns_vs_risk.annotate(
            label,
            xy = (x, y), xytext = (20, -20),
            textcoords = 'offset points', ha = 'right', va = 'bottom',
            bbox = dict(boxstyle = 'round,pad=0.5', fc = 'yellow', alpha = 0.5),
            arrowprops = dict(arrowstyle = '->', connectionstyle = 'arc3,rad=0'))

    if return_fig:
        return fig

def create_portfolio_correlation_matrix_report(portofolio_assets_daily_returns,
                                        return_fig = False):
    vertical_sections = 1
    no_of_assets = len(portofolio_assets_daily_returns.columns)
    widthInch = 10 + no_of_assets * 3
    heightInch = vertical_sections * 5 + no_of_assets * 3
    fig = plt.figure(figsize=(widthInch, heightInch))

    gs = gridspec.GridSpec(vertical_sections, 4, wspace=1, hspace=0.5)
    gs.update(left=0.1, right=0.9, top=0.965, bottom=0.03)

    i = 0
    ax_scatter_matrix = plt.subplot(gs[i, :])
    pd.plotting.scatter_matrix(portofolio_assets_daily_returns, diagonal='kde', ax = ax_scatter_matrix)

    if return_fig:
        return fig