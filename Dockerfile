FROM alpine

ONBUILD ENV \
    ENV=/etc/profile \
    PATH=/root/.nix-profile/bin:/root/.nix-profile/sbin:/bin:/sbin:/usr/bin:/usr/sbin \
    GIT_SSL_CAINFO=/root/.nix-profile/etc/ssl/certs/ca-bundle.crt \
    NIX_SSL_CERT_FILE=/root/.nix-profile/etc/ssl/certs/ca-bundle.crt \
    NIX_PATH="nixpkgs=https://github.com/NixOS/nixpkgs-channels/archive/5acb454e2ad3e3783e63b86a9a31e800d2507e66.tar.gz"

ENV \
    ENV=/etc/profile \
    PATH=/root/.nix-profile/bin:/root/.nix-profile/sbin:/bin:/sbin:/usr/bin:/usr/sbin \
    LANGUAGE="C" \
    LC_ALL="C" \
    LANG="C" \
    GIT_SSL_CAINFO=/root/.nix-profile/etc/ssl/certs/ca-bundle.crt \
    NIX_SSL_CERT_FILE=/root/.nix-profile/etc/ssl/certs/ca-bundle.crt \
    NIX_PATH="nixpkgs=https://github.com/NixOS/nixpkgs-channels/archive/5acb454e2ad3e3783e63b86a9a31e800d2507e66.tar.gz"

COPY ./ /app

RUN apk --update add bash tar openssl \
    && rm -rf /var/cache/apk/* \
    && wget -O- http://nixos.org/releases/nix/nix-1.11.7/nix-1.11.7-x86_64-linux.tar.bz2 | bzcat - | tar xf - \
    && echo "nixbld:x:30000:nixbld1,nixbld2,nixbld3,nixbld4,nixbld5,nixbld6,nixbld7,nixbld8,nixbld9,nixbld10,nixbld11,nixbld12,nixbld13,nixbld14,nixbld15,nixbld16,nixbld17,nixbld18,nixbld19,nixbld20,nixbld21,nixbld22,nixbld23,nixbld24,nixbld25,nixbld26,nixbld27,nixbld28,nixbld29,nixbld30" >> /etc/group \
    && for i in $(seq 1 30); do echo "nixbld$i:x:$((30000 + $i)):30000:::" >> /etc/passwd; done \
    && mkdir -m 0755 /nix && USER=root sh nix-*-x86_64-linux/install \
    && echo ". /root/.nix-profile/etc/profile.d/nix.sh" >> /etc/profile \
    && rm -r /nix-*-x86_64-linux \
    && mkdir -p /etc/nix \
    && echo "binary-caches = https://cache.mozilla-releng.net https://cache.nixos.org" >> /etc/nix/nix.conf \
    && nix-env -u \
    && nix-collect-garbage -d \
    && nix-build /app/nix/default.nix -A please-cli -o /app/result-please-cli
