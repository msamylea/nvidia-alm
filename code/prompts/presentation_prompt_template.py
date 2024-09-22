
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