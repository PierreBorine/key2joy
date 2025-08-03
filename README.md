<p align="center">
█▄▀ █▀▀ ▀▄▀ ▀▀▄ ░█ █▀█ ▀▄▀<br>
█░█ ██▄ ░█░ ▄█▄ ▄▀ █▄█ ░█░
</p>

---

<p align="center">
A Linux cli tool to emulate a gamepad using a keyboard.
</p>

## Usage
```sh
sudo key2joy preset.yaml
```
```sh
sudo key2joy preset.yaml --input "ckb1: CORSAIR K55 RGB PRO Gaming Keyboard vKB"
```
- <kbd>CTRL</kbd> + <kbd>C</kbd> to stop

## Writing a preset
This configuration is used to connect a second keyboard to Rainworld.
it follows the game's default keybinds.
```yaml
# Optional: The name of the device to take inputs from.
# It can be obtained using 'sudo evtest'
input: 'ckb1: CORSAIR K55 RGB PRO Gaming Keyboard vKB'

# Input event codes:
# https://github.com/torvalds/linux/blob/master/include/uapi/linux/input-event-codes.h
# Buttons list:
# https://github.com/yannbouteiller/vgamepad#xbox360-gamepad
buttons:
  KEY_LEFTSHIFT: XUSB_GAMEPAD_X
  KEY_W: XUSB_GAMEPAD_A
  KEY_X: XUSB_GAMEPAD_B
  KEY_ESC: XUSB_GAMEPAD_BACK
  KEY_SPACE: XUSB_GAMEPAD_RIGHT_SHOULDER

axis:
  KEY_LEFT:
    axis: x
    value: -1.0
  KEY_RIGHT:
    axis: x
    value: 1.0
  KEY_UP:
    axis: y
    value: -1.0
  KEY_DOWN:
    axis: y
    value: 1.0
```

## Dependencies

- [vgamepad](https://github.com/yannbouteiller/vgamepad) - Gamepad emulation library for Python
- [PyYAML](https://github.com/yaml/pyyaml) - YAML parser for Python
- [python-evdev](https://python-evdev.readthedocs.io/en/latest) - Python bindings for Linux inputs
- [libevdev](https://www.freedesktop.org/software/libevdev/doc/latest/index.html) - Linux inputs library
