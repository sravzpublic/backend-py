'''
    Performs spread analysis
'''
from src.analytics import pca, timeseries
import pandas as pd
import numpy as np
from src.util import helper, aws_cache, logger, settings
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from statsmodels.tsa.stattools import acf, pacf
import statsmodels.api as sm
from datetime import datetime
import seaborn as sns


LOGGER = logger.RotatingLogger(__name__).getLogger()

@aws_cache.save_file_to_s3
@helper.save_plot_to_file
def perform_spread_analysis_for_assets(left_asset, right_asset, upload_to_aws=False, device=settings.constants.DEVICE_TYPE_PC):
    e = pca.engine()
    te = timeseries.engine()
    df_left = e.get_price_data_dfs([left_asset])
    df_right = e.get_price_data_dfs([right_asset])
    df = df_left.join(df_right, how='inner', lsuffix=left_asset, rsuffix=right_asset)
    df['spread'] = df[f'AdjustedClose{left_asset}'] - df[f'AdjustedClose{right_asset}']
    df_price = df[[f'AdjustedClose{left_asset}', f'AdjustedClose{right_asset}', 'spread']]

    vertical_sections = 7
    widthInch = 10
    heightInch = vertical_sections * 5
    fig = plt.figure(figsize=(widthInch, heightInch))
    fig.suptitle(f'{left_asset} vs {right_asset} - {datetime.now().strftime("%m/%d/%Y %H:%M:%S")}')
    gs = gridspec.GridSpec(vertical_sections, 4, wspace=1, hspace=0.5)
    gs.update(left=0.1, right=0.9, top=0.965, bottom=0.03)
    chart_index = 0
    ax_price_plot = plt.subplot(gs[chart_index, :])
    df_price.plot(ax=ax_price_plot)
    ax_price_plot.set_title(f'{left_asset} vs {right_asset} spread')
    ax_price_plot.legend()

    sravzid = f'{left_asset}-vs-{right_asset}-price'
    col = 'spread'

    chart_index = chart_index + 1
    ax_df_spread = plt.subplot(gs[chart_index, :])
    df_price['spread'].plot(ax=ax_df_spread)
    ax_df_spread.set_title("{0} {1} Spread Vs Date".format(sravzid, col))

    chart_index = chart_index + 1
    ax_rolling_mean_plot = plt.subplot(gs[chart_index, :])
    #price_df[col].plot(label=col, ax=ax_rolling_mean_plot)
    df_price[col].rolling(7).mean().plot(
        label="7 days MA", ax=ax_rolling_mean_plot)
    df_price[col].rolling(21).mean().plot(
        label="21 days MA", ax=ax_rolling_mean_plot)
    df_price[col].rolling(255).mean().plot(
        label="255 days MA", ax=ax_rolling_mean_plot)
    ax_rolling_mean_plot.set_title(
        '{0} {1} Rolling Moving Average'.format(sravzid, col))
    ax_rolling_mean_plot.legend()

    chart_index = chart_index + 1
    ax_rolling_std_plot = plt.subplot(gs[chart_index, :])
    #price_df[col].plot(label=col, ax=ax_rolling_std_plot)
    df_price[col].rolling(7).std().plot(
        label="7 days Std", ax=ax_rolling_std_plot)
    df_price[col].rolling(21).std().plot(
        label="21 days Std", ax=ax_rolling_std_plot)
    df_price[col].rolling(255).std().plot(
        label="255 days Std", ax=ax_rolling_std_plot)
    ax_rolling_std_plot.set_title(
        '{0} {1} Rolling Moving Std'.format(sravzid, col))
    ax_rolling_std_plot.legend()

    chart_index = chart_index + 1
    ax_head_df = plt.subplot(gs[chart_index, 1:])
    df_tail = df_price.tail().round(3)
    bbox = [0, 0, 1, 1]
    ax_head_df.axis('off')
    mpl_table = ax_head_df.table(
        cellText=df_tail.values, rowLabels=df_tail.index, bbox=bbox, colLabels=df_tail.columns)
    mpl_table.auto_set_font_size(True)
    ax_head_df.set_title("Latest Spread Values")

    chart_index = chart_index + 1
    ax_describe = plt.subplot(gs[chart_index, :])
    ax_describe.axis('off')
    describe_df = df_price.describe().round(3)
    bbox = [0, 0, 1, 1]
    mpl_table = ax_describe.table(
        cellText=describe_df.values, rowLabels=describe_df.index, bbox=bbox, colLabels=describe_df.columns)
    mpl_table.auto_set_font_size(True)
    ax_describe.set_title("Spread Summary Statistics")

    chart_index = chart_index + 1
    ax_describe = plt.subplot(gs[chart_index, :])
    limits = [x for x in [describe_df['spread']['min'], describe_df['spread']['mean'], describe_df['spread']['max']]]
    data_to_plot = ("Spread", df_tail['spread'][-1])
    palette = sns.color_palette("Blues_r", len(limits))
    ax_describe.set_aspect('equal')
    ax_describe.set_yticks([1])
    ax_describe.set_yticklabels([data_to_plot[0]])
    prev_limit = 0
    for idx, lim in enumerate(limits):
        ax_describe.barh([1], lim-prev_limit, left=prev_limit, height=15, color=palette[idx])
        prev_limit = lim
    ax_describe.barh([1], data_to_plot[1], color='black', height=5)
    ax_describe.set_title("Spread - Current vs Min/Mean/Max")

    plt.tight_layout()
    return fig


