import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd 


class Plotter:
    def __init__(self, figsize=(15, 8), style="whitegrid", title="Plot", xlabel="X-axis", ylabel="Y-axis"):
        """
        Initializes the Plotter class with basic plot settings.

        Args:
            figsize: Tuple for plot dimensions, default is (10, 6).
            style: Seaborn style to use, default is "whitegrid".
            title: Title of the plot, default is "Plot".
            xlabel: Label for X-axis, default is "X-axis".
            ylabel: Label for Y-axis, default is "Y-axis".
        """
        self.figsize = figsize
        self.style = style
        self.title = title
        self.xlabel = xlabel
        self.ylabel = ylabel

        # Apply Seaborn style
        sns.set_style(self.style)
        sns.set_theme(style='darkgrid')

    def plot_basic(self, data, x, y, kind="line", hue=None, marker="o"):
        """
        Plots a basic chart based on the given data and plot type.

        Args:
            data: DataFrame or data structure to plot.
            x: Column name or data for the x-axis.
            y: Column name or data for the y-axis.
            kind: Type of plot to create (e.g., "line", "scatter", "bar"), default is "line".
        """
        # Create a new figure and axis
        fig, ax = plt.subplots(figsize=self.figsize)

        if kind == "line":
            sns.lineplot(data=data, x=x, y=y, hue=hue, marker=marker, ax=ax, linewidth=2.5, markersize=7)
        elif kind == "scatter":
            sns.scatterplot(data=data, x=x, y=y, ax=ax)
        elif kind == "bar":
            sns.barplot(data=data, x=x, y=y, ax=ax)

        # Customize plot with title and labels
        ax.set_title(self.title)
        ax.set_xlabel(self.xlabel)
        ax.set_ylabel(self.ylabel)
        ax.grid()
        ax.grid(visible=True, color='gray', linestyle='--', linewidth=0.5)
        ax.tick_params(axis='both', which='major', labelsize=12)

        ax.legend(loc="upper left")

        # Return the figure for further use
        return fig
    
    def plot_is_columns_bar_plot(self, summary_df):
        # Filter the rows from summary_df that have 'is_' in the index
        col_names = [index for index in summary_df.index if index.startswith('is_')]
        
        is_df = summary_df.loc[col_names]

        # Sort the DataFrame by the 'mean' column (smallest to largest)
        is_df = is_df.sort_values(by="mean", ascending=True)

        fig, ax = plt.subplots(figsize=(9, 6))
        
        # Plot the 'mean' values as a bar plot
        is_df["mean"].plot(kind='bar', ax=ax, color='gray', edgecolor='black')

        ax.set_title(self.title)
        ax.set_xlabel(self.xlabel)

        # Trim the 'is_' prefix from x-tick labels
        labels = [label.get_text() for label in ax.get_xticklabels()]
        ax.set_xticklabels([label.replace('is_', '') for label in labels])

        # Rotate the x-axis labels by 45 degrees for better visibility
        plt.xticks(rotation=45)

        ax.set_ylabel(self.ylabel)

        # Format y-ticks as percentages
        ax.set_yticklabels([f'{int(x*100)}%' for x in ax.get_yticks()])

        # Customize grid lines
        ax.grid(visible=True, color='gray', linestyle='--', linewidth=0.5)

        return fig

     # NEW: Method to plot histogram for card types
    def plot_histogram(self, data, x, weights_column, bins=10):
        """
        Plots a histogram of card types based on their occurrence, sorted from small to large.

        Args:
            data: DataFrame with the card type and count data.
            x: Column name for card type (e.g., 'card_type').
            weights_column: Column name for the counts or weights (e.g., 'count').
            bins: Number of bins in the histogram, default is 10.
        """
        fig, ax = plt.subplots(figsize=self.figsize)
        
        # Ensure the 'weights_column' is numeric
        data[weights_column] = pd.to_numeric(data[weights_column], errors='coerce')
        
        # Verify that the weights_column exists in the data
        if weights_column not in data.columns:
            raise ValueError(f"Column '{weights_column}' not found in DataFrame")

        # Sort data by the weights_column in ascending order
        sorted_data = data.sort_values(by=weights_column, ascending=True)

        # Plot using seaborn's histplot with weights
        sns.histplot(data=sorted_data, x=x, weights=sorted_data[weights_column], bins=bins, ax=ax, alpha=1)

        ax.set_title(self.title)
        ax.set_xlabel(self.xlabel, fontsize=14)
        ax.set_ylabel(self.ylabel)
        plt.xticks(rotation=45)
        ax.grid(visible=True, color='gray', linestyle='--', linewidth=0.5)

        return fig