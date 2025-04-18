# Space Debris Tracker

## Introduction

This repository contains a Python script that tracks space debris using the TLE (Two-Line Element) format. The script fetches TLE data from CelesTrak, calculates the position of space debris, and visualizes it on a map using Folium.

## Requirements

- Python 3.x
- `requests` library for fetching TLE data
- `numpy` library for numerical calculations
- `skyfield` library for satellite tracking
- `matplotlib` library for plotting graphs
- `datetime` library for date and time manipulation
- `pyserial` library for serial communication
- `packaging` library for version handling

## Hardware Requirements

- Arduino Uno
- GPS Module (e.g., Neo-6M GPS Module)

## Installation

- Clone the github repo
```git clone https://github.com/kareem1207/Space-Debris-Tracker.git```

- run following commands in the terminal to install the required libraries

```bash
cd Space-Debris-Tracker
pip install -r requirements.txt
python main.py
```

## Contributions

- Fork the project and follow the Installation steps.
- Contributions are open any contribution towards the progress of project is appreciated.

### Output and hardware setup images

#### Hardware Setup

![Hardware Setup Image](./Hardware1.jpg)

### Output

![Output Image](./output.jpg)
