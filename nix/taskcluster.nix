let pkgs' = import <nixpkgs> {}; in
{ pkgs ? import (pkgs'.fetchFromGitHub (builtins.fromJSON (builtins.readFile ./nixpkgs.json))) {}
}:

#let
#
#  releng_pkgs = import ./default.nix { inherit pkgs; };
#
#  inherit (releng_pkgs.lib) packagesWith;
#  inherit (releng_pkgs.pkgs.lib) flatten;
#
#  tasks =
#      pkgs.lib.strings.concatStringsSep "\n\n" (
#        flatten (map (pkg: pkg.taskclusterGithubTasks)
#                     (packagesWith  "taskclusterGithubTasks"  releng_pkgs)
#                )
#      );
#
#in pkgs.writeText "taskcluster.yml" ''
#version: 0
#allowPullRequests: public
#metadata:
#  name: "Mozilla RelEng"
#  description: "Mozilla RelEng Services"
#  owner: "{{ event.head.user.email }}"
#  source: "{{ event.head.repo.url }}"
#tasks:
#
#${tasks}
#''
pkgs.stdenv.mkDerivation {
  name = "taskcluster";
  buildCommand = ''
    echo "+--------------------------------------------------------+"
    echo "| Not possible to update repositories using \`nix-build\`. |"
    echo "|         Please run \`nix-shell taskcluster.nix\`.        |"
    echo "+--------------------------------------------------------+"
    exit 1
  '';
  shellHook = ''
    echo "Works!!"
    echo "===================================================================="
    echo "===================================================================="
    env
    echo "===================================================================="
    echo "===================================================================="
    exit
  '';
}
