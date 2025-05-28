import os

import matplotlib.pyplot as plt
import numpy as np


def plot_station_samples(
    root_dir, reference_station=None, include_stations=None, num_stations=15, step=20
):
    """
    Plot multiple station subplots with options for a reference station and specific stations to include.

    Parameters:
    - root_dir: Directory containing the substations.txt file and station subdirectories
    - reference_station: Name of a station to overlay in all subplots (optional)
    - include_stations: List of specific station names to include in the plots (optional)
    - num_stations: Number of stations to plot (not including reference or included stations)
    - step: Sampling interval for regular station selection
    """
    # Read substation coordinates
    substation_file = os.path.join(root_dir, "layout.txt")
    subdirs = [
        d for d in os.listdir(root_dir) if os.path.isdir(os.path.join(root_dir, d))
    ]

    # Read all substation coordinates at once
    substation_coords = np.loadtxt(substation_file, delimiter=",")

    # Create a mapping of station names to their coordinates
    station_to_coords = {
        subdirs[i]: substation_coords[i]
        for i in range(min(len(subdirs), len(substation_coords)))
    }

    # Load reference station data if specified
    reference_data = None
    if reference_station and reference_station in station_to_coords:
        ref_file = os.path.join(
            root_dir,
            reference_station,
            [
                f
                for f in os.listdir(os.path.join(root_dir, reference_station))
                if f.endswith(".txt")
            ][0],
        )
        try:
            reference_data = np.loadtxt(ref_file, delimiter=",")
        except Exception as e:
            print(f"Error loading reference station {reference_station}: {e}")

    # Determine which stations to plot
    stations_to_plot = []

    # Add explicitly included stations first
    if include_stations:
        for station in include_stations:
            if station in station_to_coords and station != reference_station:
                stations_to_plot.append(station)

    # Then add regularly sampled stations
    remaining_slots = num_stations - len(stations_to_plot)
    if remaining_slots > 0:
        # Filter out reference and already included stations
        available_stations = [
            s for s in subdirs if s not in stations_to_plot and s != reference_station
        ]
        # Select at regular intervals
        selected_indices = np.linspace(
            0, len(available_stations) - 1, remaining_slots, dtype=int
        )
        stations_to_plot.extend([available_stations[i] for i in selected_indices])

    # Calculate grid dimensions for subplots
    total_plots = len(stations_to_plot)
    grid_size = int(np.ceil(np.sqrt(total_plots)))

    # Create figure with subplots
    fig, axes = plt.subplots(grid_size, grid_size, figsize=(15, 15))
    if grid_size == 1:
        axes = np.array([axes])  # Handle single subplot case
    axes = axes.flatten()  # Flatten to make indexing easier

    # For each selected station
    for plot_idx, station_name in enumerate(stations_to_plot):
        if plot_idx < len(axes):
            ax = axes[plot_idx]

            # Get station info
            station_x, station_y, _ = station_to_coords[station_name]

            # Read antenna data
            antenna_dir = os.path.join(root_dir, station_name)
            antenna_files = [f for f in os.listdir(antenna_dir) if f.endswith(".txt")]

            if antenna_files:
                antenna_file_path = os.path.join(antenna_dir, antenna_files[0])

                try:
                    # Load antenna coordinates
                    antenna_coords = np.loadtxt(antenna_file_path, delimiter=",")

                    # Plot the station in the center
                    ax.scatter(0, 0, color="blue", s=100, marker="s", label="Station")

                    # Plot antennas relative to station (at origin)
                    ax.scatter(
                        antenna_coords[:, 0],
                        antenna_coords[:, 1],
                        color="red",
                        s=5,
                        marker="^",
                        alpha=0.5,
                        label="Antennas",
                    )

                    # Plot reference station antennas if specified
                    if reference_data is not None:
                        ax.scatter(
                            reference_data[:, 0],
                            reference_data[:, 1],
                            color="green",
                            s=5,
                            marker="o",
                            alpha=0.3,
                            label=f"Ref: {reference_station}",
                        )

                    # Set plot properties
                    ax.set_title(f"Station {station_name}", fontsize=10)
                    ax.set_xlim(-20, 20)  # Adjust limits as needed for your data
                    ax.set_ylim(-20, 20)
                    ax.grid(True, linestyle="--", alpha=0.3)

                    # Add legend to first plot only
                    if plot_idx == 0:
                        ax.legend(loc="upper right", fontsize=8)

                except Exception as e:
                    ax.text(
                        0.5,
                        0.5,
                        f"Error: {e}",
                        ha="center",
                        va="center",
                        transform=ax.transAxes,
                    )
            else:
                ax.text(
                    0.5,
                    0.5,
                    "No antenna data",
                    ha="center",
                    va="center",
                    transform=ax.transAxes,
                )

    # Hide any unused subplots
    for i in range(len(stations_to_plot), len(axes)):
        axes[i].set_visible(False)

    # Add overall title and adjust layout
    title = f"Sample of {len(stations_to_plot)} Stations"
    if reference_station:
        title += f" with Reference Station {reference_station}"
    if include_stations:
        title += (
            f' (Including {", ".join(include_stations[:3])}'
            + (
                f"and {len(include_stations)-3} more"
                if len(include_stations) > 3
                else ""
            )
            + ")"
        )

    plt.suptitle(title, fontsize=16, y=0.98)
    plt.tight_layout(rect=[0, 0, 1, 0.96])  # Adjust for suptitle
    plt.show()


# Example usage
plot_station_samples(
    "./telescope_model",
    reference_station="station297",  # Optional: station to overlay on all plots
    include_stations=[
        "station025",
        "station134",
    ],  # Optional: specific stations to include
    num_stations=15,  # Total stations to plot (including specifically included ones)
    step=20,  # Sampling step for remaining slots
)
