let pkgs' = import <nixpkgs> {}; in
{ pkgs ? import (pkgs'.fetchFromGitHub (builtins.fromJSON (builtins.readFile ./nixpkgs.json))) {}
}:

#let
#
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

#curl -L https://github.com/taskcluster/slugid-go/releases/download/v1.0.0/slug-linux-amd64 > slugid 
#chmod +x ./slugid 
#apt-get update 
#apt-get install jq 
#curl -X PUT -d \"`curl -sL https://gist.githubusercontent.com/garbas/703275d089ba3539fed51cfcbff8ef81/raw/9bb921bc11be0cb0c623332de28663a67acf3ade/gista-file | sed \"s|TASK_ID|\\`echo $TASK_ID\\`|\" | sed \"s|CREATED|\\`date +%Y-%m-%dT%T.%sZ\\`|\" | sed \"s|DEADLINE|\\`date --set=\"+1 day\" +%Y-%m-%dT%T.%sZ\\`|\" | sed \"s|EXPIRES|\\`date --set=\"+1 year\" +%Y-%m-%dT%T.%sZ\\`|\"`\" http://taskcluster/queue/v1/task/`./slugid`"
#],

let

  releng_pkgs = import ./default.nix { inherit pkgs; };

  createTask =
    { taskGroupId
    , created
    , deadline
    , expires
    }:
      { provisionerId  = "aws-provisioner-v1";
        workerType = "releng-task";
        taskGroupId = taskGroupId;
        dependencies = [ taskGroupId ];
        inherit created deadline expires;
        scopes = [ "queue:create-task:aws-provisioner-v1/releng-task" ];
        payload = {
            image = "nixos/nix:latest";
            command =
              [ "/bin/bash"
                "-c"
                "echo YAAAAAAY"
              ];
            maxRunTime = 7200;  # seconds (i.e. two hours)
        };
        metadata = {
            name = "Example Task 2";
            description = "Markdown description of **what** this task does";
            owner = "name@example.com";
            source = "https://tools.taskcluster.net/task-creator";
        };
      };

in pkgs.stdenv.mkDerivation {
  name = "taskcluster";
  buildInputs = [ releng_pkgs.tools.taskcluster-tasks ];
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

    taskcluster-tasks


    exit
  '';
}
