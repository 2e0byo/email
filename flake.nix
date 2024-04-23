{
  description = "Email auth management";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = {
    self,
    nixpkgs,
    flake-utils,
    ...
  }:
    flake-utils.lib.eachDefaultSystem
    (
      system: let
        pkgs = import nixpkgs {
          inherit system;
        };
        python = pkgs.python311;
        # 'build time' deps
        buildInputs = with pkgs; [
          (python.withPackages(ps: with ps; [ # packages not specified in pyproject.toml: these will be available in the venv.
          ]))
          poetry
          pre-commit
        ];
        # allow building c extensions
        env = {
          LD_LIBRARY_PATH = "${pkgs.stdenv.cc.cc.lib}/lib";
        };
      in
        with pkgs; {
          devShells.default = mkShell {
            inherit buildInputs;
            inherit env;
              shellHook = ''
              pre-commit install
              '';
          };
        }
    );
}
