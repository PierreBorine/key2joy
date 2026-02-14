#!/usr/bin/env python3

import sys
from typing import Any

import evdev
import vgamepad as vg
import yaml
from evdev import InputDevice, ecodes
from vgamepad import XUSB_BUTTON


class PresetError(Exception):
    pass


class AxisMap:
    def __init__(self, axis: str, offset: float) -> None:
        self.axis: str = axis
        self.offset: float = offset


class Preset:
    def __init__(self, filename: str, input: str | None = None) -> None:
        self.input: str | None = input
        self.maps: dict[int, XUSB_BUTTON | AxisMap] = {}

        preset: dict[str, Any] | None = None
        try:
            with open(filename, "r") as f:
                preset = yaml.safe_load(f)
        except OSError as err:
            raise PresetError(str(err))
        except yaml.YAMLError:
            raise PresetError(f"invalid YAML in file '{filename}'.")
        if preset is None:
            raise PresetError("could not read preset file")

        # '--input' has priority over the preset file
        if self.input is None and "input" in preset:
            self.input = preset["input"]

        if "buttons" not in preset and "axis" not in preset:
            raise PresetError("the preset does not contain any configuration")

        if "buttons" in preset:
            for key, value in preset["buttons"].items():
                try:
                    xusb: XUSB_BUTTON = getattr(XUSB_BUTTON, value)
                except AttributeError:
                    raise PresetError(f"invalid XUSB_BUTTON value: {value}")
                self.maps[self.get_ecode(key, value)] = xusb
        if "axis" in preset:
            for key, value in preset["axis"].items():
                for opt in ["axis", "offset"]:
                    if opt not in value:
                        raise PresetError(
                            f"missing '{opt}' attribute to {key}"
                        )
                self.maps[self.get_ecode(key, value)] = AxisMap(
                    value["axis"], value["offset"]
                )

    @staticmethod
    def get_ecode(key: str, value: str) -> int:
        ecode = ecodes.ecodes.get(key)
        if ecode is None:
            raise PresetError(f"invalid input event code: {value}")
        return ecode


def print_help():
    print("Usage: key2joy [path/to/preset] [OPTIONS]\n")
    print(
        "Example: sudo key2joy preset.yaml",
        "--input 'Keychron Keychron K8 HE Keyboard'",
    )
    print("\nOptions:")
    print("  --input [NAME]\tspecify the name of an input device")
    print("  --help\t\tdisplay this help message")
    sys.exit(0)


def main() -> None:
    if len(sys.argv) == 1 or "--help" in sys.argv:
        print_help()

    if sys.argv[1] in ["--input"]:
        print("The first argument must be a path to a preset file\n")
        print_help()

    input = None
    if "--input" in sys.argv:
        # check if '--input' has a value
        nextIndex = sys.argv.index("--input") + 1
        if len(sys.argv) > nextIndex:  # This may be an issue in the future
            input = sys.argv[nextIndex]
        else:
            print("input flag provided with no value\n")
            print_help()
    try:
        preset = Preset(sys.argv[1], input)
    except PresetError as err:
        print(str(err).capitalize())
        sys.exit(1)

    if preset.input is None:
        print("No input device were provided\n")
        print_help()

    print(f"Searching device: '{preset.input}'")
    # Iterate over the devices and find the one with the desired name
    device = None
    for path in evdev.list_devices():
        dev = InputDevice(path)
        if dev.name == preset.input:
            device = InputDevice(dev.path)
            break
    if device is None:
        print(f"Device not found: '{preset.input}', exiting...")
        sys.exit(1)
    print(f"Found device '{device.path}'")

    gamepad = vg.VX360Gamepad()
    axis = {"x": 0.0, "y": 0.0}

    print("Starting virtual gamepad")
    try:
        for event in device.read_loop():
            if event.type == ecodes.EV_KEY:
                button = preset.maps.get(event.code)
                if button is not None:
                    if event.value == 1:  # Key press
                        if isinstance(button, AxisMap):
                            axis[button.axis] += button.offset
                        else:
                            gamepad.press_button(button)
                    elif event.value == 0:  # Key release
                        if isinstance(button, AxisMap):
                            axis[button.axis] -= button.offset
                        else:
                            gamepad.release_button(button)
                # TODO: implement right_joystick_float
                gamepad.left_joystick_float(
                    x_value_float=axis["x"], y_value_float=axis["y"]
                )
                gamepad.update()
    except KeyboardInterrupt:
        print("Stopping virtual gamepad")
        sys.exit(0)


if __name__ == "__main__":
    main()
