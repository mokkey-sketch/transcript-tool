#!/bin/bash
# Install bun
curl -fsSL https://bun.sh/install | bash

# Ensure the bun binary is in the PATH for the rest of the build/run
export PATH="$HOME/.bun/bin:$PATH"
