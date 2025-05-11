import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
from matplotlib.patches import Patch
import seaborn as sns


def generate_all_stats():
    """Generate all stat graphs including the pie chart"""
    plot_game_results_pie()
    plot_levels_completed_frequency()
    plot_progress_times_boxplot()
    plot_time_stats_table()
    plot_correlation_matrix()


def plot_game_results_pie():
    df = load_game_data()
    if df.empty:
        return

    plt.figure(figsize=(14, 12))

    # Process data
    result_counts = df['game_result'].value_counts()
    percentages = 100 * result_counts / result_counts.sum()

    # Define colors
    colors = {
        'win': '#4CAF50',
        'killed_by_enemy': '#F44336',
        'timeout': '#FFC107',
        'quit': '#9E9E9E'
    }

    # Create pie chart WITHOUT autopct (we'll add custom labels)
    wedges, texts = plt.pie(
        result_counts,
        colors=[colors[r] for r in result_counts.index],
        startangle=90,
        wedgeprops={'linewidth': 2, 'edgecolor': 'white'},
        radius=0.8
    )

    # Add percentages OUTSIDE with connecting lines
    bbox_props = dict(boxstyle="round,pad=0.3", fc="white", ec="black", lw=0.72)
    kw = dict(arrowprops=dict(arrowstyle="-", color='black'),
              bbox=bbox_props, zorder=0, fontsize=16, fontweight='bold')

    for i, (wedge, percent) in enumerate(zip(wedges, percentages)):
        # Calculate label position
        ang = (wedge.theta2 + wedge.theta1) / 2.
        y = np.sin(np.deg2rad(ang))
        x = np.cos(np.deg2rad(ang))

        # Place label outside with connecting line
        horizontalalignment = {-1: "right", 1: "left"}[int(np.sign(x))]
        connectionstyle = f"angle,angleA=0,angleB={ang}"
        kw["arrowprops"].update({"connectionstyle": connectionstyle})

        plt.annotate(
            f"{percent:.1f}%",
            xy=(x * 0.8, y * 0.8),  # Start of line (pie edge)
            xytext=(1*x, 1*y),  # Label position
            horizontalalignment=horizontalalignment,
            **kw
        )

    # Create legend
    legend_elements = [
        Patch(facecolor=colors[r], edgecolor='white',
              label=f"{r.replace('_', ' ').title()} ({percentages.loc[r]:.1f}%)")
        for r in result_counts.index
    ]

    plt.legend(
        handles=legend_elements,
        title='',
        loc="center left",
        bbox_to_anchor=(0.85, 0.5),
        frameon=False,
        fontsize=15
    )

    plt.title("Game Result Distribution",
              fontsize=18,
              pad=0,  # Positive value for proper spacing
              fontweight='bold',
              y=1.02)  # Slight upward nudge
    plt.tight_layout()
    save_plot('game_results_pie.png')


def plot_levels_completed_frequency():
    df = load_game_data()
    if df.empty:
        return

    plt.figure(figsize=(10, 6))

    # Get frequency of each level completion status
    level_counts = df['levels_completed'].value_counts().sort_index()

    # Define colors for each level
    colors = ['#4CAF50', '#2196F3', '#FFC107', '#F44336']

    # Create bar plot
    bars = plt.bar(
        level_counts.index.astype(str),
        level_counts.values,
        color=colors[:len(level_counts)],
        edgecolor='white',
        linewidth=1
    )

    # Add value labels
    for bar in bars:
        height = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width() / 2.,
            height + 0.5,
            f'{height}',
            ha='center',
            va='bottom',
            fontsize=12,
            fontweight='bold'
        )

    # Customize plot
    plt.title('Level Completion Frequency', fontsize=16, pad=20)
    plt.xlabel('Levels Completed', fontsize=14)
    plt.ylabel('Number of Players', fontsize=14)
    plt.xticks(fontsize=12)

    # Force y-axis to show exactly 41 as top value
    ax = plt.gca()  # Get current axis
    ax.set_ylim(0, 45)  # Set hard limit
    ax.set_yticks(list(ax.get_yticks()))  # Add 41 to ticks

    plt.grid(axis='y', alpha=0.3)
    save_plot('levels_completed_frequency.png')


