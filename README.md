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

### Citation
If you use this code in your research, please cite the following papers:

1. Resilience of space information network based on combination of complex networks and hypergraphs[J]. Computer Communications, 2022, 195: 124-136.
2. Resilience enhancement scheme for gateway placement in space information networks[J]. Computer Networks, 2023, 222: 109555.
3. Modeling and Analysis of Cascading Failures in LEO Satellite Networks[J]. IEEE Transactions on Network Science and Engineering, 2024, 11(1): 807-822.
4. Distributed Anti-Cascading Routing Scheme Based on Fuzzy Logic in LEO Satellite Networks. IEEE Transactions on Vehicular Technology.
5. A Dynamic Cascading Failure Model for LEO Satellite Networks[J]. IEEE Transactions on Network and Service Management, 2024, 21(2): 1672-1689.
6. Cascading failure model and resilience enhancement scheme of space information networks[J]. Reliability Engineering & System Safety, 2023, 237: 109379.
7. Rapid cascading risk assessment and vulnerable satellite identification schemes for LEO satellite networks[J]. Reliability Engineering & System Safety, 2024, 110699.
8. UAV-Enabled IoT: Cascading Failure Model and Topology-Control-Based Recovery Scheme[J]. IEEE Internet of Things Journal, 2024, 11(12): 22562-22577.

