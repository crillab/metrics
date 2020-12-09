Analyze a Campaign in *Metrics*
===============================

Once the YAML file is correctly configured (`Reading a Campaign into
Metrics <scalpel-config.html>`__), we can start the analysis of data. To
analyze the campaign of experiments thanks to *Metrics*, you need to use
the *Wallet* module of *Metrics*. *Wallet* stands for *“Automated tooL
for expLoiting Experimental resulTs”* (*wALLET*).

To manipulate data, *Wallet* uses a `pandas
Dataframe <https://pandas.pydata.org/>`__. A dataframe is a table
composed of rows corresponding to experimentations and columns (or
variables) corresponding to experimentation information (cpu time,
memory, all the input and experiment-ware information, etc.). It is not
necessary to have any knowledge about this library to manipulate
*Wallet* data.

Create/Import/Export an Analysis
--------------------------------

The Classical Analysis Object
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To create a new analysis, you only need to import the ``Analysis`` class
from *Wallet* module and instantiate a new ``Analysis`` object with the
path to the YAML configuration file:

.. code:: python

   from metrics.wallet import Analysis
   my_analysis = Analysis(input_file='path/to/YAML/file')

Export and Import an Analysis
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Once the analysis is created, it is possible to export it (e.g., to save
it to a file):

.. code:: python

   json_text = my_analysis.export()

and to import it with the ``import_analysis`` function:

.. code:: python

   same_analysis = import_analysis(json_text)

..

   You can observe an example of these functions in `this
   notebook <https://github.com/crillab/metrics/blob/master/example/sat-competition/2019/make_analysis.ipynb>`__.

Manipulate the Data from Analysis
---------------------------------

Before producing the first figures, *Wallet* proposes to manipulate the
different rows/experimentations composing the dataframe. It allows to
analyze more finely the campaign.

Describe the Current Analysis
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Before manipulating the analysis, it could be interesting to describe
it:

.. code:: python

   my_analysis.describe(
       show_experiment_wares=False,
       show_inputs=False
   )

which yields the following:

::

   This Analysis is composed of:
   - 55 experiment-wares 
   - 400 inputs
   - 22000 experiments (0 missing -> more details: <Analysis>.get_error_table())

This first method allows to fastly understand how is composed the
campaign. Here, simple statistics are shown, as the number of
experiment-wares, inputs, or missing experiments, but one can also show
exhaustively the different input and experiment-ware names (by replacing
``False`` by ``True`` for the ``show_experiment_wares`` and
``show_experiment_wares`` parameters). If it exists missing data, the
*Wallet* analysis can print a table showing what are these missing
experiments by calling ``my_analysis.get_error_table()``.

   You can observe an example of this method in `this
   notebook <https://github.com/crillab/metrics/blob/master/example/sat-competition/2019/make_analysis.ipynb>`__.

Generate a New Information/Variable for Each Experiment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

*Wallet* can add new information to the underlying dataframe by giving a
function/lambda to a mapping method of ``Analysis``. For the next
example, the input name corresponds to the path of the input (e.g.,
``/somewhere/family/input-parameters.cnf``). It could be interesting to
extract the family name to use it in the rest of the analysis. For this,
we use the method ``map()`` from ``Analysis``:

.. code:: python

   import re

   rx = re.compile('^/somewhere/(.*?)/')
   my_analysis.map(
       new_col='family', 
       function=lambda x: rx.findall(x['input'])[1]
   )

``map()`` takes as first parameter the name of the future created
column, and as second parameter the lambda that applies the regular
expression ``rx`` to the variable ``input`` of the row ``x`` (the
regular expression returns a list in which the second element is the
family name we need).

   You can observe an example of this command in `this
   notebook <https://github.com/crillab/metrics/blob/master/example/sat-competition/2019/static_scatter_and_output.ipynb>`__.
   Here, the satisfiability information from the experimentation is
   extracted into a ``sat`` column.

