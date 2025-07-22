from src.util import helper, settings, logger
from src.services.etfs import index_components
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import datetime
import os
import matplotlib
import uuid
import numpy as np
from src.services import price_queries
if os.environ.get('DISPLAY', '') == '':
    print('no display found. Using non-interactive Agg backend')
    matplotlib.use('Agg')

LOGGER = logger.RotatingLogger(__name__).getLogger()


def get_crypto_tears(sravzids):
    pqe = price_queries.engine()
    firstDf = None
    firstSravzID = None
    sravzids = sravzids or ['crypto_btc_usd', 'crypto_eth_usd']
    sravzids = sravzids + ["%s_hash_rate"%(id) for id in sravzids]
    price_col_to_use = 'Last'
    for sravzid in sravzids:
        sravz_generic_id = helper.get_generic_sravz_id(sravzid)
        if "_hash_rate" in sravzid:
            price_df = pqe.get_historical_hash_rate_df(sravz_generic_id)
        else:
            price_df = pqe.get_historical_price_df(sravz_generic_id)
            price_df = price_df.loc[:, [price_col_to_use]]
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
    firstDf = firstDf.ffill()

    vertical_sections = 2
    widthInch = 10
    heightInch = vertical_sections * 6

    fig = plt.figure(figsize=(widthInch, heightInch))
    plt.title('BTH and ETH analysis as of %s'%(datetime.datetime.now().strftime("%m/%d/%Y")))
    gs = gridspec.GridSpec(vertical_sections, 4, wspace=1, hspace=0.5)
    gs.update(left=0.1, right=0.9, top=0.965, bottom=0.03)

    i = 0
    ax_plot = plt.subplot(gs[i, :])
    ax_plot.set_title("Last price vs Date")
    firstDf[[col for col in firstDf.columns if 'Last' in col]].plot(kind='line', ax=ax_plot)

    i = 1
    ax_plot = plt.subplot(gs[i, :])
    ax_plot.set_yscale('log')
    ax_plot.set_title("Log Scale: Hash Rate (GH/sec) vs Date")
    firstDf[[col for col in firstDf.columns if '_hash_rate' in col]].plot(kind='line', ax=ax_plot)


    plt.tight_layout()
    return fig
