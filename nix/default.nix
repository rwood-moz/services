let
  pkgs' = import <nixpkgs> {};
  nixpkgs = pkgs'.fetchFromGitHub (builtins.fromJSON (builtins.readFile ./nixpkgs.json));
  nixpkgs-mozilla = pkgs'.fetchFromGitHub (builtins.fromJSON (builtins.readFile ./nixpkgs-mozilla.json));
in
{ pkgs ? import nixpkgs {}
, mozilla ? import nixpkgs-mozilla {}
}:

let

  postgresql = pkgs.postgresql95;

  releng_pkgs = {

    pkgs = pkgs // {
      name = "nixpkgs";
      update = releng_pkgs.lib.updateFromGitHub {
        owner = "NixOS";
        repo = "nixpkgs-channels";
        branch = "nixos-17.03";
        path = "nix/nixpkgs.json";
      };
    };

    mozilla = mozilla // {
      name = "nixpkgs-mozilla";
      update = releng_pkgs.lib.updateFromGitHub {
        owner = "mozilla";
        repo = "nixpkgs-mozilla";
        branch = "master";
        path = "nix/nixpkgs-mozilla.json";
      };
    };

    lib = import ./lib/default.nix { inherit releng_pkgs; };
    tools = import ./tools/default.nix { inherit releng_pkgs; };
    gecko-env = import ./gecko_env.nix { inherit releng_pkgs; };
    elmPackages = pkgs.elmPackages.override { nodejs = pkgs."nodejs-6_x"; };
    postgresql = pkgs.postgresql95;
    please-cli = import ./../lib/please_cli { inherit releng_pkgs; };

    apps = {

      # TODO: backend_common_example = import ./../lib/backend_common/example { inherit releng_pkgs; };
      "frontend-common-example" = import ./../lib/frontend_common/example { inherit releng_pkgs; };


      "releng-docs" = import ./../src/releng_docs { inherit releng_pkgs; };
      "releng-frontend" = import ./../src/releng_frontend { inherit releng_pkgs; };
      "releng-clobberer" = import ./../src/releng_clobberer { inherit releng_pkgs; };
      "releng-tooltool" = import ./../src/releng_tooltool { inherit releng_pkgs; };
      "releng-treestatus" = import ./../src/releng_treestatus { inherit releng_pkgs; };
      "releng-mapper" = import ./../src/releng_mapper { inherit releng_pkgs; };
      "releng-archiver" = import ./../src/releng_archiver { inherit releng_pkgs; };

      "shipit-frontend" = import ./../src/shipit_frontend { inherit releng_pkgs; };
      "shipit-uplift" = import ./../src/shipit_uplift { inherit releng_pkgs; };
      "shipit-bot-uplift" = import ./../src/shipit_bot_uplift { inherit releng_pkgs; };
      "shipit-static-analysis" = import ./../src/shipit_static_analysis { inherit releng_pkgs; };
      "shipit-code-coverage" = import ./../src/shipit_code_coverage { inherit releng_pkgs; };
      "shipit-risk-assessment" = import ./../src/shipit_risk_assessment { inherit releng_pkgs; };
      "shipit-pulse-listener" = import ./../src/shipit_pulse_listener { inherit releng_pkgs; };
      "shipit-pipeline" = import ./../src/shipit_pipeline { inherit releng_pkgs; };
      "shipit-signoff" = import ./../src/shipit_signoff { inherit releng_pkgs; };
      "shipit-taskcluster" = import ./../src/shipit_taskcluster { inherit releng_pkgs; };
    };

  };

in releng_pkgs
