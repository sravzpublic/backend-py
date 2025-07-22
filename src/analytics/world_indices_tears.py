from src.util import helper, settings, logger
from src.services.etfs import index_components
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import datetime
import os
import matplotlib
import uuid
import numpy as np
if os.environ.get('DISPLAY', '') == '':
    print('no display found. Using non-interactive Agg backend')
    matplotlib.use('Agg')

LOGGER = logger.RotatingLogger(__name__).getLogger()


def get_index_components_by_sector(sravzid, return_fig=True):
    index_componentse = index_components.engine()
    vertical_sections = 1
    widthInch = 10
    heightInch = vertical_sections * 5
    fig = plt.figure(figsize=(widthInch, heightInch))
    gs = gridspec.GridSpec(vertical_sections, 4, wspace=1, hspace=0.5)
    gs.update(left=0.1, right=0.9, top=0.965, bottom=0.03)
    components = index_componentse.get_eod_index_components_grouped_by_sector_df(sravzid)
    objects = components['Code'].index
    y_pos = np.arange(len(objects))
    performance = components['Code'].values
    plt.barh(y_pos, performance, align='center', alpha=0.5)
    plt.yticks(y_pos, objects)
    plt.xlabel('No of Components')
    plt.title('%s Components by Sector as of %s'%(sravzid, datetime.datetime.now().strftime("%m/%d/%Y")))
    # create a list to collect the plt.patches data
    totals = []
    ax = plt.gca()
    # find the values and append to list
    for i in ax.patches:
        totals.append(i.get_width())

    # set individual bar lables using above list
    total = sum(totals)

    # set individual bar lables using above list
    for i in ax.patches:
        # get_width pulls left or right; get_y pushes up or down
        ax.text(i.get_width()+.3, i.get_y()+.38, \
                str(round((i.get_width()/total)*100, 2))+'%', fontsize=10, color='dimgrey')

    # invert for largest on top
    ax.invert_yaxis()

    plt.tight_layout()
    if return_fig:
        return fig
