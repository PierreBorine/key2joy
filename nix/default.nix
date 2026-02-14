{
  lib,
  buildPythonApplication,
  setuptools,
  vgamepad,
  libevdev,
  evdev,
  pyyaml,
}: let
  pyproject = (lib.importTOML ../pyproject.toml).project;
in
  buildPythonApplication {
    pname = pyproject.name;
    inherit (pyproject) version;
    pyproject = true;

    src = lib.cleanSource ../.;

    nativeBuildInputs = [setuptools];

    dependencies = [
      libevdev
      evdev
      vgamepad
      pyyaml
    ];

    meta = {
      inherit (pyproject) description;
      homepage = pyproject.urls.Homepage;
      license = lib.licenses.gpl3;
      mainProgram = "key2joy";
    };
  }
