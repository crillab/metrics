import re
import unittest

from autograph.core.enumstyle import LineType, Position, FontWeight

from metrics.core.constants import *
from metrics.wallet import Analysis, find_best_cpu_time_input, import_analysis_from_file


class NormalAnalysisPlotsTestCase(unittest.TestCase):

    def setUp(self) -> None:
        inconsistent_returns = {'ERR WRONGCERT', 'ERR UNSAT'}
        successful_returns = {'SAT', 'UNSAT'}

        self.analysis = Analysis(
            input_file='data/xcsp19/full_analysis/config/metrics_scalpel_full_paths.yml'
        )

        self.analysis.check_input_consistency(
            lambda df: len(set(df['Checked answer'].unique()) & successful_returns) < 2)
        self.analysis.check_xp_consistency(lambda x: not x['Checked answer'] in inconsistent_returns)

    def test_cactus_plot(self):
        self.analysis.cactus_plot(
            # Cactus plot specificities
            cumulated=False,
            cactus_col='cpu_time',
            show_marker=False,

            # Figure size
            figure_size=(7, 3.5),

            # Titles
            title='Cactus-plot',
            x_axis_name='Number of solved inputs',
            y_axis_name='Time',

            # Axis limits
            x_min=50,
            x_max=None,
            y_min=None,
            y_max=None,

            # Axis scaling
            logx=False,
            logy=False,

            # Legend parameters
            legend_location=Position.RIGHT,
            legend_offset=(0, 0),
            ncol_legend=1,

            # Style mapping
            color_map={
                'VBS': '#000000'
            },
            style_map={
                'VBS': LineType.DASH_DOT,
            },

            # Title font styles
            title_font_name='Helvetica',
            title_font_color='#000000',
            title_font_size=FONT_SIZE,
            title_font_weight=FontWeight.BOLD,

            # Label font styles
            label_font_name='Helvetica',
            label_font_color='#000000',
            label_font_size=FONT_SIZE,
            label_font_weight=FontWeight.BOLD,

            # Others
            latex_writing=True,
            output="data/xcsp19/full_analysis/output/cactus.pdf",
            dynamic=False
        )

    def test_cactus_plot_2(self):
        self.analysis.cactus_plot(
            # Cactus plot specificities
            cumulated=True,
            cactus_col='cpu_time',
            show_marker=True,

            # Figure size
            figure_size=(7, 7),

            # Titles
            title='Cactus-plot',
            x_axis_name='Number of solved inputs',
            y_axis_name='Time',

            # Axis limits
            x_min=50,
            x_max=100,
            y_min=20,
            y_max=500,

            # Axis scaling
            logx=True,
            logy=True,

            # Legend parameters
            legend_location=Position.BOTTOM,
            legend_offset=(0, 0),
            ncol_legend=2,

            # Title font styles
            title_font_name='Helvetica',
            title_font_color='#000000',
            title_font_size=FONT_SIZE,
            title_font_weight=FontWeight.BOLD,

            # Label font styles
            label_font_name='Helvetica',
            label_font_color='#000000',
            label_font_size=FONT_SIZE,
            label_font_weight=FontWeight.BOLD,

            # Others
            latex_writing=False,
            output="data/xcsp19/full_analysis/output/cactus2.pdf",
            dynamic=False
        )

    def test_cdf_plot(self):
        self.analysis.cdf_plot(
            # Cactus plot specificities
            cumulated=False,
            cdf_col='cpu_time',
            show_marker=False,

            # Figure size
            figure_size=(7, 3.5),

            # Titles
            title='CDF-plot',
            x_axis_name='Time',
            y_axis_name='Number of solved inputs',

            # Axis limits
            x_min=None,
            x_max=None,
            y_min=None,
            y_max=None,

            # Axis scaling
            logx=False,
            logy=False,

            # Legend parameters
            legend_location=Position.RIGHT,
            legend_offset=(0, 0),
            ncol_legend=1,

            # Style mapping
            color_map={
                'VBS': '#000000'
            },
            style_map={
                'VBS': LineType.DASH_DOT,
            },

            # Title font styles
            title_font_name='Helvetica',
            title_font_color='#000000',
            title_font_size=FONT_SIZE,
            title_font_weight=FontWeight.BOLD,

            # Label font styles
            label_font_name='Helvetica',
            label_font_color='#000000',
            label_font_size=FONT_SIZE,
            label_font_weight=FontWeight.BOLD,

            # Others
            latex_writing=True,
            output="data/xcsp19/full_analysis/output/cdf.pdf",
            dynamic=False
        )

    def test_scatter_plot(self):
        self.analysis.scatter_plot(
            # Cactus plot specificities
            xp_ware_x='choco-solver 2019-09-24',
            xp_ware_y='PicatSAT 2019-09-12',
            scatter_col='cpu_time',
            color_col='Checked answer',

            # Figure size
            figure_size=(7, 3.5),

            # Titles
            title='',
            x_axis_name=None,
            y_axis_name=None,
            show_label_count=True,

            # Axis limits
            x_min=1,
            x_max=None,
            y_min=1,
            y_max=None,

            # Axis scaling
            logx=True,
            logy=True,

            # Legend parameters
            legend_location=Position.TOP,
            legend_offset=(0, -.1),
            ncol_legend=2,

            # Title font styles
            title_font_name='Helvetica',
            title_font_color='#000000',
            title_font_size=FONT_SIZE,
            title_font_weight=FontWeight.BOLD,

            # Label font styles
            label_font_name='Helvetica',
            label_font_color='#000000',
            label_font_size=FONT_SIZE,
            label_font_weight=FontWeight.BOLD,

            # Others
            latex_writing=True,
            output="data/xcsp19/full_analysis/output/scatter.pdf",
            dynamic=False
        )

    def test_box_plot(self):
        self.analysis.remove_experiment_wares({
            'Concrete 3.12.2',
            'cosoco 2.0'
        }).box_plot(
            # Box plot specificities
            box_col='cpu_time',

            # Figure size
            figure_size=(7, 7),

            # Titles
            title='',
            x_axis_name=None,
            y_axis_name=None,

            # Axis limits
            x_min=None,
            x_max=None,

            # Axis scaling
            logx=True,

            # Title font styles
            title_font_name='Helvetica',
            title_font_color='#000000',
            title_font_size=FONT_SIZE,
            title_font_weight=FontWeight.BOLD,

            # Label font styles
            label_font_name='Helvetica',
            label_font_color='#000000',
            label_font_size=FONT_SIZE,
            label_font_weight=FontWeight.BOLD,

            # Others
            latex_writing=True,
            output="data/xcsp19/full_analysis/output/box.pdf",
            dynamic=False
        )

    def test_box_plot_by_family(self):
        family_re = re.compile(r'^XCSP\d\d/(.*?)/')

        new_analysis = self.analysis.add_variable(
            new_var='family',
            function=lambda x: family_re.match(x['input']).group(1)
        )

        new_analysis = new_analysis.keep_experiment_wares({
            'cosoco 2'
        })

        new_analysis.box_plot(
            # Box plot specificities
            box_by='family',
            box_col='cpu_time',

            # Figure size
            figure_size=(7, 20),

            # Titles
            title='',
            x_axis_name=None,
            y_axis_name=None,

            # Axis limits
            x_min=None,
            x_max=None,

            # Axis scaling
            logx=True,

            # Title font styles
            title_font_name='Helvetica',
            title_font_color='#000000',
            title_font_size=FONT_SIZE,
            title_font_weight=FontWeight.BOLD,

            # Label font styles
            label_font_name='Helvetica',
            label_font_color='#000000',
            label_font_size=FONT_SIZE,
            label_font_weight=FontWeight.BOLD,

            # Others
            latex_writing=False,
            output="data/xcsp19/full_analysis/output/box_by_family.pdf",
            dynamic=False
        )


if __name__ == '__main__':
    unittest.main()