Subset of ``Analysis`` Rows
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Thanks to ``Analysis``, we are also able to make a subset of the
analysis. By default, it exists some useful subset methods in
``Analysis`` object:

-  ``get_only_failed()``: returns a new ``Analysis`` with only the
   failed experiments.
-  ``get_only_common_failed()``: returns a new ``Analysis`` with only
   the common failed experiments. It corresponds to inputs for which no
   experiment-ware has succeeded.
-  ``get_only_success()``: returns a new ``Analysis`` with only the
   successful experiments.
-  ``get_only_common_success()``: returns a new ``Analysis`` with only
   the common successful experiments. It corresponds to inputs for which
   no experiment-ware has failed.
-  ``delete_common_failed()``: returns a new ``Analysis`` where commonly
   failed inputs are removed.
-  ``delete_common_success()``: returns a new ``Analysis`` where
   commonly succeeded inputs are removed.

Finally, we present a last and generic method to make a subset of an
analysis. In the next example, we show how to keep only two
experiment-wares:

.. code:: python

   my_new_analysis = my_analysis.sub_analysis(
       column='experiment_ware', 
       sub_set={'CaDiCaL', 'Maple'}
   )

The ``sub_analysis`` method takes two parameters: - ``column``
corresponds to the column we want to filter - ``sub_set`` corresponds to
a set of values allowed for the filtering

In the example above, only ``CaDiCaL`` and ``Maple`` appear in the
``my_new_analysis`` analysis.

   You can observe an example of this subset in `this
   notebook <https://github.com/crillab/metrics/blob/master/example/sat-competition/2019/static_cactus_and_output.ipynb>`__.
   Here, we want to have a clearer view on these manifold
   exepriment-wares.

``groupby`` Operator
~~~~~~~~~~~~~~~~~~~~

The ``groupby`` operator allows to create a list of new ``Analysis``
instances grouped by a column value. For example, if we have the family
name ``family`` of inputs in the dataframe, it could be interesting to
make separated analysis of each of them:

.. code:: python

   for sub_analysis in my_analysis.groupby('family'):
       print(sub_analysis.describe())

These previous lines will describe the analysis of each family of
``my_analysis``.

Add a Virtual Best Experiment-Ware
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Sometimes, it may be interesting to introduce what we call a *Virtual
Best Experiment-Ware (VBEW)*, which generalize the well-known *Virtual
Best Solvers* (VBS). It allows to compare our current experiment-wares
to the virtual best one. A VBEW selects the best experiment for each
input from a selection of real experiment-ware:

.. code:: python

   my_analysis_plus_vbs = my_analysis.add_vbew(
       xp_ware_set={'CaDiCaL', 'Maple'}, 
       opti_col='cpu_time',
       minimize=True,
       vbew_name='my_best_solver'
   )

Here, we create a VBEW named ``my_best_solver`` and based on the best
performances of ``CaDiCaL`` and ``Maple``. ``my_best_solver`` will
receive the result of one of these two experiment-wares minimizing the
``opti_col`` column.

   You can observe an example of this method in `this
   notebook <https://github.com/crillab/metrics/blob/master/example/sat-competition/2019/static_cactus_and_output.ipynb>`__.
   Here, we create two different VBEWs.

Draw Figures
------------

After having built the analysis and manipulated the data we want to
highlight, we can start drawing figures. Thanks to *Wallet*, we are able
to build two kinds of figures: static and dynamic.

*Wallet* permits to draw static plots and computing tables showing
different statistic measures. These figures can easily be exported in a
format specified by the user, such as LaTeX for tables and PNG or
vectorial graphics (such as SVG or EPS) for images. Static plots are
highly configurable in order to fit in their final destination (e.g., in
slides or articles).

Static Tables
~~~~~~~~~~~~~

*Wallet* proposes two main tables showing different kinds of statistics.

The Statistic Table
^^^^^^^^^^^^^^^^^^^

The first one allows to show a global overview of the results through
the following statistics:

