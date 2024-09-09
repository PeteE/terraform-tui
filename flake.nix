{
  description = "terraform-tui is a terminal user interface for terraform";
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    poetry2nix = {
      url = "github:nix-community/poetry2nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = { self, nixpkgs, flake-utils, poetry2nix }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        # create a custom "mkPoetryApplication" API function that under the hood uses
        # the packages and versions (python3, poetry etc.) from our pinned nixpkgs above:

        # GPT Assist: This means “take the mkPoetryApplication attribute from the set produced by calling mkPoetry2Nix { inherit pkgs; } and make it available in the current scope.”
        inherit (poetry2nix.lib.mkPoetry2Nix { inherit pkgs; }) mkPoetryApplication; 
        terraform-tui-app = mkPoetryApplication {
            projectDir = self;
        };
      in
      {
        packages = {
          default = terraform-tui-app;
        };

        # Shell for app dependencies.
        #
        #     nix develop
        #
        # Use this shell for developing your app.
        devShells.default = pkgs.mkShell {
          inputsFrom = [ terraform-tui-app ];
          packages = [ terraform-tui-app ];
        };

        # Shell for poetry.
        #
        #     nix develop .#poetry
        #
        # Use this shell for changes to pyproject.toml and poetry.lock.
        devShells.poetry = pkgs.mkShell {
          packages = [ pkgs.poetry ];
        };
      });
}
