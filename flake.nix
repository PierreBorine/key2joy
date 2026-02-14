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
    ...
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
    in {
      default = pkgs.mkShell {
        inherit (self.packages.${system}.key2joy) nativeBuildInputs;
        buildInputs =
          self.packages.${system}.key2joy.propagatedBuildInputs
          ++ self.packages.${system}.key2joy.buildInputs;
      };
    });
  };
}
