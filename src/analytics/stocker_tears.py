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
import os, sys
current_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_path)
import stocker
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

CHART_TYPE_CREATE_PROPHET_MODEL = 'CHART_TYPE_CREATE_PROPHET_MODEL'
CHART_TYPE_EVALUATE_PREDICTION = 'CHART_TYPE_EVALUATE_PREDICTION'
CHART_TYPE_CHANGE_POINT_PRIOR_ANALYSIS = 'CHART_TYPE_CHANGE_POINT_PRIOR_ANALYSIS'
CHART_TYPE_CHANGE_POINT_PRIOR_VALIDATION = 'CHART_TYPE_CHANGE_POINT_PRIOR_VALIDATION'
CHART_TYPE_EVALUATE_PREDICTION_WITH_CHANGE_POINT = 'CHART_TYPE_EVALUATE_PREDICTION_WITH_CHANGE_POINT'
CHART_TYPE_PREDICT_FUTURE = 'CHART_TYPE_PREDICT_FUTURE'

def create_stocker_tear_sheet(sravz_id, chart_type, asset_name = None, returns_df = None, number_of_years_back = 10):
    """
    Generate stocker tear sheet.

    """

    tickerAnalysis = stocker.Stocker(sravz_id, asset_name = asset_name, returns_df = returns_df, number_of_years_back = number_of_years_back)
    if chart_type == CHART_TYPE_CHANGE_POINT_PRIOR_VALIDATION:
        vertical_sections = 3
    elif chart_type in [CHART_TYPE_EVALUATE_PREDICTION_WITH_CHANGE_POINT, CHART_TYPE_EVALUATE_PREDICTION]:
        vertical_sections = 2
    else:
        vertical_sections = 1
    widthInch = 14
    heightInch = vertical_sections * 8
    fig = plt.figure(figsize=(widthInch, heightInch))

    i = 0
    gs = gridspec.GridSpec(vertical_sections, 3, wspace=1, hspace=0.5)
    gs.update(left=0.1, right=0.9, top=0.965, bottom=0.03)

    ax = plt.subplot(gs[i, :])
    if chart_type == CHART_TYPE_CREATE_PROPHET_MODEL:
        try:
            model, model_data = tickerAnalysis.create_prophet_model(days=90, ax = ax)
        except Exception:
            LOGGER.exception("Error plotting create_prophet_model")

    if chart_type == CHART_TYPE_EVALUATE_PREDICTION:
        details = tickerAnalysis.evaluate_prediction(ax = ax)
        i = 1
        evaluate_prediction_details_df = pd.DataFrame.from_dict(details, orient='index')
        ax_evaluate_prediction_details_df = plt.subplot(gs[i, 1:])
        bbox = [0, 0, 1, 1]
        ax_evaluate_prediction_details_df.axis('off')
        mpl_table = ax_evaluate_prediction_details_df.table(
            cellText=evaluate_prediction_details_df.values, rowLabels=evaluate_prediction_details_df.index, bbox=bbox, colLabels=evaluate_prediction_details_df.columns)
        mpl_table.auto_set_font_size(True)
        ax_evaluate_prediction_details_df.set_title("Prediction Evaluation")

    if chart_type == CHART_TYPE_CHANGE_POINT_PRIOR_ANALYSIS:
        try:
            tickerAnalysis.changepoint_prior_analysis(changepoint_priors=[0.001, 0.05, 0.1, 0.2], ax = ax)
        except Exception:
            LOGGER.exception("Error plotting changepoint_prior_analysis")

    # # i += 1
    # # ax_changepoint_prior_validation_1 = plt.subplot(gs[i, :])
    # # i += 1
    # # ax_changepoint_prior_validation_2 = plt.subplot(gs[i, :])
    # # tickerAnalysis.changepoint_prior_validation(changepoint_priors=[0.001, 0.05, 0.1, 0.2], ax1=ax_changepoint_prior_validation_1, ax2=ax_changepoint_prior_validation_2)

    if chart_type == CHART_TYPE_CHANGE_POINT_PRIOR_VALIDATION:
        i += 1
        ax2 = plt.subplot(gs[i, :])
        i += 1
        ax3 = plt.subplot(gs[i, :])
        try:
            tickerAnalysis.changepoint_prior_validation(changepoint_priors=[0.001, 0.05, 0.1, 0.2], ax1=ax, ax2=ax2, ax3=ax3)
        except Exception:
            LOGGER.exception("Error plotting changepoint_prior_validation")


    if chart_type == CHART_TYPE_EVALUATE_PREDICTION_WITH_CHANGE_POINT:
        tickerAnalysis.changepoint_prior_scale = 0.05
        try:
            details = tickerAnalysis.evaluate_prediction(ax = ax)
            i = 1
            evaluate_prediction_details_df = pd.DataFrame.from_dict(details, orient='index')
            ax_evaluate_prediction_details_df = plt.subplot(gs[i, 1:])
            bbox = [0, 0, 1, 1]
            ax_evaluate_prediction_details_df.axis('off')
            mpl_table = ax_evaluate_prediction_details_df.table(
                cellText=evaluate_prediction_details_df.values, rowLabels=evaluate_prediction_details_df.index, bbox=bbox, colLabels=evaluate_prediction_details_df.columns)
            mpl_table.auto_set_font_size(True)
            ax_evaluate_prediction_details_df.set_title("Prediction Evaluation")
        except Exception:
            LOGGER.exception("Error plotting evaluate_prediction")

    if chart_type == CHART_TYPE_PREDICT_FUTURE:
        try:
            tickerAnalysis.predict_future(ax = ax)
        except Exception:
            LOGGER.exception("Error plotting predict_future")

    return fig