-  ``count`` is the number of solved inputs for a given experiment-ware.
-  ``sum`` is the time taken by the experiment-ware to solve (or not)
   inputs (including timeout inputs).
-  ``PARx`` is equivalent to ``sum`` but adds a penalty of ``x`` times
   the timeout to failed experiments (*PAR* stands for *Penalised
   Average Runtime*).
-  ``common count`` is the number of inputs commonly solved by all the
   experiment-wares.
-  ``common sum`` is the time taken to solve the commonly solved inputs.
-  ``uncommon count`` corresponds to the number of inputs solved by an
   experiment-ware less the common ones (the common ones could be
   considered as easy inputs).

.. code:: python

   my_analysis.get_stat_table(
       par=[2, 10]

       output='path/for/the/output.tex', # output path or None
       
       dollars_for_number=True, # 123456789 -> $123456789$
       commas_for_number=True,  # 123456789 -> 123,456,789
       
       xp_ware_name_map=None, # a map to rename experiment-wares
   )

This first table is given by calling the previous method with different
parameters: - ``par`` corresponds to the different values we want to
give to the PARx column(s). - ``output`` is the path to the output we
want to produce (e.g., a LaTeX table). - ``dollars_for_number`` puts
numbers in math mode (for LaTeX outputs). - ``commas_for_number`` splits
numbers with commas in math mode (for LaTeX outputs). -
``xp_ware_name_map`` is a map allowing to rename each experiment-ware
names in the output table.

   A statistic table is given in `this
   notebook <https://github.com/crillab/metrics/blob/master/example/sat-competition/2019/tables_and_output.ipynb>`__.

The Contribution Table
^^^^^^^^^^^^^^^^^^^^^^

The second table proposed by *Wallet* allowing to show the
**contribution** of each experiment-ware:

-  ``vbew simple`` corresponds to the number of times an experiment-ware
   has been selected in the VBEW.
-  ``vbew d`` corresponds to the number of times an experiment-ware
   solves an instance at ``d`` second(s) faster than all other solvers.
-  ``contribution`` corresponds to the case that an experiment-ware is
   the only one that has been able to solve an input (a.k.a.
   state-of-the-art contribution).

As for the previous table, one just needs to call the following method:

.. code:: python

   my_analysis.get_contribution_table(
       output='path/for/the/output.tex', # output path or None
       
       deltas=[1, 10, 100], # minimum resolution cpu_time for the vbew
       
       dollars_for_number=True, # if True, 123456789 -> $123456789$
       commas_for_number=True,  # if True, 123456789 -> 123,456,789
       
       xp_ware_name_map=None, # a map to rename experiment-wares
   )

``deltas`` correspond to the list of ``vbew d`` we want to show in the
table.

   A contribution table is given in `this
   notebook <https://github.com/crillab/metrics/blob/master/example/sat-competition/2019/tables_and_output.ipynb>`__.

Static Plots
~~~~~~~~~~~~

*Wallet* proposed many plots to show data. Static plots have some common
parameters:

-  ``output``: output path to save the figure or ``None``.
-  ``figsize``: size of the figure to output (inches).
-  ``color_map``: a map to force the color of each experiment-ware line.
-  ``style_map``: a map to force the line style of each experiment-ware
   line.
-  ``xp_ware_name_map``: a map to rename the experiment-wares.
-  ``font_name``: the font name to set.
-  ``font_size``: the size name to set.
-  ``font_color``: the font color to set.
-  ``latex_writing``: if ``True``, allows to write in LaTeX mode.
-  ``logx``: log scale for the x-axis.
-  ``logy``: log scale for the y-axis.
-  ``[x|y]_[min|max]``: set the limit of an axis, or ``-1`` to take the
   default value of ``matplotlib``.
-  ``legend_location`` and ``bbox_to_anchor``: see the ```matplotlib``
   documentation for legend
   placement <https://matplotlib.org/3.1.1/tutorials/intermediate/legend_guide.html#legend-location>`__.
