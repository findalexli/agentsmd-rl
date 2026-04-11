#!/usr/bin/env python3
"""Fix ContainerOptions type definition that solve.sh missed."""

from pathlib import Path

PKG = Path("/workspace/remix/packages/interaction")

# Add ContainerOptions type before createContainer
p = PKG / "src/lib/interaction.ts"
src = p.read_text()

container_options = '''/**
 * Options for creating an event container.
 */
export type ContainerOptions = {
  /**
   * An optional abort signal to dispose the container when the signal is aborted
   */
  signal?: AbortSignal
  /**
   * An optional error handler called when a listener throws an error
   */
  onError?: (error: unknown) => void
}

'''

# Insert before createContainer if not already present
if "export type ContainerOptions" not in src:
    src = src.replace(
        "/**\n * ### Description\n *\n * Creates an event container",
        container_options + "/**\n * ### Description\n *\n * Creates an event container"
    )
    p.write_text(src)
    print("Added ContainerOptions type")
else:
    print("ContainerOptions already exists")
