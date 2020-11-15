# Analyse a Campaign into *Metrics*

Once the YAML file is correctly configurated ([Reading a Campaign into *Metrics*](scalpel-config.md)), we can start the analysis of data.
To analyse the campaign of experiments thanks to *Metrics*, 
you need to use the *Wallet* module of *Metrics*.
*Wallet* stands for *"Automated tooL for expLoiting Experimental resulTs"*
(*wALLET*).

To manipulate data, *Wallet* uses a [*pandas Dataframe*](https://pandas.pydata.org/). 
A dataframe is a table composed of rows corresponding to experimentations and columns (or variables) corresponding to experimentation informations (cpu time, memory, all the input and experiment-ware informations, ...).
It is not necessary to have any knowledge about this library to manipulated *Wallet* data.

## Create/Import/Export an Analysis

### The Classical Analysis Object

To create a new analysis, we just need to import the *Wallet* module and instanciate a new Analysis object with the path to the YAML configuration file:

```python
from metrics.wallet import Analysis
my_analysis = Analysis(input_file='path/to/YAML/file')
```

### Export and Import an Analysis

Once the analysis is created, the user is able to export it (to save it into a file):

```python
json_text = my_analysis.export()
```

and import it thanks to the `import_analysis` function:

```python
same_analysis = import_analysis(json_text)
```

## Manipulate the Data Analysis

Before producing the first figures, *Wallet* proposes to manipulate the different rows/experimentations composing the dataframe. It permits to the user to analyse more finely its campaign.

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

This first method permits to fastly understand how is composed our campaign dataframe. Here, we can show simple statistics, as the number of experiment-wares, inputs, or missing experiments, but also we can show exhaustively the different input and experiment-ware names (by replacing `False` by `True` for `show_experiment_wares` and `show_experiment_wares` parameters). If it exists missing data, the *Wallet* analysis is able to show you a table showing what are these missing experiments by calling `my_analysis.get_error_table()`.

### Generate a New Information/Variable to Each Experiment

*Wallet* is able to add new informations to its dataframe by giving a function/lambda to a mapping method of Analysis. For the next example, our input name corresponds to the path of the input (i.e. '/somewhere/family/input-parameters.cnf'). It could be interesting to extract the family name to use it in our next analyses. For this, we use the method `map()` from Analysis:

```python
import re

rx = re.compile("^/somewhere/(.*?)/")
my_analysis.map(
	new_col='family', 
	function=lambda x: rx.findall(x['input'])[1]
)
```

`map()` takes as first parameter the name of the future created column, and as second parameter the lambda that applies the regular expresion `rx` to the variable *input* of the row `x` (the regex returns a list where the second element is the family name we need).


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
- `sub_set` corresponds to a set of value that correpond to allowed value for the column `column`

In this previous example, only 'CaDiCaL' and 'Maple' appear in the `my_new_analysis` analysis.

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

## Draw Figures

### Static Figures

#### Tables

#### Plots

### Dynamic Plots

## Advanced Usage

+ get the original df