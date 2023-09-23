# Onelink

Self-hosted URL shortener, NixOS ready, written in Python.


## Development

### Using Nix

Using Nix, a simple `nix develop` to handle the dependencies.

### Linux/macOS

On other systems, you'll need `python3`.
Then, install the dependencies using:
```sh
pip install -e .
```

To run the development environment, use
```bash
onelink
```


## Installation

### NixOS

If you are on NixOS, you can just use this repo as an input in your NixOS
flake.nix.

Onelink exports a NixOS module, with a service that enables ACME, the Nginx
server block, the service, and will open the ports in the firewall (for this
last one to work, don't forget to open it with `networking.firewall.enable`):
```nix
{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-23.05";
    onelink.url = "github:Sigmanificient/1l.is";
  };

  outputs =
    { nixpkgs
    , onelink
    , ...
    }:
    let
      system = "x86_64-linux";
    in
    {
      nixosConfigurations = {
        Server = nixpkgs.lib.nixosSystem {
          inherit system;

          modules = [
            onelink.nixosModules.${system}.default
            {
              services.onelink = {
                enable = true;
                domain = "1l.is";
                acmeEmail = "example@example.com";
                acmeAcceptTerms = true;
              };
            }

            # Some other configuration you might need for you system.
            ./server/configuration.nix
            ./server/hardware-configuration.nix
          ];
        };
      };
    };
}
```
> **Warning**
> If your NixOS configuration fails to build, you may have baddly configured 
> your domain name. Please, configure your domain name as a *A record* and try
> again.

### Other systems

To run the prod environment, you'll need to run a ASGI service, such as
`hypercorn`:
```bash
hypercorn src.onelink.__main__:app
```
