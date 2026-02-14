#!/usr/bin/env python3

import sys

import evdev
import vgamepad as vg
import yaml
from evdev import ecodes as e
from vgamepad import XUSB_BUTTON as b


def throw(message):
    print(message)
    exit(1)


def print_help(exit_code):
    print("Usage: key2joy [path/to/preset] [OPTIONS]\n")
    print(
        "Example: sudo key2joy preset.yaml --input 'ckb1: CORSAIR K55 RGB PRO Gaming Keyboard vKB'"
    )
    print("\nOptions:")
    print("  --input [NAME]\tspecify the name of an input device")
    print("  --help\t\tdisplay this help message")
    exit(exit_code)


def load_preset(filename):
    try:
        with open(filename, "r") as f:
            preset = yaml.safe_load(f)
            presetFinal = {"input": None, "maps": {}}

            if "input" in preset:
                presetFinal["input"] = preset["input"]

            if "buttons" not in preset and "axis" not in preset:
                throw("The preset does not contain either 'buttons' or 'axis'")

            # merge the preset's buttons and axis as one dict
            if "buttons" in preset:
                for key, value in preset["buttons"].items():
                    try:
                        try:
                            value = getattr(b, value)
                        except AttributeError:
                            throw(f"Invalid XUSB_BUTTON value: {value}")
                        presetFinal["maps"][getattr(e, key)] = {"value": value}
                    except AttributeError:
                        throw(f"Invalid input event code: {value}")
            if "axis" in preset:
                for key, value in preset["axis"].items():
                    if "axis" not in value:
                        throw(f"Missing 'axis' attribute to {key}")
                    if "value" not in value:
                        throw(f"Missing 'value' attribute to {key}")
                    try:
                        presetFinal["maps"][getattr(e, key)] = value
                    except AttributeError:
                        throw(f"Invalid input event code: {value}")

            return presetFinal
    except FileNotFoundError:
        throw(f"File '{filename}' not found.")
    except yaml.YAMLError:
        throw(f"Invalid YAML in file '{filename}'.")


if __name__ == "__main__":
    if len(sys.argv) == 1 or "--help" in sys.argv:
        print_help(0)

    if sys.argv[1] in ["--input"]:
        print("The first argument must be a path to a preset file\n")
        print_help(1)

    preset = load_preset(sys.argv[1])

    # '--input' has priority over the preset file
    if "--input" in sys.argv:
        # check if '--input' has a value
        nextIndex = sys.argv.index("--input") + 1
        if len(sys.argv) > nextIndex:  # This may be an issue in the future
            preset["input"] = sys.argv[nextIndex]
        else:
            print("The '--input' flag has no value\n")
            print_help(1)
    elif preset["input"] is None:
        print("An input device was not provided\n")
        print_help(1)

    print(f"Searching device with name: '{preset['input']}'")
    # Iterate over the devices and find the one with the desired name
    device = None
    for dev in [evdev.InputDevice(path) for path in evdev.list_devices()]:
        if dev.name == preset["input"]:
            device = evdev.InputDevice(dev.path)
            break

    if device is None:
        print(f"Device not found: '{preset['input']}'")
        throw("Exiting")
    print(f"Found device '{device.path}'")

    gamepad = vg.VX360Gamepad()
    axis = {"x": 0.0, "y": 0.0}

    print("Starting virtual gamepad")
    try:
        for event in device.read_loop():
            if event.type == e.EV_KEY:
                button = preset["maps"].get(event.code)
                if button:
                    if event.value == 1:  # Key press
                        if "axis" in button:
                            axis[button["axis"]] += button["value"]
                        else:
                            gamepad.press_button(button=button["value"])
                    elif event.value == 0:  # Key release
                        if "axis" in button:
                            axis[button["axis"]] -= button["value"]
                        else:
                            gamepad.release_button(button=button["value"])
                # TODO: implement right_joystick_float
                gamepad.left_joystick_float(
                    x_value_float=axis["x"], y_value_float=axis["y"]
                )
                gamepad.update()
    except KeyboardInterrupt:
        print("Stopping virtual gamepad")
        exit(0)
