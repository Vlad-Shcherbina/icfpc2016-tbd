{ nixpkgs ? import <nixpkgs> {} }:

let

  inherit (nixpkgs) pkgs;

  py = pkgs.python35Packages;

  f = { mkDerivation    ? pkgs.stdenv.mkDerivation,
        python          ? pkgs.python3,
        postgresql      ? pkgs.postgresql,
        bottle          ? py.bottle,
        pillow          ? py.pillow,
        pytest          ? py.pytest,
        pytestcov       ? py.pytestcov,
        psycopg2        ? py.psycopg2,
        swig3           ? pkgs.swig3,
        requests        ? py.requests2,
        twisted         ? py.twisted
        }:

    mkDerivation {
      name = "tbd-tournament-runner";
      version = "0.1.0.0";
      src = ./.;
      buildInputs = [ python
                      postgresql
                      bottle
                      pillow
                      psycopg2
                      pytest
                      pytestcov
                      swig3
                      requests
                      twisted ]; };

  drv = pkgs.callPackage f {};

in

  drv
