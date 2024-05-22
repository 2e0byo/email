{
  description = "Application packaged using poetry2nix";

  inputs = {
    flake-utils.url = "github:numtide/flake-utils";
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    poetry2nix = {
      url = "github:nix-community/poetry2nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = inputs @ {
    self,
    nixpkgs,
    flake-utils,
    poetry2nix,
  }:
    flake-utils.lib.eachDefaultSystem (system: let
      # see https://github.com/nix-community/poetry2nix/tree/master#api for more functions and examples.
      pkgs = nixpkgs.legacyPackages.${system};
      poetry2nix = inputs.poetry2nix.lib.mkPoetry2Nix {inherit pkgs;};
    in {
      packages = {
        email-auth = poetry2nix.mkPoetryApplication {
          projectDir = self;
          overrides =
            poetry2nix.defaultPoetryOverrides.extend
            (self: super: {
              o365 =
                super.o365.overridePythonAttrs
                (
                  old: {
                    buildInputs = (old.buildInputs or []) ++ [super.setuptools];
                  }
                );
            });
        };
        default = self.packages.${system}.email-auth;
      };

      devShells.default = pkgs.mkShell {
        inputsFrom = [self.packages.${system}.email-auth];
        packages = [pkgs.poetry];
      };
    });
}
