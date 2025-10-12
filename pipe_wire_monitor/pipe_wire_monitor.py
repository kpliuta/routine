import io
import json
import subprocess
import sys
from typing import Any, Dict, List, Optional


class PipeWireGraph:
    """A structured representation of the PipeWire graph for easier querying."""

    def __init__(self, graph_data: List[Dict[str, Any]]):
        self.nodes: Dict[int, Dict[str, Any]] = {
            item["id"]: item for item in graph_data if "Node" in item.get("type", "")
        }
        self.links: Dict[int, Dict[str, Any]] = {
            item["id"]: item for item in graph_data if "Link" in item.get("type", "")
        }


class PipeWireMonitor:
    """Monitors a PipeWire audio device for property consistency with its sources."""

    def __init__(self, target_device_substring: str):
        """
        Initializes the PipeWireMonitor.

        Args:
            target_device_substring: A substring of the target audio device name to monitor.
        """
        self.target_device_substring = target_device_substring
        self.log_buffer = io.StringIO()

    def _log(self, message: str):
        """Logs a message to stderr and an internal buffer for the tooltip."""
        print(message, file=sys.stderr)
        self.log_buffer.write(message + "\n")

    def _format_output(self, status_text: str) -> str:
        """Formats the final output string with the status and a tooltip."""
        tooltip_text = self.log_buffer.getvalue().strip()
        # Escape special XML characters for the tooltip.
        tooltip_text = tooltip_text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        return f"{status_text}<tool>{tooltip_text}</tool>"

    def _get_pipewire_graph(self) -> Optional[List[Dict[str, Any]]]:
        """
        Dumps the PipeWire graph as a JSON object.

        Returns:
            A list of dictionaries representing the PipeWire graph, or None on error.
        """
        self._log(f"-> Running 'pw-dump' to get PipeWire graph state...")
        try:
            result = subprocess.run(
                ["pw-dump"],
                capture_output=True,
                text=True,
                check=True,
            )
            return json.loads(result.stdout)
        except Exception as e:
            self._log(f"Error getting or parsing PipeWire graph: {e}")
            return None

    def _find_node_by_name(self, graph: PipeWireGraph, name: str) -> Optional[Dict[str, Any]]:
        """
        Finds a node in the PipeWire graph where 'node.name' contains the given name string.

        Args:
            graph: The PipeWireGraph object to search within.
            name: A substring of the 'node.name' to search for.

        Returns:
            The node dictionary if found, otherwise None.
        """
        for node in graph.nodes.values():
            if name in node.get("info", {}).get("props", {}).get("node.name", ""):
                return node
        return None

    def _get_node_sample_rate(self, node: Dict[str, Any]) -> Optional[int]:
        """
        Extracts the current sample rate from a node object.

        Args:
            node: The node dictionary.

        Returns:
            The sample rate as an integer, or None if not available.
        """
        params = node.get("info", {}).get("params", {})

        def _extract_rate_from_value(value: Any) -> Optional[int]:
            """Helper to get rate, handling if it's a dict or a direct int."""
            if isinstance(value, dict):
                # If rate is a dict like {'default': 48000, ...}, use the default.
                return value.get("default")
            if isinstance(value, int):
                return value
            return None

        # First, try to get the *active* format from the 'Format' parameter.
        # This is usually present when the device is actively playing audio.
        if "Format" in params and params["Format"]:
            format_info = params["Format"][0]
            # Case 1: Rate is nested under an 'audio' key.
            if "audio" in format_info:
                return _extract_rate_from_value(format_info.get("audio", {}).get("rate"))
            # Case 2: Rate is a direct key in the format info (e.g., for some BT devices).
            return _extract_rate_from_value(format_info.get("rate"))

        # Fallback: If 'Format' is empty (e.g., device is idle/suspended),
        # check the *available* formats in 'EnumFormat'. We'll use the first one.
        if "EnumFormat" in params and params["EnumFormat"]:
            return _extract_rate_from_value(params["EnumFormat"][0].get("rate"))

        return None

    def _get_connected_source_nodes(self, graph: PipeWireGraph, target_node_id: int) -> List[Dict[str, Any]]:
        """
        Finds all source nodes that are actively linked to the target device.

        Args:
            graph: The PipeWireGraph object to search within.
            target_node_id: The integer ID of the target device node.

        Returns:
            A list of node dictionaries for the connected sources.
        """
        source_node_ids = set()
        for link in graph.links.values():
            info = link.get("info", {})
            if info.get("input-node-id") == target_node_id:
                source_node_ids.add(info.get("output-node-id"))

        source_nodes = [
            graph.nodes[node_id]
            for node_id in source_node_ids
            if node_id in graph.nodes
        ]
        return source_nodes

    def _filter_sources(self, source_nodes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filters out source nodes that are not in a 'running' state.

        Args:
            source_nodes: A list of source node dictionaries.

        Returns:
            A filtered list of source node dictionaries.
        """
        filtered_nodes = []
        for node in source_nodes:
            info = node.get("info", {})
            props = info.get("props", {})
            state = info.get("state")

            log_name = self._get_node_descriptive_name(node)

            # Filter out sources that are not actively running.
            if state != "running":
                self._log(f"-> Filtering out non-running source: {log_name} (state: {state})")
            else:
                filtered_nodes.append(node)

        return filtered_nodes

    def _get_node_descriptive_name(self, node: Dict[str, Any]) -> str:
        """Gets a descriptive name for a node, preferring user-friendly names."""
        props = node.get("info", {}).get("props", {})
        return (
                props.get("node.description")
                or props.get("application.name")
                or props.get("node.name")
                or "Unknown Source"
        )

    def _is_volume_at_100(self, node: Dict[str, Any]) -> bool:
        """
        Checks if a node's volume and channel volumes are at 100% (1.0).

        Args:
            node: The node dictionary to check.

        Returns:
            True if all volumes are at 1.0, False otherwise.
        """
        params = node.get("info", {}).get("params", {})
        if "Props" not in params or not params["Props"]:
            # No volume properties to check.
            return True

        node_name = self._get_node_descriptive_name(node)
        node_id = node.get("id")

        for prop_set in params["Props"]:
            # Check main 'volume' property.
            if "volume" in prop_set and prop_set["volume"] != 1.0:
                self._log(
                    f"Volume is not 100% for '{node_name}' (ID: {node_id}) (value: {prop_set['volume']})")
                return False

            # Check 'channelVolumes' array.
            if "channelVolumes" in prop_set and not all(vol == 1.0 for vol in prop_set["channelVolumes"]):
                self._log(
                    f"Volume is not 100% for '{node_name}' (ID: {node_id}) (values: {prop_set['channelVolumes']})")
                return False

        return True

    def run(self) -> str:
        """
        Executes all checks and returns a formatted status string.

        Returns:
            A formatted string for display.
        """
        raw_graph = self._get_pipewire_graph()
        if not raw_graph:
            return self._format_output("<txt><span color='Red'>Err</span></txt>")

        graph = PipeWireGraph(raw_graph)

        # 1. Find the target device node.
        self._log(f"-> Searching for device: '{self.target_device_substring}'")
        target_node = self._find_node_by_name(graph, self.target_device_substring)
        if not target_node:
            self._log("Device not found.")
            return self._format_output("<txt><span color='White'>N/A</span></txt>")

        self._log("Device found.")
        device_freq = self._get_node_sample_rate(target_node)
        if not device_freq:
            self._log("Could not determine sample rate for the target device.")
            return self._format_output("<txt><span color='Red'>Err</span></txt>")

        # 2. Check target device volume.
        if not self._is_volume_at_100(target_node):
            return self._format_output("<txt><span color='Red'>Vol Err</span></txt>")

        # 3. Find and filter sources connected to the target device.
        self._log(f"-> Finding sources connected to device ID {target_node['id']}")
        source_nodes = self._get_connected_source_nodes(graph, target_node["id"])
        self._log("-> Filtering sources...")
        relevant_sources = self._filter_sources(source_nodes)

        # 4. Handle different source count scenarios.
        if not relevant_sources:
            self._log("Device is idle (no relevant sources connected).")
            return self._format_output(f"<txt><span color='White'>Idle</span></txt>")

        if len(relevant_sources) > 1:
            self._log(f"Device has {len(relevant_sources)} active sources. Skipping detailed check.")
            return self._format_output("<txt><span color='Red'>Src Err</span></txt>")

        # 5. Process the single relevant source.
        source = relevant_sources[0]
        self._log(f"Found 1 relevant source.")

        if not self._is_volume_at_100(source):
            return self._format_output("<txt><span color='Red'>Vol Err</span></txt>")

        source_freq = self._get_node_sample_rate(source)
        source_name = self._get_node_descriptive_name(source)
        self._log(f"-> Checking source '{source_name}' (ID: {source.get('id')}): "
                  f"Device rate is {device_freq}, Source rate is {source_freq}")

        if source_freq and device_freq != source_freq:
            self._log(f"Mismatch found! Device({device_freq}) != Source({source_freq})")
            return self._format_output("<txt><span color='Red'>Freq Err</span></txt>")

        # 6. If all checks pass, report the current frequency.
        self._log("All source sample rates match the device rate.")
        return self._format_output(f"<txt><span color='White'>{device_freq}</span></txt>")


def main():
    """
    Main entry point for the script.
    Parses command-line arguments and runs the frequency check.
    """
    if len(sys.argv) != 2:
        print(f"Usage: python {sys.argv[0]} <device_name>", file=sys.stderr)
        sys.exit(1)

    target_device = sys.argv[1]

    monitor = PipeWireMonitor(target_device)
    result_string = monitor.run()
    print(result_string)


if __name__ == "__main__":
    main()