@helper.save_file_to_contabo
@helper.empty_cache
def perform_spread_analysis(upload_to_s3 = True):
    e = pca.engine()
    te = timeseries.engine()

    left_asset = 'idx_us_us10y'
    right_asset = 'idx_us_us5y'
    df_left = e.get_price_data_dfs([left_asset])
    df_right = e.get_price_data_dfs([right_asset])
    df = df_left.join(df_right, how='inner', lsuffix=left_asset, rsuffix=right_asset)
    df['spread'] = df[f'AdjustedClose{left_asset}'] - df[f'AdjustedClose{right_asset}']
    df_price = df[[f'AdjustedClose{left_asset}', f'AdjustedClose{right_asset}', 'spread']]


    left_asset = 'fut_us_ty'
    right_asset = 'fut_us_fvz0'
    df_left = e.get_price_data_dfs([left_asset])
    df_right = e.get_price_data_dfs([right_asset])
    df = df_left.join(df_right, how='inner', lsuffix=left_asset, rsuffix=right_asset)
    df['difference'] = df[f'AdjustedClose{left_asset}'] - df[f'AdjustedClose{right_asset}']
    df_spread = df[[f'AdjustedClose{left_asset}', f'AdjustedClose{right_asset}', 'difference']]

    vertical_sections = 20
    widthInch = 10
    heightInch = vertical_sections * 5
    fig = plt.figure(figsize=(widthInch, heightInch))
    fig.suptitle(f'10yr vs 5yr US Treasury Analysis - {datetime.now().strftime("%m/%d/%Y %H:%M:%S")}')
    gs = gridspec.GridSpec(vertical_sections, 4, wspace=1, hspace=0.5)
    gs.update(left=0.1, right=0.9, top=0.965, bottom=0.03)
    chart_index = 0
    ax_price_plot = plt.subplot(gs[chart_index, :])
    df_price.plot(ax=ax_price_plot)
    ax_price_plot.set_title('US Treasure 10 yr vs 5 yr spread')
    ax_price_plot.legend()

    sravzid = '10yr-vs-5y-price'
    col = 'spread'

    chart_index = chart_index + 1
    ax_df_spread = plt.subplot(gs[chart_index, :])
    df_price['spread'].plot(ax=ax_df_spread)
    ax_df_spread.set_title("{0} {1} Spread Vs Date".format(sravzid, col))

    chart_index = chart_index + 1
    ax_rolling_mean_plot = plt.subplot(gs[chart_index, :])
    #price_df[col].plot(label=col, ax=ax_rolling_mean_plot)
    df_price[col].rolling(7).mean().plot(
        label="7 days MA", ax=ax_rolling_mean_plot)
    df_price[col].rolling(21).mean().plot(
        label="21 days MA", ax=ax_rolling_mean_plot)
    df_price[col].rolling(255).mean().plot(
        label="255 days MA", ax=ax_rolling_mean_plot)
    ax_rolling_mean_plot.set_title(
        '{0} {1} Rolling Moving Average'.format(sravzid, col))
    ax_rolling_mean_plot.legend()

    chart_index = chart_index + 1
    ax_rolling_std_plot = plt.subplot(gs[chart_index, :])
    #price_df[col].plot(label=col, ax=ax_rolling_std_plot)
    df_price[col].rolling(7).std().plot(
        label="7 days Std", ax=ax_rolling_std_plot)
    df_price[col].rolling(21).std().plot(
        label="21 days Std", ax=ax_rolling_std_plot)
    df_price[col].rolling(255).std().plot(
        label="255 days Std", ax=ax_rolling_std_plot)
    ax_rolling_std_plot.set_title(
        '{0} {1} Rolling Moving Std'.format(sravzid, col))
    ax_rolling_std_plot.legend()

    chart_index = chart_index + 1
    ax_head_df = plt.subplot(gs[chart_index, 1:])
    df_tail = df_price.tail().round(3)
    bbox = [0, 0, 1, 1]
    ax_head_df.axis('off')
    mpl_table = ax_head_df.table(
        cellText=df_tail.values, rowLabels=df_tail.index, bbox=bbox, colLabels=df_tail.columns)
    mpl_table.auto_set_font_size(True)
    ax_head_df.set_title("Latest Spread Values")

    chart_index = chart_index + 1
    ax_describe = plt.subplot(gs[chart_index, :])
    ax_describe.axis('off')
    describe_df = df_price.describe().round(3)
    bbox = [0, 0, 1, 1]
    mpl_table = ax_describe.table(
        cellText=describe_df.values, rowLabels=describe_df.index, bbox=bbox, colLabels=describe_df.columns)
    mpl_table.auto_set_font_size(True)
    ax_describe.set_title("Spread Summary Statistics")

    chart_index = chart_index + 1
    ax_describe = plt.subplot(gs[chart_index, :])
    limits = [x*100 for x in [describe_df['spread']['min'], describe_df['spread']['mean'], describe_df['spread']['max']]]
    data_to_plot = ("Spread", df_tail['spread'][-1]*100)
    palette = sns.color_palette("Blues_r", len(limits))
    ax_describe.set_aspect('equal')
    ax_describe.set_yticks([1])
    ax_describe.set_yticklabels([data_to_plot[0]])
    prev_limit = 0
    for idx, lim in enumerate(limits):
        ax_describe.barh([1], lim-prev_limit, left=prev_limit, height=15, color=palette[idx])
        prev_limit = lim
    ax_describe.barh([1], data_to_plot[1], color='black', height=5)
    ax_describe.set_title("Spread - Current vs Min/Mean/Max (times 100)")

    chart_index = chart_index + 1
    ax_spread_plot = plt.subplot(gs[chart_index, :])
    df_spread.plot(ax=ax_spread_plot)
    ax_spread_plot.set_title('US Treasure 10 yr vs 5 yr price difference')
    ax_spread_plot.legend()

    chart_index = chart_index + 1
    ax_head_df = plt.subplot(gs[chart_index, 1:])
    df_tail = df_spread.tail().round(3)
    bbox = [0, 0, 1, 1]
    ax_head_df.axis('off')
    mpl_table = ax_head_df.table(
        cellText=df_tail.values, rowLabels=df_tail.index, bbox=bbox, colLabels=df_tail.columns)
    mpl_table.auto_set_font_size(True)
    ax_head_df.set_title("Latest Price Difference Values")

    chart_index = chart_index + 1
    ax_describe = plt.subplot(gs[chart_index, :])
    ax_describe.axis('off')
    describe_df = df_spread.describe().round(3)
    bbox = [0, 0, 1, 1]
    mpl_table = ax_describe.table(
        cellText=describe_df.values, rowLabels=describe_df.index, bbox=bbox, colLabels=describe_df.columns)
    mpl_table.auto_set_font_size(True)
    ax_describe.set_title("Price Difference Summary Statistics")

    chart_index = chart_index + 1
    ax_describe = plt.subplot(gs[chart_index, :])
    limits = [describe_df['difference']['min'], describe_df['difference']['mean'], describe_df['difference']['max']]
    data_to_plot = ("Price Difference", df_tail['difference'][-1])
    palette = sns.color_palette("Blues_r", len(limits))
    ax_describe.set_aspect('equal')
    ax_describe.set_yticks([1])
    ax_describe.set_yticklabels([data_to_plot[0]])
    prev_limit = 0
    for idx, lim in enumerate(limits):
        ax_describe.barh([1], lim-prev_limit, left=prev_limit, height=15, color=palette[idx])
        prev_limit = lim
    ax_describe.barh([1], data_to_plot[1], color='black', height=5)
    ax_describe.set_title("Price Difference - Current Vs Min/Mean/Max")

    col = 'difference'
    chart_index = chart_index + 1
    ax_rolling_mean_plot = plt.subplot(gs[chart_index, :])
    #price_df[col].plot(label=col, ax=ax_rolling_mean_plot)
    df_spread[col].rolling(7).mean().plot(
        label="7 days MA", ax=ax_rolling_mean_plot)
    df_spread[col].rolling(21).mean().plot(
        label="21 days MA", ax=ax_rolling_mean_plot)
    df_spread[col].rolling(255).mean().plot(
        label="255 days MA", ax=ax_rolling_mean_plot)
    ax_rolling_mean_plot.set_title(
        '{0} {1} Rolling Moving Average'.format(sravzid, col))
    ax_rolling_mean_plot.legend()

    chart_index = chart_index + 1
    ax_rolling_std_plot = plt.subplot(gs[chart_index, :])
    #price_df[col].plot(label=col, ax=ax_rolling_std_plot)
    df_spread[col].rolling(7).std().plot(
        label="7 days Std", ax=ax_rolling_std_plot)
    df_spread[col].rolling(21).std().plot(
        label="21 days Std", ax=ax_rolling_std_plot)
    df_spread[col].rolling(255).std().plot(
        label="255 days Std", ax=ax_rolling_std_plot)
    ax_rolling_std_plot.set_title(
        '{0} {1} Rolling Moving Std'.format(sravzid, col))
    ax_rolling_std_plot.legend()

    chart_index = chart_index + 1
    ax_df_spread = plt.subplot(gs[chart_index, :])
    df_spread[col].plot(ax=ax_df_spread)
    ax_df_spread.set_title("{0} {1} Difference Vs Date".format(sravzid, col))

    chart_index = chart_index + 1
    ax_first_difference = plt.subplot(gs[chart_index, :])
    df_spread['First Difference'] = df_spread[col] - df_spread[col].shift()
    df_spread['First Difference'].plot(ax=ax_first_difference)
    ax_first_difference.set_title(
        "{0} {1} Price First Difference Vs Date".format(sravzid, col))

    chart_index = chart_index + 1
    ax_natural_log = plt.subplot(gs[chart_index, :])
    df_spread['Natural Log'] = df_spread[col].apply(lambda x: np.log(x))
    df_spread['Natural Log'].plot(ax=ax_natural_log)
    ax_natural_log.set_title(
        "{0} {1} Price Natual Log Vs Date".format(sravzid, col))

    ax_original_variance = plt.subplot(gs[chart_index, :2])
    ax_natual_log_variance = plt.subplot(gs[chart_index, 2:])
    df_spread['Original Variance'] = df_spread[col].rolling(30, min_periods=None, center=True).var()
    df_spread['Log Variance'] = df_spread['Natural Log'].rolling(30, min_periods=None, center=True).var()
    df_spread['Original Variance'].plot(ax=ax_original_variance,
                                        title="{0} {1} Price Original Variance Vs Date".format(sravzid, col))
    df_spread['Log Variance'].plot(ax=ax_natual_log_variance,
                                    title="{0} {1} Price Log Variance Vs Date".format(sravzid, col))

    chart_index = chart_index + 1
    ax_logged_first_difference = plt.subplot(gs[chart_index, :])
    df_spread['Logged First Difference'] = df_spread['Natural Log'] - \
        df_spread['Natural Log'].shift()
    df_spread['Logged First Difference'].plot(ax=ax_logged_first_difference,
                                                title="{0} {1} Price Logged First Difference Vs Date".format(sravzid, col))

    chart_index = chart_index + 1
    ax_lag_correlation = plt.subplot(gs[chart_index, :])
    lag_correlations = acf(df_spread['Logged First Difference'].iloc[1:])
    ax_lag_correlation.plot(lag_correlations, marker='o', linestyle='--')
    ax_lag_correlation.set_title(
        "{0} {1} Price Logged First Difference Auto correlation Vs Lag Step".format(sravzid, col))

    chart_index = chart_index + 1
    ax_lag_partial_auto_correlation = plt.subplot(gs[chart_index, :])
    lag_partial_correlations = pacf(
        df_spread['Logged First Difference'].iloc[1:])
    ax_lag_partial_auto_correlation.plot(
        lag_partial_correlations, marker='o', linestyle='--')
    ax_lag_partial_auto_correlation.set_title(
        "{0} {1} Price Logged First Difference Partial Auto correlation Vs Lag Step".format(sravzid, col))


    if upload_to_s3:
        return fig, f'{settings.constants.CONTABO_BUCKET_PREFIX}/assets/10yr-vs-5yr-us-treasury-analysis.jpg'
    helper.save_plt(fig)
    return None, None



if __name__ == '__main__':
    # perform_spread_analysis_for_assets('fut_us_gc', 'idx_us_gspc')
    perform_spread_analysis()
    # print(get_seed_ticker())

