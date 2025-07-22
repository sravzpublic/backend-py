'''
Tensor Flow tear sheets
'''
import os
import matplotlib
if os.environ.get('DISPLAY', '') == '':
    print('no display found. Using non-interactive Agg backend')
    matplotlib.use('Agg')
from src.util import helper, settings, logger
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import pandas as pd
from src.services import price_queries

LOGGER = logger.RotatingLogger(__name__).getLogger()

import pandas as pd
import numpy as np
from . import stocker

from . import stocker
import os
import matplotlib
if os.environ.get('DISPLAY', '') == '':
    print('no display found. Using non-interactive Agg backend')
    matplotlib.use('Agg')
from src.util import helper, settings, logger
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import pandas as pd

LOGGER = logger.RotatingLogger(__name__).getLogger()


def create_tf_tear_sheet():
    """
    Generate stocker tear sheet.

    """

    _stocker = stocker.Stocker('fut_gold', asset_name = 'fut_gold', returns_df = None, number_of_years_back = 10)
    # socker df has ('Date', 'ds', 'y') columns
    vertical_sections = 1
    widthInch = 14
    heightInch = vertical_sections * 8
    fig = plt.figure(figsize=(widthInch, heightInch))

    i = 0
    gs = gridspec.GridSpec(vertical_sections, 3, wspace=1, hspace=0.5)
    gs.update(left=0.1, right=0.9, top=0.965, bottom=0.03)

    # ax = plt.subplot(gs[i, :])
    # try:
    #     model, model_data = tickerAnalysis.create_prophet_model(days=90, ax = ax)
    # except Exception:
    #     LOGGER.exception("Error plotting TF tear sheet")

    # return fig
    print(_stocker.stock)



class TFTears:
    def __init__(self):
        self.pqe = price_queries.engine()
        self.file = pd.read_csv(file)
        self.train = train
        self.i = int(self.train * len(self.file))
        self.stock_train = self.file[0: self.i]
        self.stock_test = self.file[self.i:]
        self.input_train = []
        self.output_train = []
        self.input_test = []
        self.output_test = []

    def gen_train(self, seq_len):
        """
        Generates training data
        :param seq_len: length of window
        :return: X_train and Y_train
        """
        for i in range((len(self.stock_train)//seq_len)*seq_len - seq_len - 1):
            x = np.array(self.stock_train.iloc[i: i + seq_len, 1])
            y = np.array([self.stock_train.iloc[i + seq_len + 1, 1]], np.float64)
            self.input_train.append(x)
            self.output_train.append(y)
        self.X_train = np.array(self.input_train)
        self.Y_train = np.array(self.output_train)

    def gen_test(self, seq_len):
        """
        Generates test data
        :param seq_len: Length of window
        :return: X_test and Y_test
        """
        for i in range((len(self.stock_test)//seq_len)*seq_len - seq_len - 1):
            x = np.array(self.stock_test.iloc[i: i + seq_len, 1])
            y = np.array([self.stock_test.iloc[i + seq_len + 1, 1]], np.float64)
            self.input_test.append(x)
            self.output_test.append(y)
        self.X_test = np.array(self.input_test)
        self.Y_test = np.array(self.output_test)