-  ``ncol_legend``: number of columns for the legend (default: ``1``).

Static Cactus-Plot
^^^^^^^^^^^^^^^^^^

A first kind of plots that allows to consider an overview of all the
experiment-wares is the *cactus plot*. A cactus plot considers all
solved inputs of each experiment-ware. Each line in the plot represents
an experiment-ware. Inputs are ordered by solving time for each
experiment-ware to build this figure: the x-axis corresponds to the rank
of the solved input and the y-axis to the time taken to solve the input,
so that the righter the line, the better the solver. Note that we can
also cumulate the runtime of each solved inputs to get a smoother plot.

.. code:: python

   sub_analysis.get_cactus_plot(
       cactus_col='cpu_time', # column permitting to draw lines of the cactus
       cumulated=False,       # cumulate or not the cactus_col value
       show_marker=False,     # show a marker for each experiment
       
       output='output/cactus_zoom.pdf', # output path or None
       figsize=(10,7),                  # size of the figure to output (inch)
       
       color_map=xpware_color,        # a map to force the color of each experiment-ware line
       style_map=xpware_type,         # a map to force forces the line style of each experiment-ware line
       xp_ware_name_map=xpware_map,   # a map to rename experiment-wares
       
       # font properties
       font_name='Times New Roman',
       font_size=12,
       font_color='#000000',
       latex_writing=True, # if True, permits to write in latex mode (make attention to some characters)
       
       logx=False, # log scale to x-axis
       logy=False, # log scale to y-axis
       
       # set the limit of axis, or -1 to take the default value of matplotlib
       x_min=200,
       x_max=-1,
       y_min=-1,
       y_max=-1,
       
       # matplotlib legend location
       legend_location='best',
       bbox_to_anchor=None,
       ncol_legend=1,
   )

By default, the cactus plot draws its graphic by using the ``cpu_time``
of the results: you are free to change this behaviour by replacing the
``cactus_col`` parameter. You can ask this plot to cumulate the runtime
by giving ``cumulated=True``. We can show and hide markers thanks to
``show_marker`` parameter.

   A full example of a static cactus-plot is given in `this
   notebook <https://github.com/crillab/metrics/blob/master/example/sat-competition/2019/static_cactus_and_output.ipynb>`__.

Static CDF-Plot
^^^^^^^^^^^^^^^

Equivalently to cactus plot, one may instead use the so-called
*Cumulative Distribution Function* (CDF), which is well-known when
considering statistics. In this plot x-axis corresponds to the y-axis of
the cactus-plot (time), and the y-axis corresponds to the normalized
number of solved inputs. A point on the line of the CDF may be
interpreted as the probability to solve an input given a time limit.

.. code:: python

   my_analysis.get_cdf( # CDF = Cumulative distributive Function
       cdf_col='cpu_time', 
       
       output='output/cdf.pdf', # output path or None
       figsize=(15,10),         # size of the figure to output (inch)
       
       color_map=None, 
       style_map=None,
       xp_ware_name_map=None, # a map to rename experiment-wares
       
       # font properties
       font_name='Times New Roman',
       font_size=11,
       font_color='#000000',
       latex_writing=False, # if True, permits to write in latex mode (make attention to some characters)
       
       logx=False, # log scale to x-axis
       logy=False, # log scale to y-axis
       
       # set the limit of axis, or -1 to take the default value of matplotlib
       x_min=-1,
       y_min=-1,
       x_max=-1,
       y_max=.65,
       
       # matplotlib legend location
       legend_location="upper center",
       bbox_to_anchor=(0.5, -0.06),
       ncol_legend=3,
   )

By default, the CDF plot draws its graphic by using the ``cpu_time`` of
results: you are free to change this behaviour by replacing the
``cdf_col`` parameter.

   A full example of a static CDF-plot is given in `this
   notebook <https://github.com/crillab/metrics/blob/master/example/sat-competition/2019/static_cdf_and_output.ipynb>`__.

