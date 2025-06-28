#!/usr/bin/env python3

import sys

import evdev
import vgamepad as vg
import yaml
from evdev import ecodes as e
from vgamepad import XUSB_BUTTON as b


def load_preset(filename):
    try:
        with open(filename, "r") as f:
            preset = yaml.safe_load(f)
            presetFinal = {"input": None, "maps": {}}

            if "input" in preset:
                presetFinal["input"] = preset["input"]

            if "buttons" not in preset and "axis" not in preset:
                print("The preset does not contain either 'buttons' or 'axis'")
                exit(1)

            # merge the preset's buttons and axis as one dict
            if "buttons" in preset:
                for key, value in preset["buttons"].items():
                    try:
                        try:
                            value = getattr(b, value)
                        except AttributeError:
                            print(f"Invalid XUSB_BUTTON value: {value}")
                            exit(1)
                        presetFinal["maps"][getattr(e, key)] = {"value": value}
                    except AttributeError:
                        print(f"Invalid input event code: {value}")
                        exit(1)
            if "axis" in preset:
                for key, value in preset["axis"].items():
                    if "axis" not in value:
                        print(f"Missing 'axis' attribute to {key}")
                        exit(1)
                    if "value" not in value:
                        print(f"Missing 'value' attribute to {key}")
                        exit(1)
                    try:
                        presetFinal["maps"][getattr(e, key)] = value
                    except AttributeError:
                        print(f"Invalid input event code: {value}")
                        exit(1)

            return presetFinal
    except FileNotFoundError:
        print(f"File {filename} not found.")
        exit(1)
    except yaml.YAMLError:
        print(f"Invalid YAML in file {filename}.")
        exit(1)


if __name__ == "__main__":
    if len(sys.argv) == 1 or "--help" in sys.argv:
        print("Usage: key2joy [path/to/preset] [OPTIONS]")
        print(
            "Example: sudo key2joy my_preset.yaml --input 'ckb1: CORSAIR K55 RGB PRO Gaming Keyboard vKB'"
        )
        print("\nOptions:")
        print("  --input [NAME]\t\tspecify the name of an input device")
        print("  --help\t\tdisplay this help message")
        exit(0)

    preset = load_preset(sys.argv[1])

    # Get input device from cli arg if not in the preset file
    if preset["input"] is None:
        if "--input" in sys.argv:
            # check if '--input' has a value
            nextIndex = sys.argv.index("--input") + 1
            if len(sys.argv) > nextIndex:
                preset["input"] = sys.argv[nextIndex]
            else:
                print("The '--input' flag has no value")
                exit(1)
        else:
            print("An input device was not provided")
            exit(1)

    print(f"Searching device with name: '{preset['input']}'")
    # Iterate over the devices and find the one with the desired name
    devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
    device = None
    for dev in devices:
        if dev.name == preset["input"]:
            device = evdev.InputDevice(dev.path)
            break

    if device is None:
        print(f"Device not found: '{preset['input']}'")
        print("Exiting")
        exit(1)
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
        print("Stoping virtual gamepad")
        exit(0)
