{ nixpkgs ? import <nixpkgs> {} }:

let

  inherit (nixpkgs) pkgs;

  py = pkgs.python35Packages;

  f = { mkDerivation    ? pkgs.stdenv.mkDerivation,
        python          ? pkgs.python3,
        pillow          ? py.pillow,
        pytest          ? py.pytest,
        pytestcov       ? py.pytestcov,
        requests        ? py.requests2,
        swig3           ? pkgs.swig3,
        twisted         ? py.twisted }:

    mkDerivation {
      name = "tbd-tournament-runner";
      version = "0.1.0.0";
      src = ./.;
      buildInputs = [ python
                      pillow
                      pytest
                      pytestcov
                      requests
                      swig3
                      twisted ]; };

  drv = pkgs.callPackage f {};

in

  drv
