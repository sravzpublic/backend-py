'''
Created on Jan 20, 2017

@author: admin
'''
import datetime, os, platform
import pandas as pd
import matplotlib as mpl
if platform.system() not in ['Windows', 'Darwin']:
    print('matplotlib: no display found. Using non-interactive Agg backend')
    mpl.use('Agg')
import matplotlib.pyplot as plt
from . import helper

class util(object):
    '''
    Helper methods
    '''
    def __init__(self, params):
        '''

        '''
    @staticmethod
    def plot_df(df):
        '''
            Returns plot of the data frame
        '''
        return df.plot()

    @staticmethod
    def save_df_plot(plot, fileName):
        '''
            Saves the plot to cache directory
        '''
        fig = plot.get_figure()
        fig.savefig(helper.util.get_tempfile_path(fileName))