def plot_progress_times_boxplot():
    df = load_game_data()
    if df.empty:
        return

    plt.figure(figsize=(12, 7))

    # Prepare data based on completion progress
    time_data = []
    labels = []

    # 1. Players who only completed Level 1
    mask_level1 = (df['levels_completed'] == 1)
    times_level1 = pd.to_numeric(df.loc[mask_level1, 'level1_time'], errors='coerce')
    times_level1 = times_level1[(times_level1.notna()) & (times_level1 > 0)]
    if not times_level1.empty:
        time_data.append(times_level1)
        labels.append('Level 1')

    # 2. Players who completed Levels 1-2
    mask_level2 = (df['levels_completed'] == 2)
    times_level2 = pd.to_numeric(df.loc[mask_level2, 'level1_time'] +
                                 df.loc[mask_level2, 'level2_time'], errors='coerce')
    times_level2 = times_level2[(times_level2.notna()) & (times_level2 > 0)]
    if not times_level2.empty:
        time_data.append(times_level2)
        labels.append('Levels 2')

    # 3. Players who completed all 3 levels
    mask_level3 = (df['levels_completed'] == 3)
    times_level3 = pd.to_numeric(df.loc[mask_level3, 'level1_time'] +
                                 df.loc[mask_level3, 'level2_time'] +
                                 df.loc[mask_level3, 'level3_time'], errors='coerce')
    times_level3 = times_level3[(times_level3.notna()) & (times_level3 > 0)]
    if not times_level3.empty:
        time_data.append(times_level3)
        labels.append('Level 3')

    if not time_data:
        print("No valid time data available after filtering")
        return

    # Create box plot without mean markers
    box = plt.boxplot(
        time_data,
        labels=labels,
        patch_artist=True,
        medianprops={'linewidth': 2, 'color': 'black'},
        whiskerprops={'linewidth': 1.5},
        capprops={'linewidth': 1.5},
        flierprops={
            'marker': 'o',
            'markersize': 5,
            'markerfacecolor': '#F44366',
            'alpha': 0.6
        }
    )

    # Color boxes
    colors = ['#4CAF50', '#2196F3', '#FFC107']
    for patch, color in zip(box['boxes'], colors[:len(time_data)]):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)

    # Customize plot
    plt.title('Completion Time by Progress Level', fontsize=16, pad=20)
    plt.xlabel('Levels Completed', fontsize=14)
    plt.ylabel('Total Time', fontsize=14)
    plt.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    save_plot('progress_times_boxplot.png')


def plot_time_stats_table():
    df = load_game_data()
    if df.empty:
        return

    # Prepare data - filter valid times (>0)
    stats_data = []
    for level in [1, 2, 3]:
        col = f'level{level}_time'
        if col in df.columns:
            times = pd.to_numeric(df[col], errors='coerce')
            times = times[(times.notna()) & (times > 0)]

            if not times.empty:
                stats_data.append({
                    'Level': level,
                    'Players': len(times),
                    'Min Time': times.min(),
                    'Max Time': times.max(),
                    'Median': times.median(),
                    'Mean': times.mean(),
                    'Std Dev': times.std()
                })

    if not stats_data:
        print("No valid time data available")
        return

    # Create DataFrame for the table
    stats_df = pd.DataFrame(stats_data)

    # Round all numeric columns to 2 decimal places
    stats_df = stats_df.round(2)

    # Create figure
    plt.figure(figsize=(10, 4))
    ax = plt.subplot(111, frame_on=False)
    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)

    # Create table
    table = plt.table(
        cellText=stats_df.values,
        colLabels=stats_df.columns,
        loc='center',
        cellLoc='center',
        colColours=['#f3f3f3'] * len(stats_df.columns)
    )

    # Style table
    table.auto_set_font_size(False)
    table.set_fontsize(12)
    table.scale(1.2, 1.5)  # Adjust cell sizes

    # Title
    plt.title('Level Completion Time Statistics',
              fontsize=14, pad=20, fontweight='bold')

    plt.tight_layout()
    save_plot('time_stats_table.png')


