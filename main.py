import shutil
from pathlib import Path
import argparse

import numpy as np
import pandas as pd
from ska_ost_array_config.array_config import LowSubArray


def apply_rotation(low_array_file: str, station_name: str) -> tuple[np.ndarray, float]:
    low_array_data = pd.read_csv(low_array_file, skiprows=21)
    s81_spec = low_array_data[low_array_data["label"] == "S8-1"]
    s81_rot = s81_spec["rotation"].values[0]

    after_rot = []
    if station_name == "S8-1":
        after_rot = np.loadtxt("./s8-1.txt", delimiter=",")[:, 0:2]
        station_rot = 251.3
    else:
        station_spec = low_array_data[low_array_data["label"] == station_name]
        station_rot = station_spec["rotation"].values[0]

        # Calculate rotation angle relative to s8-1 rotation
        # NOTE: Rotation angles given in degrees East of North (clockwise)
        rot_angle_deg = s81_rot - station_rot

        # Convert to radians
        rot_angle = rot_angle_deg * np.pi / 180.0

        rot_mat = np.array(
            [
                [np.cos(rot_angle), -np.sin(rot_angle)],
                [np.sin(rot_angle), np.cos(rot_angle)],
            ]
        )

        # Coordinates of the antennas before rotation
        before_rot = np.loadtxt("./s8-1.txt", delimiter=",")[:, 0:2]

        after_rot = np.dot(before_rot, rot_mat.T)

    return after_rot, station_rot


def input_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    _ = parser.add_argument(
        "--no-rot", help="Do not rotate stations or feed elements", action="store_true"
    )
    _ = parser.add_argument(
        "--no-feed-rot",
        help="Do not rotate feed elements, but do rotate stations",
        action="store_true",
    )
    _ = parser.add_argument(
        "telescope_str",
        help="Accepts any of these values: AA0.5, AA1, AA2, AAstar, AA4",
        type=str,
    )
    args = parser.parse_args()

    acceptable_strings = ["AA0.5", "AA1", "AA2", "AAstar", "AA4"]
    if args.telescope_str not in acceptable_strings:
        print("Accepted telescope models: AA0.5, AA1, AA2, AAstar, AA4")
        raise SystemExit(1)

    if args.no_rot and args.no_feed_rot:  # noqa: F821
        print("Choose either no rotation at all or no feed rotation")
        raise SystemExit(1)

    print(
        f"Input settings:\nTelescope: {args.telescope_str}\nDisable all rotation: {args.no_rot}\nDisable feed rotation: {args.no_feed_rot}"
    )
    return args


def main():
    args = input_arguments()
    # Load this file for the rotation information for each station
    low_array_file = "./low_array_coords.dat"

    # Create output directory
    telescope_str = args.telescope_str

    if args.no_rot:
        output_dir = f"telescope_model_{telescope_str}_no_rot"
    elif args.no_feed_rot:
        output_dir = f"telescope_model_{telescope_str}_no_feed_rot"
    else:
        output_dir = f"telescope_model_{telescope_str}"

    if Path(output_dir).exists() and Path(output_dir).is_dir():
        shutil.rmtree(output_dir)

    Path.mkdir(Path(output_dir))

    # Select SKA-Low telescope subarray
    if telescope_str == "AAstar":
        telescope_str = "AA*"
    telescope = LowSubArray(subarray_type=telescope_str)

    # Save telescope centre in WGS84 coordinates into "position.txt"
    coordinates = telescope.array_config.location.to_geodetic(ellipsoid="WGS84")
    with open(f"{output_dir}/position.txt", "x") as f:
        f.write(f"{coordinates.lon.degree}, {coordinates.lat.degree}")

    # Save telescope station coordinates into "layout.txt"
    # NOTE: Some code borrowed from the ska_ost_array_config project
    n_stations = telescope.array_config.names.data.shape[0]
    with open(f"{output_dir}/layout.txt", "x") as f:
        for i in range(n_stations):
            f.write(
                f"{telescope.array_config.xyz.data[i][1]}, {telescope.array_config.xyz.data[i][0]}, {telescope.array_config.xyz.data[i][2]}\n"
            )

    # Go through each station and apply correct rotation then save antenna coordinates
    for i in range(n_stations):
        Path.mkdir(Path(f"{output_dir}/station{i:03d}"))

        # Get name of station
        station_name = telescope.array_config.names.data[i]
        print(f"{i} {station_name}")

        # Apply rotation relative to s8-1, returned rotation is angles EAST OF NORTH
        # but the "Feed Element Rotation" setting in OKSAR expects counter-clockwise angles from the positive x-axis (I'm pretty sure)
        if args.no_rot:  # Do not apply rotation, therefore pass in S8-1 since every station starts off at S8-1
            ant_coords, rotation = apply_rotation(low_array_file, "S8-1")
        else:
            ant_coords, rotation = apply_rotation(low_array_file, station_name)
            euler_angle = (90 - rotation) % 360

        # euler_angle = 45 # Test feed angle, output beam should be have sidelobes at 45/135 degrees

        # Save antenna coordinates
        with open(f"{output_dir}/station{i:03d}/layout.txt", "x") as f:
            for row in ant_coords:
                f.write(f"{row[0]:.5f}, {row[1]:.5f}\n")

        # Save rotation to antennas
        if not (args.no_rot or args.no_feed_rot):
            with open(f"{output_dir}/station{i:03d}/feed_angle.txt", "x") as f:
                for i, _ in enumerate(ant_coords):
                    f.write(f"{euler_angle:.5f}\n")


if __name__ == "__main__":
    main()
