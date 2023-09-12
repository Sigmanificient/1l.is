{
  inputs = {
    nixpkgs.url = "nixpkgs/nixos-unstable";
    utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, utils }:
    utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};

        quart-db = (import ./quart-db.nix {
          inherit pkgs;
          pypkgs = py.pkgs;
        });

        onelink = py.pkgs.buildPythonPackage {
          pname = "onelink";
          version = "0.0.1";
          format = "pyproject";

          src = ./.;
          propagatedBuildInputs = py.deps.web;
        };

        py = {
          env = pkgs.python311.withPackages (_: py.deps.all);
          pkgs = pkgs.python311Packages;
          deps = rec {
            web = with py.pkgs; [ quart quart-db ];
            dev = with py.pkgs; [ black isort vulture pytest ];
            prod = with py.pkgs; [ hypercorn ];
            all = web ++ dev ++ prod ++ [ onelink ];
          };
        };

      in
      {
        nixosModules.default = { config, ... }:
          let
            lib = nixpkgs.lib;
            cfg = config.services.onelink;
            sock = "/run/onelink/onelink.sock";
            domain = "1l.is";
            acme_email = "clement2104.boillot@gmail.com";
          in
          {
            options.services.onelink = {
              enable = lib.mkEnableOption "onelink";
            };

            config = lib.mkIf cfg.enable {
              security.acme = {
                acceptTerms = true;
                defaults.email = acme_email;
              };

              networking.firewall = {
                enable = true;
                allowedTCPPorts = [ 80 443 ];
              };

              services.nginx = {
                enable = true;
                virtualHosts.${domain} = {
                  enableACME = true;
                  forceSSL = true;
                  locations = {
                    "/".extraConfig = ''
                      include proxy_params;
                      proxy_pass http://unix:${sock};
                    '';
                    "/.well-known/acme-challenge".extraConfig = ''
                      root /var/www/demo
                    '';
                  };
                };
              };

              systemd.services.onelink = {
                wantedBy = [ "multi-user.target" ];
                serviceConfig = {
                  ExecStart = "${py.env}/bin/hypercorn onelink.__main__:app --bind unix:${sock}";
                  WorkingDirectory = ./.;
                  RuntimeDirectory = "onelink";
                };
              };
            };
          };

        devShells.default = pkgs.mkShell {
          packages = [ py.env pkgs.pyright ];
        };

        formatter = pkgs.nixpkgs-fmt;
        packages.default = onelink;
      });
}
