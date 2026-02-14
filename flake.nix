{
  description = "Linux cli to emulate a gamepad using a keyboard";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixpkgs-unstable";
    systems.url = "github:nix-systems/default";
  };

  outputs = {
    self,
    nixpkgs,
    systems,
  }: let
    eachSystem = nixpkgs.lib.genAttrs (import systems);
  in {
    packages = eachSystem (system: let
      pkgs = import nixpkgs {inherit system;};
    in {
      vgamepad = pkgs.python3Packages.callPackage ./nix/vgamepad.nix {};
      key2joy = pkgs.python3Packages.callPackage ./nix {
        inherit (self.packages.${system}) vgamepad;
      };
      default = self.packages.${system}.key2joy;
    });

    devShells = eachSystem (system: let
      pkgs = import nixpkgs {inherit system;};
      inputsFrom = [self.packages.${system}.key2joy];
      packages = pkgs.lib.singleton (
        pkgs.python3.withPackages (pps:
          (with pps; [uv mypy types-pyyaml])
          ++ self.packages.${system}.key2joy.propagatedBuildInputs)
      );
    in {
      default = pkgs.mkShellNoCC {inherit inputsFrom packages;};
      fhs =
        (pkgs.buildFHSEnv {
          name = "pyzone";
          targetPkgs = _: packages;
        }).env;
    });
  };
}
