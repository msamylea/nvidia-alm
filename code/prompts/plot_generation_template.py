generate_plots_prompt = """ 
You have been given a dataset and a section name for a report.
From this, you will generate a single plot recommendation for the section that demonstrates an interesting insight from the data.

Categorical Columns: {categorical_columns}
Numerical Columns: {numerical_columns}
Datetime Columns: {datetime_columns}

Section: {section_name}

Keeping in mind the column datatypes (categorical, numeric, datetime), ensure you choose a plot type that fits the columns you want to use.
For example, if you want to use a categorical column, it must be used in a plot that supports categorical data.  
You must select a plot type from below and return the required elements in a JSON format:

plot type                    required
scatter                      x (numeric or datetime), y (numeric), size (numeric), color (any)
bar                          x (categorical or numeric), y (numeric), color (categorical)
regression                   x (numeric), y (numeric)
violin                       x (categorical), y (numeric), color (categorical)
ecdf                         x (numeric), color (categorical)
parallelcoordinates          (all columns numeric)
pie                          x (categorical), y (numeric)
timeseries                   x (datetime), y (numeric)

If data is timeseries, it is preferrable to use a timeseries plot. If data is categorical, it is preferrable to use a pie chart or bar plot.

Example JSON format:
{
    "scatter": {
        "x": "column_name",
        "y": "column_name",
        "size": "column_name",
        "color": "column_name"
}

Important! You must generate only one recommendation and you must not include any other information in your response.

"""