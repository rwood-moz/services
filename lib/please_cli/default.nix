{ releng_pkgs 
}: 

let

  inherit (releng_pkgs.lib) mkPython fromRequirementsFile filterSource ;
  inherit (releng_pkgs.pkgs) writeScript makeWrapper glibcLocales nix;
  inherit (releng_pkgs.pkgs.lib) fileContents ;
  inherit (releng_pkgs.pkgs.stdenv) mkDerivation;
  inherit (releng_pkgs.tools) pypi2nix;

  python = import ./requirements.nix { inherit (releng_pkgs) pkgs; };
  name = "mozilla-please-cli";
  dirname = "please_cli";

  self = mkPython {
    inherit python name dirname;
    version = fileContents ./please_cli/VERSION;
    src = filterSource ./. { inherit name; };
    doCheck = false;
    buildInputs =
      [ makeWrapper nix ] ++
      fromRequirementsFile ./requirements-dev.txt python.packages;
    propagatedBuildInputs =
      fromRequirementsFile ./requirements.txt python.packages;
    prePatch= ''
      rm -f please_cli/VERSION
      cp ${./../../VERSION} please_cli/VERSION
      sed -i \
        -e 's|NIX_BIN_DIR = ""|NIX_BIN_DIR = "${nix}/bin/"|'\
        please_cli/config.py
    '';
    passthru = {
      src_path = "lib/please_cli";
      update = writeScript "update-${name}" ''
        pushd ${self.src_path}
        ${pypi2nix}/bin/pypi2nix -v \
          -V 3.5 \
          -r requirements.txt \
          -r requirements-dev.txt
        popd
      '';
    };
  };

in self
