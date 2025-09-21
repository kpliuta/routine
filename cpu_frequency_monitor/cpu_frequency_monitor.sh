#!/bin/sh

# ======================================================================================================================
#
#         USAGE:  ./cpu_frequency_monitor.sh
#
#   DESCRIPTION:  Monitors and displays the current and maximum CPU frequency for each core.
#                 The output is formatted for the XFCE Generic Monitor panel applet, using newline characters (\n).
#                 It can be configured to hide the CPU number, hide the maximum frequency, and set the number of CPUs per row.
#
#       EXAMPLE:  To use with XFCE's Generic Monitor, set this script as the command.
#                 With default settings, the output will be something like:
#                 <txt><b>0</b>:2.40GHz/3.50GHz, <b>1</b>:2.40GHz/3.50GHz
#                 <b>2</b>:2.40GHz/3.50GHz, <b>3</b>:2.40GHz/3.50GHz</txt>
#
# ======================================================================================================================

# --- CONFIGURATION ---

# CPUS_PER_ROW: Number of CPU cores to display per line.
# Adjust this value to fit your panel's width.
CPUS_PER_ROW=2

# SHOW_CPU_NUM: Set to "true" to display the core number (e.g., "<b>0</b>:2.40GHz"), or "false" to hide it (e.g., "2.40GHz").
SHOW_CPU_NUM=false

# SHOW_MAX_FREQ: Set to "true" to display max frequency (e.g., "2.40GHz/3.50GHz"), or "false" to hide it (e.g., "2.40GHz").
SHOW_MAX_FREQ=false

# --- SCRIPT ---

# Inform the user that the script is running. Output to stderr to not interfere with panel output.
echo "Gathering CPU frequency data..." >&2

# Find all CPU directories.
cpu_dirs=$(find /sys/devices/system/cpu/ -maxdepth 1 -type d -name "cpu[0-9]*" | sort -V)

if [ -z "$cpu_dirs" ]; then
    echo "<txt>Error: CPU freq info not found.</txt>"
    echo "Could not find CPU frequency information in /sys/devices/system/cpu/" >&2
    exit 1
fi

output_lines=""
line=""
count=0

# Iterate over each CPU core directory.
for cpu_dir in $cpu_dirs; do
    # Get the CPU core number from the directory path.
    cpu_num=$(echo "$cpu_dir" | grep -o '[0-9]*$')

    # --- Frequency Information ---

    cur_freq_path="$cpu_dir/cpufreq/scaling_cur_freq"
    max_freq_path="$cpu_dir/cpufreq/cpuinfo_max_freq"

    # Skip core if frequency information is not available.
    if [ ! -f "$cur_freq_path" ] || [ ! -f "$max_freq_path" ]; then
        continue
    fi

    # Get the current and maximum frequencies for the core (in KHz).
    cur_freq_khz=$(cat "$cur_freq_path")
    max_freq_khz=$(cat "$max_freq_path")

    # Convert current frequency to GHz.
    cur_freq_ghz=$(awk "BEGIN {printf \"%.2f\", $cur_freq_khz / 1000000}")

    # --- Format Output String ---

    # Determine the prefix (CPU number)
    cpu_prefix=""
    if [ "$SHOW_CPU_NUM" = "true" ]; then
        cpu_prefix="<b>${cpu_num}</b>:"
    fi

    # Determine the suffix (max frequency)
    freq_suffix=""
    if [ "$SHOW_MAX_FREQ" = "true" ]; then
        max_freq_ghz=$(awk "BEGIN {printf \"%.2f\", $max_freq_khz / 1000000}")
        freq_suffix="/${max_freq_ghz}GHz"
    fi

    # Combine all parts for the core's output
    core_output="${cpu_prefix}${cur_freq_ghz}GHz${freq_suffix}"

    # Build the line of output.
    if [ -n "$line" ]; then
        line="$line "
    fi
    line="$line$core_output"
    count=$((count + 1))

    # If the line is full, add it to the output and reset.
    if [ "$count" -eq "$CPUS_PER_ROW" ]; then
        if [ -n "$output_lines" ]; then
            output_lines="$output_lines\n$line"
        else
            output_lines="$line"
        fi
        line=""
        count=0
    fi
done

# Add any remaining part of a line to the output.
if [ -n "$line" ]; then
    if [ -n "$output_lines" ]; then
        output_lines="$output_lines\n$line"
    else
        output_lines="$line"
    fi
fi

# Print the final formatted output for the Generic Monitor.
# The -e flag for echo enables interpretation of backslash escapes (like \n).
# shellcheck disable=SC3037
echo -e "<txt>$output_lines</txt>"

# Inform the user that the script has finished.
echo "Done." >&2
