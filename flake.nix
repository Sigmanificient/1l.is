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

        onelink = py.pkgs.buildPythonApplication {
          pname = "onelink";
          version = "0.0.1";
          format = "setuptools";

          src = ./.;
          propagatedBuildInputs = py.deps.web ++ py.deps.build;
          doCheck = false;
       };

        py = {
          env = pkgs.python311.withPackages (_: py.deps.all);
          pkgs = pkgs.python311Packages;
          deps = rec {
            web = with py.pkgs; [ quart quart-db ];
            dev = with py.pkgs; [ black isort vulture pytest ];
            prod = with py.pkgs; [ hypercorn ];
            build = with py.pkgs; [ setuptools wheel ];
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
          in
          {
            options.services.onelink = {
              enable = lib.mkEnableOption "onelink";
              domain = lib.mkOption {
                type = lib.types.nullOr lib.types.str;
                default = null;
              };
              acmeEmail = lib.mkOption {
                type = lib.types.nullOr lib.types.str;
                default = null;
              };
              acmeAcceptTerms = lib.mkOption {
                type = lib.types.bool;
                default = false;
              };
            };

            config = lib.mkIf cfg.enable {
              security.acme = {
                acceptTerms = cfg.acmeAcceptTerms;
                defaults.email = cfg.acmeEmail;
              };
              services.nginx = {
                enable = true;
                virtualHosts.${cfg.domain} = {
                  enableACME = true;
                  addSSL = true;
                  locations = {
                    "/" = {
                      proxyPass = "http://unix:${sock}";
                      recommendedProxySettings = true;
                    };
                  };
                };
              };

              systemd.services.onelink = {
                wantedBy = [ "multi-user.target" ];
                serviceConfig = {
                  ExecStart = "${py.env}/bin/hypercorn onelink.__main__:app --bind unix:${sock} --user 666";
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
