# Analyse a Campaign in *Metrics*

Once the YAML file is correctly configurated ([Reading a Campaign into *Metrics*](scalpel-config.md)), we can start the analysis of data.
To analyze the campaign of experiments thanks to *Metrics*, 
you need to use the *Wallet* module of *Metrics*.
*Wallet* stands for *"Automated tooL for expLoiting Experimental resulTs"*
(*wALLET*).

To manipulate data, *Wallet* uses a [*pandas Dataframe*](https://pandas.pydata.org/). 
A dataframe is a table composed of rows corresponding to experimentations and columns (or variables) corresponding to experimentation information (cpu time, memory, all the input and experiment-ware information, etc.).
It is not necessary to have any knowledge about this library to manipulate *Wallet* data.

## Create/Import/Export an Analysis

### The Classical Analysis Object

To create a new analysis, we only need to import the *Wallet* module and instantiate a new Analysis object with the path to the YAML configuration file:

```python
from metrics.wallet import Analysis
my_analysis = Analysis(input_file='path/to/YAML/file')
```

### Export and Import an Analysis

Once the analysis is created, the user can export it (i.e., to save it into a file):

```python
json_text = my_analysis.export()
```

and import it thanks to the `import_analysis` function:

```python
same_analysis = import_analysis(json_text)
```

> You can observe an example of these commands in [this notebook](https://github.com/crillab/metrics/blob/master/example/sat-competition/2019/make_analysis.ipynb)

## Manipulate the Data from Analysis

Before producing the first figures, *Wallet* proposes to manipulate the different rows/experimentations composing the dataframe. It permits the user to analyze more finely its campaign.

### Describe the Current Analysis

Before manipulating the analysis, it could be interesting to describe it:

```python
my_analysis.describe(
	show_experiment_wares=False,
	show_inputs=False
)
```

>This Analysis is composed of:
>- 55 experiment-wares 
>- 400 inputs
>- 22000 experiments (0 missing -> more details: <Analysis>.get_error_table())

This first method permits us to fastly understand how is composed our campaign. Here, we can show simple statistics, as the number of experiment-wares, inputs, or missing experiments, but we can also show exhaustively the different input and experiment-ware names (by replacing `False` by `True` for `show_experiment_wares` and `show_experiment_wares` parameters). If it exists missing data, the *Wallet* analysis can print a table showing what are these missing experiments by calling `my_analysis.get_error_table()`.

> You can observe an example of this command in [this notebook](https://github.com/crillab/metrics/blob/master/example/sat-competition/2019/make_analysis.ipynb)

### Generate a New Information/Variable for Each Experiment

*Wallet* can add new information to its dataframe by giving a function/lambda to a mapping method of Analysis. For the next example, our input name corresponds to the path of the input (i.e. `/somewhere/family/input-parameters.cnf`). It could be interesting to extract the family name to use it in our next analyses. For this, we use the method `map()` from Analysis:

```python
import re

rx = re.compile("^/somewhere/(.*?)/")
my_analysis.map(
	new_col='family', 
	function=lambda x: rx.findall(x['input'])[1]
)
```

`map()` takes as first parameter the name of the future created column, and as second parameter the lambda that applies the regular expression `rx` to the variable `input` of the row `x` (the regex returns a list where the second element is the family name we need).

> You can observe an example of this command in [this notebook](https://github.com/crillab/metrics/blob/master/example/sat-competition/2019/static_scatter_and_output.ipynb). Here, we extract the satisfiability information from the experimentation (we create a *sat* column).

### Subset of Analysis Rows

Thanks to Analysis, we are also able to make a subset of the analysis. By default, it exists some useful subset methods into Analysis object:

+ `get_only_failed()`: returns a new Analysis with only the failed experiments.
+ `get_only_common_failed()`: returns a new Analysis with only the common failed experiments. It corresponds to inputs for which no experiment-ware has succeeded.
+ `get_only_success()`: returns a new Analysis with only the successful experiments.
+ `get_only_common_success()`: returns a new Analysis with only the common successful experiments. It corresponds to inputs for which no experiment-ware has failed.
+ `delete_common_failed()`: returns a new Analysis where commonly failed inputs are removed.
+ `delete_common_success()`: returns a new Analysis where commonly succeeded inputs are removed.

Finally, we present a last and generic method to make a subset of an analysis. In the next example, we show how to keep only two experiment-wares:

```python
my_new_analysis = my_analysis.sub_analysis(
	column='experiment_ware', 
	sub_set={'CaDiCaL', 'Maple'}
)
```

`sub_analysis` method takes two parameters:
- `column` corresponds to the column we want to filter
- `sub_set` corresponds to a set of values allowed for the filtering

In this previous example, only `CaDiCaL` and `Maple` appear in the `my_new_analysis` analysis.

> You can observe an example of this subset in [this notebook](https://github.com/crillab/metrics/blob/master/example/sat-competition/2019/static_cactus_and_output.ipynb). Here, we want to have a clearer view on these manifold exepriment-wares.

### *GroupBy* Operator

The *GroupBy* operator permits to create a list of new Analysis grouped by a column value. For example, if we have the family name `family` of inputs in the dataframe, it could be interesting to make separated analysis of each of them:

```python
for sub_analysis in my_analysis.groupby('family'):
	print(sub_analysis.describe())
```

These previous lines will describe the analysis of each family of `my_analysis`.

### Add a Virtual Best Experiment-Ware

Sometimes, it could be interesting to introduce what we call a *Virtual Best Experiment-Ware (VBEW)* in order to compare our current experiment-wares to this virtual best one. A VBEW selects the best experiment for each input from a selection of real experiment-ware:

```python
my_analysis_plus_vbs = my_analysis.add_vbew(
	xp_ware_set={'CaDiCaL', 'Maple'}, 
	opti_col='cpu_time',
	minimize=True,
	vbew_name='my_best_solver'
)
```

Here, we create a VBEW named `my_best_solver` and based on the best performances of `CaDiCaL` and `Maple`. `my_best_solver` will receive the result of one of these two experiment-wares minimizing the `opti_col` column.

> You can observe an example of this method in [this notebook](https://github.com/crillab/metrics/blob/master/example/sat-competition/2019/static_cactus_and_output.ipynb). Here, we create two different VBEWs.

## Draw Figures

Now we have the analysis built and we have manipulated the data we want to highlight, we can start to draw figures. Thanks to *Wallet*, we are able to build two kinds of figures: static and dynamic.

### Static Figures

*Wallet* permits to draw static plots and computing tables showing different statistic measures. These figures can easily be exported in a format specified by the user, such as LaTeX for tables and PNG or vectorial graphics (such as SVG or EPS images). Static plots are highly configurable in order to fit in their final destination (e.g., in slides or articles).

#### The Statistic Table

*Wallet* proposes two main tables showing different kinds of statistics. The first one permits us to show a global overview of the results. The main **statistic table** permits to show these statistics:

- `count` is the number of solved inputs for a given experiment-ware.
- `sum` is the time taken by the experiment-ware to solve (or not) inputs (including timeout inputs).
- `PARx` is equivalent to `sum` but gives a penalty of `x` times the timeout to failed experiments.
- `common count` is the number of inputs commonly solved by all the experiment-wares.
- `common sum` is the time taken to solve the commonly solved inputs.
- `uncommon count` corresponds to the number of inputs solved by an experiment-ware less the common ones (the common ones could be considered as easy inputs).

```python
my_analysis.get_stat_table(
    par=[2, 10]

    output='path/for/the/output.tex', # output path or None
    
    dollars_for_number=True, # 123456789 -> $123456789$
    commas_for_number=True,  # 123456789 -> 123,456,789
    
    xp_ware_name_map=None, # a map to rename experimentwares
)
```

This first table is given by calling the previous method with different parameters:
- `par` corresponds to the different values we want to give to the PARx column(s).
- `output` is the path to the output we want to produce (i.e. a LaTeX table).
- `dollars_for_number` permits to put numbers in maths mode (for the LaTeX output).
- `commas_for_number` permits to split numbers with commas in maths mode (for the LaTeX output).
- `xp_ware_name_map` is a map that permits to rename each experiment_ware names for the output table.

> A statistic table is given in [this notebook](https://github.com/crillab/metrics/blob/master/example/sat-competition/2019/tables_and_output.ipynb).

#### The Contribution Table

The second table proposed by *Wallet* allowing to show the **contribution** of each experiment-ware:

- `vbew simple` corresponds to the intersection size of an experiment-ware and the VBEW.
- `vbew x` corresponds to this previous intersection but it only allows experiments that have taken at least `x` second(s).
- `contribution` corresponds to the case that an experiment-ware is the only one that has been able to solve an input.

As the previous table, we just need to call it by this simple method:

```python
my_analysis.get_contribution_table(
    output='path/for/the/output.tex', # output path or None
    
    deltas=[1, 10, 100], # minimum resolution cpu_time for the vbew
    
    dollars_for_number=True, # if True, 123456789 -> $123456789$
    commas_for_number=True,  # if True, 123456789 -> 123,456,789
    
    xp_ware_name_map=None, # a map to rename experimentwares
)
```

`deltas` correspond to the list of `vbew x` we want to show in the table.

> A contribution table is given in [this notebook](https://github.com/crillab/metrics/blob/master/example/sat-competition/2019/tables_and_output.ipynb).

#### Static Cactus-Plot

*Wallet* proposed many plots to show data.

A first kind of plots that allows to consider an overview of all the
experimentwares is the *cactus plot*. A cactus plot considers all solved inputs of each
experimentware. Each line in the plot represent an experimentware. Inputs are
ordered by solving time for each experiment-ware to build this figure: the x-axis
corresponds to the rank of the solved input and the y-axis to the time taken to
solve the input, so that the righter the line, the better the solver. Note that
we can also cumulate the runtime of each solved inputs to get a smoother plot.

```python
sub_analysis.get_cactus_plot(
    cactus_col='cpu_time', # column permitting to draw lines of the cactus
    cumulated=False,       # cumulate or not the cactus_col value
    show_marker=False,     # show a marker for each experiment
    
    output='output/cactus_zoom.pdf', # output path or None
    figsize=(10,7),                  # size of the figure to output (inch)
    
    color_map=xpware_color,        # a map to force the color of each experimentware line
    style_map=xpware_type,         # a map to force forces the line style of each experimentware line
    xp_ware_name_map=xpware_map,   # a map to rename experimentwares
    
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
```

> A full example of a static cactus-plot is given in [this notebook](https://github.com/crillab/metrics/blob/master/example/sat-competition/2019/static_cactus_and_output.ipynb).

#### Static CDF-Plot

An equivalent plot is also considered to gain in generality of usage through 
communities: the Cumulative Distribution Function (CDF). This plot is based on a histogram: x-axis corresponds
to the y-axis of the cactus-plot (time), and y-axis corresponds to the normalized 
number of solved inputs.

```python
my_analysis.get_cdf( # CDF = Cumulative distributive Function
    cdf_col='cpu_time', 
    
    output='output/cdf.pdf', # output path or None
    figsize=(15,10),         # size of the figure to output (inch)
    
    color_map=None, 
    style_map=None,
    xp_ware_name_map=None, # a map to rename experimentwares
    
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
```

> A full example of a static CDF-plot is given in [this notebook](https://github.com/crillab/metrics/blob/master/example/sat-competition/2019/static_cdf_and_output.ipynb).

#### Static Box-Plot

In addition to cactus and CDF plots, one may consider *box plots*
to get more detailed results about the runtime of each solver. A
box in such a plot represents the distribution of each experiment time of a
given experimentware. In particular, such plots allow to easily locate medians,
quartiles and means for all experimentwares in a single figure.
We can find a practical application of this plot in the case of randomized algorithms: 
it permits to visualize the variance and to simply compare the effect of changing 
the random function seed for a given fixed solver configuration using it.

```python
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
```

> A full example of a static box-plot is given in [this notebook](https://github.com/crillab/metrics/blob/master/example/sat-competition/2019/static_box_and_output.ipynb).

#### Static Scatter-Plot

Finally, to get a more detailed comparison of two experimentwares, one can use
scatter plots. Each axis in
this plot corresponds to an experimentware and displays its runtime (between
$`0`$ and the timeout). We can place each input in the plot as a point
corresponding to the time taken by both experimentwares to solve this input. We
can quickly observe if there exists a trend for one experimentware or the other in
terms of efficiency.

```python
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
```

> A full example of a static scatter-plot is given in [this notebook](https://github.com/crillab/metrics/blob/master/example/sat-competition/2019/static_scatter_and_output.ipynb).

#### Dynamic Plots

Dynamic plots can be called by simply giving a new parameter of these previous static figures `dynamic`.

For example:

```python
my_analysis.get_scatter_plot(dynamic=True)
```

> A global view of the dynamic plots is given in [this notebook](https://github.com/crillab/metrics/blob/master/example/sat-competition/2019/dynamic_analysis.ipynb).

## Advanced Usage

For advanced users, it is possible to get the original *pandas Dataframe* and manipulate it thanks to this command:

```python
df = my_analysis.campaign_df.data_frame
```

The advanced user could now follow the [*pandas documentation*](https://pandas.pydata.org/docs/) or more concisely this [*pandas cheat sheet*](https://pandas.pydata.org/Pandas_Cheat_Sheet.pdf).


