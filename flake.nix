{
  inputs = {
    nixpkgs.url = "nixpkgs/nixos-unstable";
    utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, utils }:
    utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};

        quart-db = (import ./quart-db.nix {
          inherit pkgs;
          pypkgs = py.pkgs;
        });

        py = {
          env = pkgs.python311.withPackages (_: py.deps.all);
          pkgs = pkgs.python311Packages;
          deps = rec {
            prod = with py.pkgs; [ quart quart-db ];
            dev = with py.pkgs; [ black isort vulture ];
            all = prod ++ dev;
          };
        };
      in
      {
        devShells.default = pkgs.mkShell {
          packages = [ py.env pkgs.pyright ];
        };

        formatter = pkgs.nixpkgs-fmt;
        packages.default = py.pkgs.buildPythonPackage {
          pname = "onelink";
          version = "0.0.1";
          format = "pyproject";

          src = ./.;
          propagatedBuildInputs = py.deps.prod;
        };
      });
}
