#!/usr/bin/env python3

import sys

import evdev
import vgamepad as vg
import yaml
from evdev import ecodes as e
from vgamepad import XUSB_BUTTON as b


def throw(message):
    print(message)
    sys.exit(1)


class AxisMap:
    def __init__(self, axis: str, value: float) -> None:
        self.axis: str = axis
        self.value: float = value


class Preset:
    def __init__(self, filename: str, input: str | None = None) -> None:
        self.input: str | None = input
        self.maps: dict[str, str | AxisMap] = {}

        try:
            with open(filename, "r") as f:
                preset = yaml.safe_load(f)

                # '--input' has priority over the preset file
                if self.input is None and "input" in preset:
                    self.input = preset["input"]

                if "buttons" not in preset and "axis" not in preset:
                    throw(
                        "The preset does not contain either 'buttons' or 'axis'"
                    )

                # merge the preset's buttons and axis as one dict
                if "buttons" in preset:
                    for key, value in preset["buttons"].items():
                        try:
                            try:
                                value = getattr(b, value)
                            except AttributeError:
                                throw(f"Invalid XUSB_BUTTON value: {value}")
                            self.maps[getattr(e, key)] = value
                        except AttributeError:
                            throw(f"Invalid input event code: {value}")
                if "axis" in preset:
                    for key, value in preset["axis"].items():
                        if "axis" not in value:
                            throw(f"Missing 'axis' attribute to {key}")
                        if "value" not in value:
                            throw(f"Missing 'value' attribute to {key}")
                        try:
                            self.maps[getattr(e, key)] = AxisMap(
                                value["axis"], value["value"]
                            )
                        except AttributeError:
                            throw(f"Invalid input event code: {value}")
        except FileNotFoundError:
            throw(f"File '{filename}' not found.")
        except yaml.YAMLError:
            throw(f"Invalid YAML in file '{filename}'.")


def print_help():
    print("Usage: key2joy [path/to/preset] [OPTIONS]\n")
    print(
        "Example: sudo key2joy preset.yaml --input 'ckb1: CORSAIR K55 RGB PRO Gaming Keyboard vKB'"
    )
    print("\nOptions:")
    print("  --input [NAME]\tspecify the name of an input device")
    print("  --help\t\tdisplay this help message")
    sys.exit(0)


if __name__ == "__main__":
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
            print("The '--input' flag has no value\n")
            print_help()
    preset = Preset(sys.argv[1], input)

    if preset.input is None:
        print("An input device was not provided\n")
        print_help()

    print(f"Searching device with name: '{preset.input}'")
    # Iterate over the devices and find the one with the desired name
    device = None
    for dev in [evdev.InputDevice(path) for path in evdev.list_devices()]:
        if dev.name == preset.input:
            device = evdev.InputDevice(dev.path)
            break

    if device is None:
        print(f"Device not found: '{preset.input}'")
        throw("Exiting")
    print(f"Found device '{device.path}'")

    gamepad = vg.VX360Gamepad()
    axis = {"x": 0.0, "y": 0.0}

    print("Starting virtual gamepad")
    try:
        for event in device.read_loop():
            if event.type == e.EV_KEY:
                button = preset.maps.get(event.code)
                if button:
                    if event.value == 1:  # Key press
                        if isinstance(button, AxisMap):
                            axis[button.axis] += button.value
                        else:
                            gamepad.press_button(button)
                    elif event.value == 0:  # Key release
                        if isinstance(button, AxisMap):
                            axis[button.axis] -= button.value
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
