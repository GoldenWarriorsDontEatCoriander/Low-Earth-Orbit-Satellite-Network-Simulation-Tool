# Low-Earth-Orbit-Satellite-Network-Simulation-Tool

An open-source Low Earth Orbit (LEO) satellite network simulation tool designed to simulate satellite network functions, including real-time satellite operation visualization, satellite-to-ground data transmission, and inter-satellite link transmission. It provides a platform for researchers and developers to simulate and analyze LEO satellite networks.

## Directory Structure

- `src/`: Directory containing the source code.
- `resource/`: Directory for storing resources.
- `config/`: Directory for configuration files.
- `tests/`: Directory for test files.

## Installation & Usage

### Installation

1. Clone the project to your local machine:

    ```bash
    git clone https://github.com/GoldenWarriorsDontEatCoriander/Low-Earth-Orbit-Satellite-Network-Simulation-Tool.git
    ```

2. Navigate to the project directory:

    ```bash
    cd Low-Earth-Orbit-Satellite-Network-Simulation-Tool
    ```

3. Open the Command Prompt (CMD) or PowerShell and Install dependenciesusing `pip`:


### Usage

1. Run the `main.py` script located in the `src` folder to start the simulation. The default port is set to 8080:

    Open the Command Prompt or PowerShell in the `src` directory and run:

    ```bash
    python main.py
    ```

2. To view the satellite constellation in 3D, open the `src/visualization/constellation_3d.html` file in any modern web browser.

3. The `config/config.ini` file allows you to adjust various parameters, such as constellation, satellite, user, environmental, time, and web server settings.


