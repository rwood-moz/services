{ releng_pkgs
}:

let
  inherit (releng_pkgs.pkgs) makeWrapper;
  inherit (releng_pkgs.pkgs.stdenv) mkDerivation;
  inherit (releng_pkgs.pkgs.lib) writeScript;

  python = import ./requirements.nix { inherit (releng_pkgs) pkgs; };
  python_path =
    "${python.__old.python}/${python.__old.python.sitePackages}:" +
    (builtins.concatStringsSep ":"
      (map (pkg: "${pkg}/${python.__old.python.sitePackages}")
           (builtins.attrValues python.packages)
      )
    );

in mkDerivation {
  name = "taskcluster-cli";
  buildInputs = [ makeWrapper python.__old.python ];
  buildCommand = ''
    mkdir -p $out/bin
    cp ${./taskcluster.py} $out/bin/taskcluster
    chmod +x $out/bin/taskcluster
    echo "${python.__old.python}"
    patchShebangs $out/bin/taskcluster
    wrapProgram $out/bin/taskcluster\
      --set PYTHONPATH "${python_path}" \
      --set LANG "en_US.UTF-8" \
      --set LOCALE_ARCHIVE ${releng_pkgs.pkgs.glibcLocales}/lib/locale/locale-archive
  '';
  passthru.update = writeScript "update-tools-taskcluster-cli" ''
    pushd nix/tools
    ${releng_pkgs.tools.pypi2nix}/bin/pypi2nix -V "3.5" -r requirements.txt -v
    popd
  '';
}
