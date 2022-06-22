# {{ title }}

{% if description %}
{{ description }}
{% endif %}

## Description of the environment

The experiments presented here have been run on computers running {{ os }},
and equipped with {{ cpu }} and {{ ram }} of RAM.

The CPU time was limited to {{ timeout }} and the memory limit was
set to {{ memout }}.

{% if input_description %}
## Description of the input instances

{{ input_description }}
{% endif %}

{% if xp_ware_description %}
## Description of the experiment-wares

{{ xp_ware_description }}
{% endif %}

## Analysis

We now present an analysis of our experiments using
[*Metrics*](https://github.com/crillab/metrics), which has been used to
generate this report.
You can browse the notebooks of this analysis from the following table of
contents:

{% if load %}- [Loading Experiment Data]({{ load_notebook }}.ipynb){% endif %}
{% if runtime %}- [Analysis of the Runtime]({{ runtime_notebook }}.ipynb){% endif %}
{% if optimization %}- [Analysis of the Best Bounds]({{ optimization_notebook }}.ipynb){% endif %}
