{ pkgs ? import <nixpkgs> { }
, pypkgs ? pkgs.python311Packages
}:
pypkgs.buildPythonPackage rec {
  pname = "quart-db";

  version = "0.6.1";
  format = "wheel";

  src = pkgs.fetchPypi {
    pname = "quart_db";
    inherit version format;

    python = "py3";
    dist = "py3";
    platform = "any";
    hash = "sha256-rq8Z94CxlGrweqakS02QVdVLoSoOAt4aAjzzJAkeXNU=";
  };

  propagatedBuildInputs = with pypkgs; [ aiosqlite ];
}
