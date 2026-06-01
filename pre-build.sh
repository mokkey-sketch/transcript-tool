#!/bin/bash
# Install Bun
curl -fsSL https://bun.sh/install | bash

# Add bun to the PATH for the current session
export BUN_INSTALL="$HOME/.bun"
export PATH="$BUN_INSTALL/bin:$PATH"

# Install your project dependencies using bun
bun install
