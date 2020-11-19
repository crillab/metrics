# ##############################################################################
#  Wallet - A Metrics Module                                                   #
#  Copyright (c) 2019-2020 - Univ Artois & CNRS, Exakis Nelite                 #
#  --------------------------------------------------------------------------  #
#  mETRICS - rEproducible sofTware peRformance analysIs in perfeCt Simplicity  #
#  wALLET - Automated tooL for expLoiting Experimental resulTs                 #
#                                                                              #
#                                                                              #
#  This program is free software: you can redistribute it and/or modify it     #
#  under the terms of the GNU Lesser General Public License as published by    #
#  the Free Software Foundation, either version 3 of the License, or (at your  #
#  option) any later version.                                                  #
#                                                                              #
#  This program is distributed in the hope that it will be useful, but         #
#  WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY  #
#  or FITNESS FOR A PARTICULAR PURPOSE.                                        #
#  See the GNU General Public License for more details.                        #
#                                                                              #
#  You should have received a copy of the GNU Lesser General Public License    #
#  along with this program.                                                    #
#  If not, see <https://www.gnu.org/licenses/>.                                #
# ##############################################################################

"""
This module provides classes for dynamic plots.
"""

import plotly.graph_objects as go
import plotly.express as px

from metrics.wallet.figure.abstract_figure import CactusPlot, ScatterPlot, BoxPlot, CDFPlot
import plotly.io as pio
pio.templates.default = 'none'


class CactusPlotly(CactusPlot):
    """
    Creation of a dynamic cactus plot.
    """

    def get_figure(self):
        """

        @return: the figure.
        """
        return go.Figure({
            'data': self._get_data(),
            'layout': self._get_layout()
        })

    def _get_data(self):
        self.df_cactus = self.get_data_frame()
        solvers = list(self.df_cactus.columns)

        return [{
            'name': col,
            'mode': 'lines+markers' if self._show_marker else 'lines',
            'marker.symbol': i % 10,
            'line.width': 2,
            'x': self.df_cactus.index,
            'y': self.df_cactus[col],
        } for i, col in enumerate(solvers)]

    def _get_layout(self):
        return {
            'title.text': self.get_title(),
            'xaxis.title.text': self.get_x_axis_name(),
            'yaxis.title.text': self.get_y_axis_name(),
        }


class CDFPlotly(CDFPlot):
    """
    Creation of a dynamic CDF.
    """

    def get_figure(self):
        """

        @return: the figure.
        """
        return go.Figure({
            'data': self._get_data(),
            'layout': self._get_layout()
        })

    def _get_data(self):
        self.df_cactus = self.get_data_frame()
        solvers = list(self.df_cactus.columns)

        return [{
            'name': col,
            'mode': 'lines',
            'marker.symbol': i % 10,
            'line.width': 2,
            'x': self.df_cactus[col],
            'y': self.df_cactus.index / len(self.df_cactus.index),
        } for i, col in enumerate(solvers)]

    def _get_layout(self):
        return {
            'title.text': self.get_title(),
            'xaxis.title.text': self.get_x_axis_name(),
            'yaxis.title.text': self.get_y_axis_name(),
        }


class ScatterPlotly(ScatterPlot):
    """
    Creation of a dynamic scatter plot.
    """

    def get_figure(self):
        """

        @return: the figure.
        """
        return go.Figure({
            'data': self._get_data(),
            'layout': self._get_layout()
        })

    def _get_data(self):
        self._extra_col(self._df_scatter, self._color_col)

        if self._color_col is None:
            return [{
                'x': self._df_scatter[self._xp_ware_i],
                'y': self._df_scatter[self._xp_ware_j],
                'text': self._df_scatter.index,
                'mode': 'markers',
            }]
        else:
            return [{
                'x': sub[self._xp_ware_i],
                'y': sub[self._xp_ware_j],
                'text': sub.index,
                'mode': 'markers',
                'name': name
            } for name, sub in self._df_scatter.groupby(self._color_col)]

    def _get_layout(self):
        timeout = self._campaign_df.campaign.timeout
        shapes = [{
            'x0': opt[0],
            'y0': opt[1],
            'x1': timeout,
            'y1': timeout,
            'type': 'line',
            'line': {'color': 'gray', 'width': 2, 'dash': opt[2]}
        } for opt in [(self._min, self._min, 'dash'), (self._min, timeout, 'dot'), (timeout, self._min, 'dot')]
        ]

        return {
            'title.text': self.get_title(),
            'xaxis': {
                'title': self.get_x_axis_name(),
                'type': 'log'
            },
            'yaxis': {
                'title': self.get_y_axis_name(),
                'type': 'log'
            },
            'hovermode': 'closest',
            'shapes': shapes
        }


class BoxPlotly(BoxPlot):
    """
    Creation of a dynamic box plot.
    """

    def get_figure(self):
        """

        @return: the figure.
        """
        return go.Figure({
            'data': self._get_data(),
            'layout': self._get_layout()
        })

    def _get_data(self):
        df = self.get_data_frame()

        return [
            go.Box({
                'y': df[col],
                'boxpoints': 'all',
                'name': col,
                'marker.size': 2,
                'boxmean': True,
                'showlegend': False
            })
            for col in df.columns]

    def _get_layout(self):
        return {
            'title.text': self.get_title(),
            'yaxis.type': 'log'
        }
