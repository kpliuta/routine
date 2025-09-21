# CPU Frequency Monitor for XFCE Panel

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A simple, lightweight, and customizable shell script to display real-time CPU core frequencies on your XFCE panel using the Generic Monitor applet.

---

## Preview

2 CPU in a row, **with** core number and max frequency displayed:

<img width="539" height="83" src="https://github.com/user-attachments/assets/3e11d18b-281c-4f8c-b52d-b74f9b15db79" />

2 CPU in a row, **without** core number and max frequency displayed:

<img width="428" height="66" src="https://github.com/user-attachments/assets/e7d4c6ea-e1f0-4d3f-b857-d40f0c36c861" />

---

## Prerequisites

Before you begin, ensure you have the following:

- A Linux system where CPU frequency information is available in `/sys/devices/system/cpu/`.
- **XFCE Desktop Environment**.
- The **Generic Monitor (genmon)** applet. If you don't have it, you can usually install it through your distribution's package manager (e.g., `sudo apt-get install xfce4-genmon-plugin`).

---

## Installation & Usage

Setting up the monitor is straightforward. Follow these steps:

1.  **Make the script executable:**
    Open a terminal in the project directory and run:
    ```sh
    chmod +x cpu_frequency_monitor.sh
    ```

2.  **Add the Generic Monitor to your panel:**
    - Right-click your XFCE panel and navigate to `Panel` > `Add New Items`.
    - Find "Generic Monitor" in the list and click `Add`.
    - A new monitor will appear on your panel.

3.  **Configure the Generic Monitor:**
    - Right-click the new monitor on your panel and select `Properties`.
    - In the **Command** field, enter the **absolute path** to the `cpu_frequency_monitor.sh` script.
    - **Uncheck** the `Use label` checkbox.
    - Set the **Period (s)** to your desired refresh rate (e.g., `2` seconds).
    - Close the properties window. The monitor will now display your CPU frequencies.

---

## Configuration

You can customize the script's output by editing the configuration variables at the top of the `cpu_frequency_monitor.sh` file.

```sh
# --- CONFIGURATION ---

# CPUS_PER_ROW: Number of CPU cores to display per line.
CPUS_PER_ROW=2

# SHOW_CPU_NUM: Set to "true" to display the core number, or "false" to hide it.
SHOW_CPU_NUM=true

# SHOW_MAX_FREQ: Set to "true" to display max frequency, or "false" to hide it.
SHOW_MAX_FREQ=true
```

- `CPUS_PER_ROW`: An integer that controls how many CPU outputs are grouped on a single line.
- `SHOW_CPU_NUM`: A boolean (`true` or `false`) that toggles the display of the CPU core number and its following colon.
- `SHOW_MAX_FREQ`: A boolean (`true` or `false`) that toggles the display of the maximum possible frequency for each core.

---

## Contributing

Contributions are welcome! If you have an idea for an improvement or have found a bug, please feel free to open an issue or submit a pull request.

---

## License

Distributed under the MIT License.
