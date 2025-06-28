{
  lib,
  buildPythonApplication,
  vgamepad,
  libevdev,
  evdev,
  pyyaml,
}:
buildPythonApplication rec {
  pname = "key2joy";
  version = "0.1.0";
  pyproject = false;

  src = ../src;

  propagatedBuildInputs = [
    libevdev
    evdev
    vgamepad
    pyyaml
  ];

  installPhase = ''
    install -Dm755 key2joy.py $out/bin/${pname}
  '';

  meta = {
    description = "Python cli application to emulate a gamepad using a keyboard";
    homepage = "https://github.com/PierreBorine/key2joy";
    license = lib.licenses.gpl3;
  };
}
