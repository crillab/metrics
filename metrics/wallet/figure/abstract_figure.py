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
import matplotlib

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

    def __init__(self, campaign_df: CampaignDataFrame, xp_ware_name_map: dict = None, output: str = None):
        """
        A figure at least need a CampaignDataFrame.
        @param campaign_df: a CampaignDataFrame.
        """
        self._campaign_df = campaign_df
        self._xp_ware_name_map = xp_ware_name_map
        self._output = output

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


class Table(Figure):

    def __init__(self, campaign_df: CampaignDataFrame, commas_for_number: bool = False, dollars_for_number: bool = False, **kwargs):
        super().__init__(campaign_df, **kwargs)
        self._commas_for_number = commas_for_number
        self._dollars_for_number = dollars_for_number

    def _output_maker(self, df):
        if self._output is None:
            return

        if self._commas_for_number:
            df = df.applymap(lambda x: f"{x:,d}")

        if self._dollars_for_number:
            df = df.applymap(lambda x: f"${x}$")

        if self._xp_ware_name_map is not None:
            df.index = df.index.map(lambda x: self._xp_ware_name_map[x] if x in self._xp_ware_name_map else x)

        ext = self._output.split('.')[-1]

        if ext == 'tex':
            with open(self._output, 'w') as file:
                df.to_latex(
                    buf=file,
                    escape=False,
                    index_names=False,
                    bold_rows=True
                )

    def get_figure(self):
        """

        @return: the figure.
        """

        df = self.get_data_frame()
        self._output_maker(df)

        return df

class Plot(Figure):
    """
    A plot is a figure print in 2d with axis and title.
    """

    def __init__(self, campaign_df: CampaignDataFrame, figsize=(7, 5), font_name='DejaVu Sans', font_size=12, font_color='#000000', logx: bool = False, logy: bool = False, latex_writing: bool = False, x_min: int = 0, y_min: int = 0, x_max: int = -1, y_max: int = -1, **kwargs):
        super().__init__(campaign_df, **kwargs)

        self._font_name = font_name
        self._font_size = font_size
        self._font_color = font_color
        self._logx = logx
        self._logy = logy
        self._latex_writing = latex_writing
        self._x_min = x_min
        self._y_min = y_min
        self._x_max = x_max
        self._y_max = y_max
        self._figsize = figsize

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

    def _set_font(self):
        font = {
            'family': self._font_name,
            'size': self._font_size,
        }

        matplotlib.rc('font', **font)
        matplotlib.rc('axes', titlesize=self._font_size)
        matplotlib.rc('text', usetex=self._latex_writing)
        matplotlib.rc('text', color=self._font_color)
        matplotlib.rc('axes', labelcolor=self._font_color)
        matplotlib.rc('xtick', color=self._font_color)
        matplotlib.rc('ytick', color=self._font_color)

    def _get_x_lim(self, ax):
        min, max = ax.get_xlim()
        min = self._x_min if self._x_min != -1 else min
        max = self._x_max if self._x_max != -1 else max
        return [min, max]

    def _get_y_lim(self, ax):
        min, max = ax.get_ylim()
        min = self._y_min if self._y_min != -1 else min
        max = self._y_max if self._y_max != -1 else max
        return [min, max]

    def _get_final_xpware_name(self, col):
        mapped = self._xp_ware_name_map is not None and col in self._xp_ware_name_map
        return self._xp_ware_name_map[col] if mapped else col


class CactusPlot(Plot):
    """
    Creation of a cactus plot.
    """

    def __init__(self, campaign_df: CampaignDataFrame, cumulated=False, show_marker=True, color_map=None, style_map=None, cactus_col='cpu_time', legend_location: str = 'best', ncol_legend: int = 1, bbox_to_anchor=None, **kwargs):
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
        self.show_marker = show_marker
        self.color_map = color_map
        self.style_map = style_map
        self.cactus_col = cactus_col
        self._legend_location = legend_location
        self._bbox_to_anchor = bbox_to_anchor
        self._ncol_legend = ncol_legend

    def get_data_frame(self):
        """

        @return: the pandas dataframe used by this figure.
        """
        df_solved = self._campaign_df.filter_by([CampaignDFFilter.ONLY_SOLVED]).data_frame
        df_cactus = df_solved.pivot(columns='experiment_ware', values=self.cactus_col)
        for col in df_cactus.columns:
            df_cactus[col] = df_cactus[col].sort_values().values
        df_cactus = df_cactus.dropna(how='all').reset_index(drop=True)
        df_cactus = df_cactus[df_cactus.index > self._x_min]

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


class CDFPlot(Plot):
    """
    Creation of a Cumulative Distribution Function to compare the performance of several solvers.
    """

    def __init__(self, campaign_df: CampaignDataFrame, color_map=None, style_map=None, cdf_col='cpu_time', legend_location: str = 'best', ncol_legend: int = 1, bbox_to_anchor=None, **kwargs):
        """
        Creates a cactus plot.
        @param campaign_df: the campaign dataframe to plot.
        @param color_map: a color map to personalise each plot line by a given color.
        @param style_map: a style map to personalise each plot line by a given style (dotted...).
        @param xp_ware_name_map: a mapping of experimentware names.
        """
        super().__init__(campaign_df, **kwargs)
        self.color_map = color_map
        self.style_map = style_map
        self.cdf_col = cdf_col
        self._legend_location = legend_location
        self._bbox_to_anchor = bbox_to_anchor
        self._ncol_legend = ncol_legend

    def get_data_frame(self):
        """

        @return: the pandas dataframe used by this figure.
        """
        df_solved = self._campaign_df.data_frame
        df_cdf = df_solved.pivot(columns='experiment_ware', values=self.cdf_col)

        order = list(df_cdf.count().sort_values(ascending=False).index)
        df_cdf = df_cdf[order]

        return df_cdf

    def get_x_axis_name(self):
        """

        @return: the x axis name.
        """
        return 'Time'

    def get_y_axis_name(self):
        """

        @return: the y axis name.
        """
        return 'Solved inputs'

    def get_title(self):
        """

        @return: the title of the plot.
        """
        return 'Comparison of experimentwares'


class ScatterPlot(Plot):
    """
    Creation of a scatter plot.
    """

    def __init__(self, campaign_df: CampaignDataFrame, xp_ware_x, xp_ware_y, sample=None, scatter_col='cpu_time', marker_alpha: float = 0.3, **kwargs):
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
        self._marker_alpha = marker_alpha

    def get_data_frame(self):
        """

        @return: the pandas dataframe used by this figure.
        """
        df_solved = self._campaign_df.filter_by([CampaignDFFilter.ONLY_SOLVED]).data_frame
        df_scatter = df_solved.pivot_table(index=['input'], columns='experiment_ware', values=self.scatter_col,
                                           fill_value=self._campaign_df.campaign.timeout)

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
        df_by_ware = self._campaign_df.data_frame
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
