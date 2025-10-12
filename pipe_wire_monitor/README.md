# PipeWire Monitor for XFCE Panel

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python script for the XFCE Generic Monitor applet to ensure bit-perfect audio playback by monitoring and comparing the sample rates of a source and a sink in PipeWire.

## Key Features

- **Sample Rate Matching**: Verifies that the output device's sample rate matches the source's sample rate.
- **Volume Monitoring**: Checks that both the source and output device volumes are set to 100% to prevent software volume control.
- **Idle and Error States**: Provides clear feedback for various states, including idle, multiple sources, or configuration errors.
- **XFCE Panel Integration**: Designed to be used with the Generic Monitor applet in the XFCE panel for at-a-glance status updates.

## Why It's Important

Modern high-end DACs (Digital-to-Analog Converters) are designed to handle the digital-to-analog conversion as accurately as possible. However, audio quality can be compromised by software-level processing, such as sample rate conversion and volume adjustments.

- **Sample Rate Conversion**: When the sample rate of the source material (e.g., a 44.1kHz FLAC file) does not match the sample rate of the audio device, the operating system's audio server (like PipeWire) must resample the audio in real-time. This process can introduce audible artifacts and degrade the listening experience.
- **Software Volume Control**: Adjusting volume at the software level modifies the digital audio data before it reaches the DAC. This can reduce the signal's dynamic range. For the best quality, volume should be controlled by the analog amplifier after the DAC.

This script helps audiophiles maintain a bit-perfect audio chain by providing a visual indicator of whether the digital signal is being altered. Manually checking parameters with tools like `pw-top` is cumbersome, but this script automates the monitoring process.

## Preview

Here are the possible outputs you will see in the XFCE panel. Detailed logs for each status can be found in the tooltip of the applet.

- **`N/A`**: The target audio device was not found:
<img width="650" height="120" alt="image" src="https://github.com/user-attachments/assets/bd5c6fea-6d49-4aaf-823a-969326751b5d" />

- **`Idle`**: No active audio source is detected:
<img width="650" height="175" alt="image" src="https://github.com/user-attachments/assets/c84ff7c8-ccfa-46d1-b0a4-38938e40f628" />

- **`48000`**: An active source is playing at 48000 Hz, and the device is set to the same rate:
<img width="650" height="209" alt="image" src="https://github.com/user-attachments/assets/ded6307a-8480-4929-b874-38bc51eafa74" />

- **`Freq Err`**: The source and device sample rates do not match:
<img width="650" height="230" alt="image" src="https://github.com/user-attachments/assets/407263fc-6e32-40bf-8e56-a930b5731ffe" />

- **`Vol Err`**: The volume of either the source or the device is not at 100%:
<img width="650" height="206" alt="image" src="https://github.com/user-attachments/assets/da3ef0dd-5633-43a6-bdcb-d3e671b32c40" />

- **`Src Err`**: More than one audio source is active, making it impossible to guarantee a bit-perfect stream:
<img width="650" height="179" alt="image" src="https://github.com/user-attachments/assets/a987542a-e019-40ec-966a-c0fdc0c1868c" />

- **`Err`**: A script error occurred, likely related to `pw-dump`:
<img width="650" height="102" alt="image" src="https://github.com/user-attachments/assets/f22c345c-9453-46b8-bdec-444a067a2e70" />


## Usage with XFCE Generic Monitor

1.  Add the "Generic Monitor" applet to your XFCE panel.
2.  In the applet's properties, set the command to:
    ```bash
    python /path/to/pipe_wire_monitor.py "My DAC"
    ```
    Replace `"My DAC"` with a unique part of your audio device's name as it appears in `pw-top`.
3.  Set the period (e.g., 1-2 seconds).

## How to Lock Sample Rate in PipeWire

To prevent PipeWire from automatically changing the sample rate of your device, you can lock it. This is useful for DACs that have a fixed set of supported sample rates.

1.  Find your device's name by running `pw-top` or `pactl list sinks`.
2.  Create a configuration file in `~/.config/pipewire/pipewire.conf.d/` (e.g., `99-my-dac-rates.conf`).
3.  Add the following content, replacing `"My DAC"` with your device's name and `48000` with your desired sample rate:

    ```
    context.properties = {
        "default.clock.rate" = 48000
    }

    context.modules = [
        {
            name = "libpipewire-module-adapter"
            args = {
                "node.name" = "My DAC"
                "audio.rate" = 48000
            }
        }
    ]
    ```

4.  Restart PipeWire:
    ```bash
    systemctl --user restart pipewire pipewire-pulse wireplumber
    ```

## Contributing

Contributions are welcome! If you have an idea for an improvement or have found a bug, please feel free to open an issue or submit a pull request.

## License

Distributed under the MIT License.
