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
This module provides abstraction of each figures.
"""

from metrics.wallet.dataframe.dataframe import CampaignDataFrame, CampaignDFFilter

DEFAULT_COLORS = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22',
                  '#17becf']
"""
Default colors that could be used to customise figures.
"""

class Figure:
    """
    Figure is an abstract object that can represent a plot or a dataframe.
    """

    def __init__(self, campaign_df: CampaignDataFrame):
        """
        A figure at least need a CampaignDataFrame.
        @param campaign_df: a CampaignDataFrame.
        """
        self.campaign_df = campaign_df

    def get_data_frame(self):
        """

        @return: the pandas dataframe used by this figure.
        """
        raise NotImplementedError('Method "get_data_frame()" needs to be implemented!')

    def get_figure(self):
        """

        @return: the figure.
        """
        raise NotImplementedError('Method "get_figure()" needs to be implemented!')


class Plot(Figure):
    """
    A plot is a figure print in 2d with axis and title.
    """

    def __init__(self, campaign_df: CampaignDataFrame, font_name='DejaVu Sans', font_size=12):
        super().__init__(campaign_df)

        self._font = {
            'fontname': 'DejaVu Sans',
            'fontsize': font_size
        }

    def get_x_axis_name(self):
        """

        @return: the x axis name.
        """
        raise NotImplementedError('Method "get_data_frame()" needs to be implemented!')

    def get_y_axis_name(self):
        """

        @return: the y axis name.
        """
        raise NotImplementedError('Method "get_data_frame()" needs to be implemented!')

    def get_title(self):
        """

        @return: the title of the plot.
        """
        raise NotImplementedError('Method "get_data_frame()" needs to be implemented!')


class CactusPlot(Plot):
    """
    Creation of a cactus plot.
    """

    def __init__(self, campaign_df: CampaignDataFrame, cumulated=False, min_solved_inputs=0, show_marker=True, color_map=None, style_map=None, xp_ware_name_map=None, cactus_col='cpu_time', **kwargs):
        """
        Creates a cactus plot.
        @param campaign_df: the campaign dataframe to plot.
        @param cumulated: if True, y axis corresponds to the cumulation of time.
        @param min_solved_inputs: corresponds to the starting of x-axis.
        @param show_marker: if True, show markers for each solved instances.
        @param color_map: a color map to personalise each plot line by a given color.
        @param style_map: a style map to personalise each plot line by a given style (dotted...).
        @param xp_ware_name_map: a mapping of experimentware names.
        """
        super().__init__(campaign_df, **kwargs)
        self.cumulated = cumulated
        self.min_solved_inputs = min_solved_inputs
        self.show_marker = show_marker
        self.color_map = color_map
        self.style_map = style_map
        self.xp_ware_name_map = xp_ware_name_map
        self.cactus_col = cactus_col

    def get_data_frame(self):
        """

        @return: the pandas dataframe used by this figure.
        """
        solvers = self.campaign_df.xp_ware_names
        df_solved = self.campaign_df.filter_by([CampaignDFFilter.ONLY_SOLVED]).data_frame
        df_cactus = df_solved.pivot(columns='experiment_ware', values=self.cactus_col)
        for col in solvers:
            df_cactus[col] = df_cactus[col].sort_values().values
        df_cactus = df_cactus.dropna(how='all').reset_index(drop=True)
        df_cactus = df_cactus[df_cactus.index > self.min_solved_inputs]

        order = list(df_cactus.count().sort_values(ascending=False).index)
        df_cactus = df_cactus[order]

        return df_cactus.cumsum() if self.cumulated else df_cactus

    def get_x_axis_name(self):
        """

        @return: the x axis name.
        """
        return 'Number of solved inputs'

    def get_y_axis_name(self):
        """

        @return: the y axis name.
        """
        return 'Cumulated time' if self.cumulated else 'Time to solve an input'

    def get_title(self):
        """

        @return: the title of the plot.
        """
        return 'Comparison of experimentwares'


class ScatterPlot(Plot):
    """
    Creation of a scatter plot.
    """

    def __init__(self, campaign_df: CampaignDataFrame, xp_ware_x, xp_ware_y, sample=None, scatter_col='cpu_time', **kwargs):
        """
        Creates a scatter plot.
        @param campaign_df: the campaign dataframe to plot.
        @param xp_ware_x: the experimentware name to associate to x-axis.
        @param xp_ware_y: the experimentware name to associate to y-axis.
        @param sample: if there is too much datas, a sample can choose "sample" number of inputs to show.
        """
        super().__init__(campaign_df, **kwargs)
        self.xp_ware_i = xp_ware_x
        self.xp_ware_j = xp_ware_y
        self.sample = sample
        self.scatter_col = scatter_col
        self.df_scatter = self.get_data_frame()
        self.min = self.df_scatter[[self.xp_ware_i, self.xp_ware_j]].min(skipna=True).min()

    def get_data_frame(self):
        """

        @return: the pandas dataframe used by this figure.
        """
        df_solved = self.campaign_df.filter_by([CampaignDFFilter.ONLY_SOLVED]).data_frame
        df_scatter = df_solved.pivot_table(index=['input'], columns='experiment_ware', values=self.scatter_col,
                                           fill_value=self.campaign_df.campaign.timeout)

        return df_scatter.sample(n=self.sample) if self.sample else df_scatter

    def get_x_axis_name(self):
        """

        @return: the x axis name.
        """
        return self.xp_ware_i

    def get_y_axis_name(self):
        """

        @return: the y axis name.
        """
        return self.xp_ware_j

    def get_title(self):
        """

        @return: the title of the plot.
        """
        return f'Comparison of {self.xp_ware_i} and {self.xp_ware_j}'


class BoxPlot(Plot):
    """
    Creation of a box plot.
    """

    def __init__(self, campaign_df: CampaignDataFrame, box_col='cpu_time', **kwargs):
        super().__init__(campaign_df, **kwargs)
        self.box_col = box_col

    def get_data_frame(self):
        """

        @return: the pandas dataframe used by this figure.
        """
        df_by_ware = self.campaign_df.filter_by([CampaignDFFilter.ONLY_SOLVED]).data_frame
        df_by_ware = df_by_ware.pivot(columns='experiment_ware', values=self.box_col)
        return df_by_ware

    def get_x_axis_name(self):
        """

        @return: the x axis name.
        """
        return ''

    def get_y_axis_name(self):
        """

        @return: the y axis name.
        """
        return ''

    def get_title(self):
        """

        @return: the title of the plot.
        """
        return 'Comparison of experimentwares'
