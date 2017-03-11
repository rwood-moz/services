{ releng_pkgs
}:
let
  inherit (builtins) readFile;
  inherit (releng_pkgs.lib) mkFrontend;

  nodejs = releng_pkgs.pkgs."nodejs-6_x";
  node_modules = import ./node-modules.nix {
    inherit nodejs;
    inherit (releng_pkgs) pkgs;
  };
  elm_packages = import ./elm-packages.nix;

in mkFrontend {
  inProduction = true;
  inherit nodejs node_modules elm_packages;
  name = "mozilla-shipit-frontend";
  csp = "default-src 'none'; img-src 'self' data: *.gravatar.com; script-src 'self'; style-src 'self'; font-src 'self';";
  src = ./.;
}