Static Box-Plot
^^^^^^^^^^^^^^^

In addition to cactus and CDF plots, one may consider *box plots* to get
more detailed results about the runtime of each solver. A box in such a
plot represents the distribution of each experiment time of a given
experiment-ware. In particular, such plots allow to easily locate
medians, quartiles and means for all experiment-wares in a single
figure. We can find a practical application of this plot in the case of
randomized algorithms: it permits to visualize the variance and to
simply compare the effect of changing the random function seed for a
given fixed solver configuration using it.

.. code:: python

   my_analysis.get_box_plot( 
       box_col='cpu_time',
       
       output='output/box.pdf', # output path or None
       figsize=(15,10),         # size of the figure to output (inch)
       
       xp_ware_name_map=xpware_map, # a map to rename experiment-wares
       
       # font properties
       font_name='DejaVu Sans',
       font_size=11,
       font_color='#000000',
       latex_writing=True, # if True, permits to write in latex mode (make attention to some characters)
       
       logy=True, # log scale to y-axis
   )

By default, the box plot draw its graphic by using the ``cpu_time`` of
results: the user is free to change this behaviour by replacing the
``cdf_col`` parameter.

   A full example of a static box-plot is given in `this
   notebook <https://github.com/crillab/metrics/blob/master/example/sat-competition/2019/static_box_and_output.ipynb>`__.

Static Scatter-Plot
^^^^^^^^^^^^^^^^^^^

Finally, to get a more detailed comparison of two experiment-wares, one
can use scatter plots. Each axis in this plot corresponds to an
experiment-ware and displays its runtime (between :math:``0`` and the
timeout). We can place each input in the plot as a point corresponding
to the time taken by both experiment-wares to solve this input. We can
quickly observe if there exists a trend for one experiment-ware or the
other in terms of efficiency.

.. code:: python

   my_analysis.get_scatter_plot(
       xp_ware_x='CaDiCaL default', 
       xp_ware_y='MapleLCMDistChronoBT-DL-v2.2 default',
       scatter_col='cpu_time',
       
       # We precise here the new created column to take into account
       color_col='sat',
       
       output='output/scatter.pdf',
       figsize=(7,6),
       
       xp_ware_name_map=xpware_map,
       
       font_name='DejaVu Sans',
       font_size=11,
       font_color='#000000',
       latex_writing=True,
       
       logx=True,
       logy=True,
       
       x_min=-1,
       y_min=-1,
       x_max=-1,
       y_max=-1,
   )

To draw a scatter-plot, we need to specify the experiment-wares on the
x-axis and tge y-axis: ``xp_ware_x`` and ``xp_ware_y``. By default, the
scatter plot draw its graphic by using the ``cpu_time`` of results: you
are free to change this behaviour by replacing the ``cdf_col``
parameter.

   A full example of a static scatter-plot is given in `this
   notebook <https://github.com/crillab/metrics/blob/master/example/sat-competition/2019/static_scatter_and_output.ipynb>`__.

Dynamic Plots
~~~~~~~~~~~~~

Dynamic plots can be called by simply giving a new parameter of these
previous static figures ``dynamic``.

For example:

.. code:: python

   my_analysis.get_scatter_plot(dynamic=True)

..

   A global view of the dynamic plots is given in `this
   notebook <https://github.com/crillab/metrics/blob/master/example/sat-competition/2019/dynamic_analysis.ipynb>`__.

Advanced Usage
--------------

For a more advanced usage, it is possible to get the original *pandas
Dataframe* and to manipulate it thanks to this instruction:

.. code:: python

   df = my_analysis.campaign_df.data_frame

Then simply foloow `pandas
documentation <https://pandas.pydata.org/docs/>`__ or more concisely
this `pandas cheat
sheet <https://pandas.pydata.org/Pandas_Cheat_Sheet.pdf>`__.
