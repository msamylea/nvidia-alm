
summarize_prompt = """
Given the section content you are provided, create a very short summary of the key points of this section.
Do not provide the data or code, only text.
Your response should be no more than 2 - 3 sentences total.

Section Content:
{section_content}

"""
generate_plots_prompt = """ 
You have been given a dataset and a section name for a report.
From this, you will generate a single plot recommendation for the section that demonstrates an interesting insight from the data.

Categorical Columns: {categorical_columns}
Numerical Columns: {numerical_columns}
Datetime Columns: {datetime_columns}

Section: {section_name}

Keeping in mind the column datatypes (categorical, numeric, datetime), ensure you choose a plot type that fits the columns you want to use.
For example, if you want to use a categorical column, it must be used in a plot that supports categorical data.  The same applies to numeric and datetime columns.
Do not try to apply the wrong column datatype to a required element that does not support it.

You must select a plot type from below and return the required elements in a JSON format:

plot type                    required
scatter                      x (numeric or datetime), y (numeric), size (numeric), color (any)
bar                          x (categorical or numeric), y (numeric), color (categorical)
area                         x (numeric or datetime), y (numeric), color (categorical), line_group (categorical)
violin                       x (categorical), y (numeric), color (categorical)
ecdf                         x (numeric), color (categorical)
parallelcoordinates          (all columns numeric)
pie                          x (categorical), y (numeric)
timeseries                   x (datetime), y (numeric)
heatmap                      (all columns numeric)

If data is timeseries, it is preferrable to use a timeseries plot. If data is categorical, it is preferrable to use a pie chart or bar plot.

Example JSON format for each plot type:
{
    "scatter": {
        "x": "column_name",
        "y": "column_name",
        "size": "column_name",
        "color": "column_name"
}

{
    "bar": {
        "x": "column_name",
        "y": "column_name",
        "color": "column_name"
}

{
    "area": {
        "x": "column_name",
        "y": "column_name",
        "color": "column_name",
        "line_group": "column_name"
}

{
    "violin": {
        "x": "column_name",
        "y": "column_name",
        "color": "column_name"
}

{
    "ecdf": {
        "x": "column_name",
        "color": "column_name"
}

{
    "parallelcoordinates": {}
}

{
    "heatmap": {}
}

{
    "timeseries": {
        "x": "column_name",
        "y": "column_name"
}

Important! You must generate only one recommendation and you must not include any other information in your response.

"""

prepare_outline_prompt = """
You are a data science expert tasked with creating a comprehensive outline for a data-driven report. 
Use the provided dataset context to generate an insightful analysis plan.

Dataset Context:
{dataset_context}

Your outline should focus on extracting meaningful insights and patterns from the data. Include the following elements in your outline:

1. An overarching report title that captures the main theme of the analysis.
2. 4-6 main sections, each targeting a specific aspect of the data or analysis type.

Your goal is to provide an outline to be used to create a detailed analysis of the dataset.

Do not include the data schema, data outline, data types, or dataset statistics in the outline.
The outline is entirely focused on the insights and content of the dataset.

Your outline should be formatted as JSON as follows. Do not add additional properties to the JSON object:
{
    "Report_Title": "Suggested Report Title",
    "Sections": [
        {"Section_Name": "Suggested Section Name"},
        {"Section_Name": "Suggested Section Name"},
        {"Section_Name": "Suggested Section Name"},
    ]
}

IMPORTANT: Do not reply with any text outside of the JSON format. Only provide the JSON formatted outline.
The conclusions and recommendations will be created separately so do not include them as a section.
"""