def plot_correlation_matrix():
    df = load_game_data()
    if df.empty:
        return

    # Select and clean our metrics
    metrics = df[['levels_completed', 'total_score',
                  'ghosts_defeated', 'time_taken']].copy()

    # Convert to numeric and filter invalid values
    for col in metrics.columns:
        metrics[col] = pd.to_numeric(metrics[col], errors='coerce')
    metrics = metrics.dropna()
    metrics = metrics[(metrics > 0).all(axis=1)]  # Remove zeros/negatives

    if metrics.empty:
        print("No valid data for correlation matrix")
        return

    # Calculate correlations
    corr = metrics.corr()

    # Create heatmap
    plt.figure(figsize=(10, 8))
    sns.heatmap(
        corr,
        annot=True,  # Show correlation values
        fmt=".2f",  # 2 decimal places
        cmap="coolwarm",  # Blue(-) to Red(+) colors
        vmin=-1, vmax=1,  # Fix color scale
        square=True,  # Square cells
        linewidths=.5,  # Grid lines
        cbar_kws={"shrink": 0.8}  # Color bar size
    )

    # Customize plot
    plt.title("Game Metrics Correlation Matrix",
              fontsize=16, pad=20, fontweight='bold')
    plt.xticks(fontsize=12, rotation=45)
    plt.yticks(fontsize=12, rotation=0)

    plt.tight_layout()
    save_plot('correlation_matrix.png')


def load_game_data():
    """Robust data loading with error handling"""
    try:
        df = pd.read_csv('data/game_data.csv')
        df.columns = [col.strip().lower().replace(' ', '_') for col in df.columns]
        return df
    except Exception as e:
        print(f"Error loading data: {e}")
        return pd.DataFrame()


def save_plot(filename):
    """Save plot with directory creation"""
    os.makedirs('data/stats', exist_ok=True)
    plt.savefig(f'data/stats/{filename}')
    plt.close()


if __name__ == "__main__":
    print("Generating game statistics graphs...")
    generate_all_stats()
    print("Graph generation complete!")


def load_game_data():
    """Load and clean game data with error handling for malformed rows"""
    try:
        # First try normal reading
        try:
            df = pd.read_csv('data/game_data.csv')
        except pd.errors.ParserError:
            # If normal reading fails, try with error_bad_lines=False to skip bad lines
            df = pd.read_csv('data/game_data.csv', error_bad_lines=False)

        # Clean column names
        if not df.empty:
            df.columns = [str(c).lower().replace(' ', '_') for c in df.columns]
        return df
    except Exception as e:
        print(f"Error loading game data: {e}")
        return pd.DataFrame()


def save_plot(filename):
    """Save plot to stats directory"""
    os.makedirs('data/stats', exist_ok=True)
    path = f'data/stats/{filename}'
    plt.savefig(path)
    plt.close()
    print(f"Saved: {path}")


def find_bad_line():
    """Helper function to identify the exact problematic line"""
    with open('data/game_data.csv', 'r') as f:
        for i, line in enumerate(f, 1):
            if line.count(',') > 8:  # More commas than expected columns
                print(f"Problematic line {i}: {line.strip()}")
                return i
    return None


if __name__ == "__main__":
    bad_line = find_bad_line()
    if bad_line:
        print(f"\nFound problematic data at line {bad_line}")
        print("Please check this line in your CSV file for extra commas or formatting issues.")
    else:
        print("Generating game statistics graphs...")
        generate_all_stats()
        print("Graph generation complete!")


def show_sample_data():
    """Show first few rows of the CSV"""
    try:
        with open('data/game_data.csv', 'r') as f:
            print("\nFirst 5 lines of CSV:")
            for i, line in enumerate(f, 1):
                if i <= 5:
                    print(f"{i}: {line.strip()}")
                else:
                    break
    except Exception as e:
        print(f"Couldn't read CSV: {e}")


if __name__ == "__main__":
    show_sample_data()
    bad_line = find_bad_line()
    print("Generating game statistics graphs...")
    generate_all_stats()
    print("Graph generation complete!")
