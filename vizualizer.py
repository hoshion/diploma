import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import matplotlib.colors as mcolors
import matplotlib.patches as mpatches

if __name__ == '__main__':
    # Load data
    df = pd.read_excel("llama3.1-2.xlsx")

    # Create a date column
    df['date'] = pd.to_datetime(df[['year', 'month', 'day']])

    # Extract the week number (YYYY-Wxx format for better sorting)
    df['week'] = df['date'].dt.strftime('%Y-W%U')

    # Count sentiment occurrences per section per week
    weekly_counts = df.groupby(['week', 'section', 'sentiment_word']).size().reset_index(name='count')

    # Pivot to get separate columns for each sentiment type
    weekly_pivot = weekly_counts.pivot_table(index=['week', 'section'],
                                             columns='sentiment_word',
                                             values='count',
                                             fill_value=0).reset_index()

    # Rename columns for clarity
    weekly_pivot.columns.name = None
    weekly_pivot = weekly_pivot.rename(columns={'POSITIVE': 'Positive',
                                                'NEUTRAL': 'Neutral',
                                                'NEGATIVE': 'Negative'})

    # Compute total sentiments per section per week
    weekly_pivot['Total'] = weekly_pivot[['Positive', 'Neutral', 'Negative']].sum(axis=1)

    # Normalize to percentage
    for sentiment in ['Positive', 'Neutral', 'Negative']:
        weekly_pivot[sentiment] = weekly_pivot[sentiment]

    # Sort by week for correct ordering
    weekly_pivot = weekly_pivot.sort_values(by='week')

    # Define unique sections
    sections = weekly_pivot['section'].unique()

    # Define a color map for sections
    base_colors = {
        'Політика': 'blue',
        'Війна': 'red',
        'Культура': 'orange',
        'Світ': 'purple',
        'Економіка': 'green',
        'Лайфстайл': 'yellow',
        'Суспільство': 'teal'
    }
    default_color = 'gray'  # Default if a section isn’t in the dictionary


    def adjust_color(color, factor):
        """Lightens or darkens a color by a given factor (0 = black, 1 = original color, >1 = lighter)"""
        rgb = mcolors.to_rgb(color)
        adjusted_rgb = tuple(min(1, max(0, c * factor)) for c in rgb)
        return mcolors.to_hex(adjusted_rgb)


    # Generate sentiment colors for each section
    section_colors = {}
    for section in sections:
        base_color = base_colors.get(section, default_color)
        section_colors[section] = {
            'Positive': adjust_color(base_color, 1.4),  # Lighter
            'Neutral': base_color,
            'Negative': adjust_color(base_color, 0.6)  # Darker
        }

    # Plot
    fig, ax = plt.subplots(figsize=(18, 6))

    # Get unique weeks
    weeks = weekly_pivot['week'].unique()
    bar_width = 0.1  # Width of each section's bar within a week
    x_positions = np.arange(len(weeks))  # X-axis positions for weeks

    # Offset positions for each section within the same week
    section_offsets = np.linspace(-bar_width * len(sections) / 2,
                                  bar_width * len(sections) / 2,
                                  len(sections))

    # Loop over sections to plot
    for i, section in enumerate(sections):
        subset = weekly_pivot[weekly_pivot['section'] == section]

        if not subset.empty:
            # Align bars for correct week positions
            week_indices = [np.where(weeks == week)[0][0] for week in subset['week']]
            x_vals = x_positions[week_indices] + section_offsets[i]

            # Get section-specific colors
            positive_color = section_colors[section]['Positive']
            neutral_color = section_colors[section]['Neutral']
            negative_color = section_colors[section]['Negative']

            # Plot stacked bars
            ax.bar(x_vals, subset['Positive'], width=bar_width, label=f"{section} - Positive" if i == 0 else "",
                   color=positive_color)
            ax.bar(x_vals, subset['Neutral'], width=bar_width, label=f"{section} - Neutral" if i == 0 else "",
                   color=neutral_color, bottom=subset['Positive'])
            ax.bar(x_vals, subset['Negative'], width=bar_width, label=f"{section} - Negative" if i == 0 else "",
                   color=negative_color, bottom=subset['Neutral'] + subset['Positive'])

    # Create a legend with section names and base colors
    legend_patches = [mpatches.Patch(color=base_colors.get(sec, default_color), label=sec) for sec in sections]
    ax.legend(handles=legend_patches, title="Sections", loc="upper left", bbox_to_anchor=(1, 1))

    # Formatting
    ax.set_xticks(x_positions)
    ax.set_xticklabels(weeks, ha="right")
    ax.set_ylabel("Sentiment Word Amount")
    ax.set_xlabel("Week")
    ax.set_title("Sentiment Word Distribution by Section and Week")
    plt.savefig("sentiment_plot.png")
