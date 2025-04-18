#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -n "$ZSH_VERSION" ]; then
    SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
fi
INTERACTIVE_DIR="$ISAAC_PATH/exts/isaacsim.examples.interactive/isaacsim/examples/interactive"

count=0
echo "Starting to create symbolic links..."
echo "Source directory: $INTERACTIVE_DIR"
echo "Target directory: $SCRIPT_DIR"
echo

for target in "$SCRIPT_DIR"/*/; do
    echo $target
    if [ -d "$target" ]; then
        dirname="$(basename "$target")"
        ln -sf "$target" "$INTERACTIVE_DIR"
        echo "Linked: $INTERACTIVE_DIR/$(basename "$target") -> $target"
        ((count++))
    fi
done
echo

# config file
target="$ISAAC_PATH/exts/isaacsim.examples.interactive/config/extension.toml"
target_bak="$ISAAC_PATH/exts/isaacsim.examples.interactive/config/extension.bak.toml"
if [ ! -f "$target_bak" ]; then
    echo "Backup config file: $target_bak"
    cp "$target" "$target_bak"
fi
ln -sf "$target" "$SCRIPT_DIR"
echo "Linked: $SCRIPT_DIR/$(basename "$target") -> $target"

echo "Total symbolic links created: $count"