write_section_prompt = """
You have been given a dataset to analyze and have been asked to write a section of a report based on the data.

Write a detailed analysis of the data for the section you have been assigned targeted toward
fulfilling the user query, including as much detail as possible.

The section you are writing is as follows:
{section_name}

User Query: {user_query}

Schema:
{schema}

Summary:
{summary}

CRITICAL: Only use information directly present in the dataset as described above. Do not introduce any external information or assumptions. Do not mention any specific entities, platforms, tools, or channels that are not explicitly present in this dataset.

IMPORTANT GUIDELINES:
1. Provide SPECIFIC, DATA-DRIVEN insights. Do not use placeholder values like 'Category X' or 'X%'.
2. Use ACTUAL numbers, percentages, and category names from the dataset.
3. If you don't have a specific piece of information, DO NOT make it up or use placeholders. Instead, focus on the data you do have.
4. Every claim or insight should be backed by specific data points from the dataset.
5. Do not discuss data types, null counts, or column names. Focus on the actual insights from the data.
6. Do not rename columns or data points. Use the exact names as they appear in the dataset.
7. If you're unsure about a specific value, use phrases like "approximately" or "around" instead of making up precise numbers.

Return your analysis and insights in a detailed report.
Use markdown to format your report and provide clear explanations for your findings.
Do not include an introduction or conclusion, only the analysis.
Do not include recommendations or next steps in your response.
Do not include plots or visualizations in your response.
You may include tables or statistics if they are relevant to your analysis, but do not use a table for single comparisons or values.
You may use mathjax for mathematical notation if necessary, and should show how you arrived at conclusions.

Do not use markdown formatting inside tables.

Table formatting:
| Column 1 | Column 2 | Column 3 |
|----------|----------|----------|
| Data 1   | Data 2   | Data 3   |

Remember: Your goal is to provide concrete, data-driven insights. If you can't make a specific claim based on the data, don't make the claim at all.
"""

write_recommendations_conclusions_prompt = """
As a senior data strategist renowned for uncovering critical insights, your task is to synthesize the provided report sections into powerful recommendations and conclusions.

Report Sections:
{combined_sections}

Your response should include two main parts: Recommendations and Conclusions.

Do not mention the user or the user query.  Do not mention data types or column names.

For the Recommendations section:

1. Provide 3-5 specific, actionable recommendations based on the insights from the report.
2. For each recommendation:
   - Clearly state the recommended action
   - Explain the rationale behind it, citing specific data points or insights from the report
   - Describe the potential impact or benefit of implementing the recommendation
   - Suggest a high-level approach for implementation
3. Prioritize recommendations based on potential impact and feasibility
4. Include at least one recommendation that addresses a potential risk or challenge identified in the analysis

For the Conclusions section:

1. Summarize the 3-4 most significant findings from the entire report
2. Highlight any overarching patterns or themes that emerged across different sections
3. Discuss how the findings answer the original user query or business question
4. Address any limitations of the analysis and suggest areas for further investigation
5. Provide a forward-looking statement on the implications of these findings for future strategy or decision-making

Formatting Guidelines:
- Use '## Recommendations' and '## Conclusions' for main section headers
- Use '#### ' for subheaders within each section
- Use '* ' for unordered lists and '1. ' for ordered lists
- Use '**bold**' for emphasis on key points or critical numbers but never inside tables
- Use '`code`' for specific data points or metrics
- Use '> ' for blockquotes or notable quotes
- Use '---' for horizontal rules to separate major parts of the section

IMPORTANT:
- Ensure all recommendations and conclusions are directly tied to the data and insights presented in the report
- Provide quantitative support for your points wherever possible
- Focus on strategic, high-level insights rather than repeating detailed findings from individual sections
- Do not introduce new data or analyses not mentioned in the original report sections
- Maintain a balanced view, addressing both positive findings and areas for improvement
- Maintain consistent formatting throughout the section
- Do not make up names for items (e.g., "Category A", or "Product B"). If you don't know
the name, don't include the item in your response.
"""

presentation_prompt = """
Create a compelling multi-slide presentation based on the following section content. Focus on key insights, data points, and actionable recommendations. Your slides should be concise yet informative. If there's tabular data or plot information, include it in your response.

Section Content:
{section_content}

Guidelines:
1. Create 2-4 slides, each with a clear, short, attention-grabbing title (max 3 words).
2. For each slide, provide 3-5 bullet points, each no longer than 15 words.
3. Include at least one key statistic or data point per slide, if available.
4. Do not include code.
5. Do include tables that were in the section content using the table format below.
6. Do not make up names for items (e.g., "Category A", or "Product B"). If you don't know
the name, don't include the item in your response.

Return your response in this format:

<Slide>
<Section_Title>{Section Title}</Section_Title>
<Content>
- {Bullet Point 1}
- {Bullet Point 2}
- {Bullet Point 3}
</Content>
<Table>
| Column 1 | Column 2 | Column 3 |
|----------|----------|----------|
| Data 1   | Data 2   | Data 3   |
| Data 4   | Data 5   | Data 6   |
</Table>
</Slide>

<Slide>
<Section_Title>{Section Title}</Section_Title>
<Content>
- {Bullet Point 1}
- {Bullet Point 2}
- {Bullet Point 3}
</Content>
</Slide>

Note: Only include the <Table> section if there's relevant tabular data to present.
"""