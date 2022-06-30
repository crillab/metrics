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
from autograph import create_plot
from autograph.core.enumstyle import Position, FontWeight, MarkerShape, LineType
from autograph.core.style import TextStyle, LegendStyle, PlotStyle

from metrics.core.constants import *


class Plot:

    def __init__(self,
                 dynamic=False,
                 label_font_color=FONT_COLOR,
                 label_font_name=FONT_NAME,
                 label_font_size=FONT_SIZE,
                 label_font_weight=FontWeight.NORMAL,
                 logx=False, logy=False,
                 title_font_color=FONT_COLOR,
                 title_font_name=FONT_NAME,
                 title_font_size=FONT_SIZE,
                 title_font_weight=FontWeight.BOLD,
                 latex_writing=False,
                 figure_size=FIGURE_SIZE,
                 x_min=None, x_max=None,
                 y_min=None, y_max=None,
                 output=None
                 ):
        self._plot = create_plot(DYNAMIC_PLOT if dynamic else STATIC_PLOT)

        self._plot.latex = latex_writing
        self._plot.title_style = TextStyle()
        self._plot.title_style.font_name = title_font_name
        self._plot.title_style.size = title_font_size
        self._plot.title_style.weight = title_font_weight
        self._plot.title_style.color = title_font_color

        self._plot.y_label_style = TextStyle()
        self._plot.y_label_style.font_name = label_font_name
        self._plot.y_label_style.size = label_font_size
        self._plot.y_label_style.weight = label_font_weight
        self._plot.y_label_style.color = label_font_color

        self._plot.x_label_style = TextStyle()
        self._plot.x_label_style.font_name = label_font_name
        self._plot.x_label_style.size = label_font_size
        self._plot.x_label_style.weight = label_font_weight
        self._plot.x_label_style.color = label_font_color

        self._plot.log_x = logx
        self._plot.log_y = logy

        self._plot.figure_size = figure_size

        self._x_lim = (x_min, x_max)
        self._y_lim = (y_min, y_max)

        self._output = output

    @property
    def plot(self):
        return self._plot

    def _legend(self, legend_location, legend_offset, ncol_legend):
        self._plot.legend = LegendStyle()
        self._plot.legend.n_col = ncol_legend
        self._plot.legend.position = legend_location
        self._plot.legend.offset = legend_offset

    def _set_limitations(self):
        self._plot.x_lim = self._x_lim
        self._plot.y_lim = self._y_lim

    def save(self):
        if self._output is not None:
            self._plot.save(self._output, bbox_inches='tight', transparent=True)

    def show(self):
        return self._plot.show()


class LinePlot(Plot):

    def __init__(self,
                 df,
                 title=CACTUS_TITLE,
                 x_axis_name=CACTUS_X_LABEL,
                 y_axis_name=CACTUS_Y_LABEL,
                 show_marker=True,
                 color_map=None,
                 style_map=None,
                 legend_location=Position.RIGHT,
                 legend_offset=(0, 0),
                 ncol_legend=1,
                 **kwargs
                 ):
        super().__init__(**kwargs)

        self._plot.title = title

        self._plot.x_label = x_axis_name
        self._plot.y_label = y_axis_name

        color_map = dict() if color_map is None else color_map
        style_map = dict() if style_map is None else style_map

        for name, series in df.iteritems():
            style = PlotStyle()
            if name in color_map:
                style.color = color_map[name]
            if name in style_map:
                style.line_type = style_map[name]
            if show_marker:
                style.marker_shape = MarkerShape.CIRCLE
            self._plot.plot(x=series.index, y=series, label=name, style=style)

        if legend_location is not None:
            self._legend(legend_location, legend_offset, ncol_legend)

        self._set_limitations()


