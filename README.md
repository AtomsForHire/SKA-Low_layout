# SKA-Low_layout
Simple script that grabs SKA-Low telescope layout from ska_ost_array_config,
station layout from a file of s8-1, and rotation information in
low_array_coords.dat. Applies rotations relative to the s8-1 station.

# Installation
You will first need to install [ska ost array
config](https://gitlab.com/ska-telescope/ost/ska-ost-array-config).


# Usage

Simply run `python3 main.py -h` to print out the help menu.

```
$ python3 main.py -h
usage: main.py [-h] [--no-rot] [--no-feed-rot] telescope_str

positional arguments:
  telescope_str  Accepts any of these values: AA0.5, AA1, AA2, AAstar, AA4
```

`--no-rot` disables rotation for both stations and antennas, which means all
stations are identical to S8-1.

`--no-feed-rot` disables rotation for only antennas, this means stations are
*not* identical.

Examples
To create an AAstar layout with identical stations you would run:
```
python3 main.py AAstar --no-rot
```

To create an AA2 layout with everything rotated:
```
python3 main.py AA2
```

To create an AA4 layout with all antennas not-rotated
```
python3 main.py AA4 --no-feed-rot
```
