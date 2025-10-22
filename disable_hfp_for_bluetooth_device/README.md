# Disable HFP for a Bluetooth Device

## Description

This guide provides instructions on how to manually disable the Hands-Free Profile (HFP) for a specific Bluetooth device on a Linux system using `bluez` and `pulseaudio`.

This is sometimes necessary for devices that do not allow for on-the-fly profile switching, or default to a lower-quality audio profile. For example, with the Shure RMCE-TW2 wireless adapters, it is not possible to switch from HFP to the high-fidelity A2DP profile automatically. By disabling HFP, you force the system to use the A2DP profile, ensuring the best possible audio quality.

## Instructions

1.  **Get the Bluetooth MAC address of your device.**

    You can list all paired devices and find the MAC address of your target device with the following command:

    ```bash
    bluetoothctl devices
    ```

    You will also need your Bluetooth adapter's MAC address, which you can typically find in your system's Bluetooth settings or via command-line tools.

2.  **Open the PulseAudio Bluetooth configuration file.**

    The configuration file is located in `/var/lib/bluetooth/`. You will need to replace `<your_adapter_mac>` and `<device_mac>` with the appropriate addresses.

    ```bash
    sudo vim /var/lib/bluetooth/<your_adapter_mac>/<device_mac>/info
    ```

3.  **Force A2DP by disabling HFP.**

    Add the following lines to the `info` file under the `[General]` section. If the `[General]` section doesn't exist, create it.

    ```ini
    [General]
    DisableHandsfree = true
    ```

4.  **Save the file and restart Bluetooth services.**

    Save the changes to the `info` file. Then, restart the Bluetooth service and PulseAudio.

    ```bash
    sudo systemctl restart bluetooth
    pulseaudio --kill && pulseaudio --start
    ```

Your device should now connect using the A2DP profile automatically.