class CDFPlot(Plot):

    def __init__(self,
                 df,
                 n_inputs,
                 title=CDF_TITLE,
                 normalized=False,
                 x_axis_name=CDF_X_LABEL,
                 y_axis_name=CDF_Y_LABEL,
                 show_marker=True,
                 color_map=None,
                 style_map=None,
                 legend_location=Position.RIGHT,
                 legend_offset=(0, 0),
                 ncol_legend=1,
                 **kwargs
                 ):
        super().__init__(**kwargs)

        self._plot.title = title

        self._plot.x_label = x_axis_name
        self._plot.y_label = y_axis_name

        color_map = dict() if color_map is None else color_map
        style_map = dict() if style_map is None else style_map

        for name, series in df.iteritems():
            style = PlotStyle()
            if name in color_map:
                style.color = color_map[name]
            if name in style_map:
                style.line_type = style_map[name]
            if show_marker:
                style.marker_shape = MarkerShape.CIRCLE
            y = series.index / n_inputs if normalized else series.index
            self._plot.plot(x=series, y=y, label=name, style=style)

        if legend_location is not None:
            self._legend(legend_location, legend_offset, ncol_legend)

        self._set_limitations()


class ScatterPlot(Plot):

    def __init__(self,
                 df,
                 title=SCATTER_TITLE,
                 x_axis_name=None,
                 y_axis_name=None,
                 show_label_count=False,
                 legend_location=Position.RIGHT,
                 legend_offset=(0, 0),
                 ncol_legend=1,
                 color_col=None,
                 **kwargs
                 ):
        super().__init__(**kwargs)

        self._plot.title = title
        self._plot.x_label = df.columns[0] if x_axis_name is None else x_axis_name
        self._plot.y_label = df.columns[1] if y_axis_name is None else y_axis_name

        diag_style = PlotStyle()
        diag_style.line_type = LineType.DASH
        diag_style.color = 'gray'
        limits = [0, df.iloc[:, 0:2].max().max()]

        self._plot.plot(
            limits,
            limits,
            label=None,
            style=diag_style
        )

        if color_col is None:
            self._plot.scatter(df.iloc[:, 0], df.iloc[:, 1])
        else:
            for name, sub in df.groupby(color_col):
                self._plot.scatter(sub.iloc[:, 0], sub.iloc[:, 1], label=name)

        if show_label_count:
            self._label_count(df)

        if legend_location is not None and color_col is not None:
            self._legend(legend_location, legend_offset, ncol_legend)

        self._set_limitations()

    def _label_count(self, df):
        x = df.apply(lambda x: x[0] < x[1], axis=1).sum()
        y = df.apply(lambda x: x[0] > x[1], axis=1).sum()

        self._plot.x_label = f'{self._plot.x_label} (count={x})'
        self._plot.y_label = f'{self._plot.y_label} (count={y})'


class BoxPlot(Plot):

    def __init__(self,
                 df,
                 title=BOX_TITLE,
                 x_axis_name=None,
                 y_axis_name=None,
                 # legend_location=Position.RIGHT,
                 # legend_offset=(0, 0),
                 # ncol_legend=1,
                 **kwargs
                 ):
        super().__init__(**kwargs)

        self._plot.title = title

        self._plot.x_label = x_axis_name
        self._plot.y_label = y_axis_name

        self._plot.boxplot(
            [df[col].dropna() for col in df.columns],
            labels=df.columns
        )


class BarPlot(Plot):

    def __init__(self,
                 df,
                 colx,
                 coly,
                 category=None,
                 title=BAR_TITLE,
                 x_axis_name=None,
                 y_axis_name=None,
                 legend_location=Position.RIGHT,
                 legend_offset=(0, 0),
                 ncol_legend=1,
                 estimator=sum,
                 **kwargs
                 ):
        super().__init__(**kwargs)

        self._plot.barplot(
            colx, coly, df, category=category,estimator=estimator
        )

        if legend_location is not None:
            self._legend(legend_location, legend_offset, ncol_legend)

        self._plot.title = title
        self._plot.x_label = x_axis_name
        self._plot.y_label = y_axis_name
