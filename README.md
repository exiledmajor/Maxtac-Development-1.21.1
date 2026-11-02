# Warden AV–07 — Maxtac Development (Minecraft 1.21.1)

Standalone NeoForge workspace for the Warden AV–07 flying deployment craft.

## Target
- Minecraft 1.21.1
- NeoForge 21.1.172
- Java 21

## Build
Install Java 21 and Gradle 8.10.2, then run:

```sh
gradle --no-daemon build
```

The mod jar is written to `build/libs/`. GitHub Actions runs the same build and uploads a workflow artifact when compilation succeeds.

## Source model
The intended asset is the Warden AV V11 generic Blockbench model and its 512×512 texture. The source model has extensive mesh geometry, so a cube-only rebuild is not acceptable.

The conversion utility in `tools/convert_bbmodel.py` is an initial mesh/UV extraction aid. It is not yet a verified lossless importer: Blockbench group transforms, pivots, rotations, and texture/material handling still need validation against the original project before its output can be used as the final in-game model.

## Implementation status
- [x] NeoForge 1.21.1 project scaffold
- [x] Java 21 configuration and CI build workflow
- [x] Warden AV entity type registration and base entity class
- [x] Initial Blockbench mesh conversion utility
- [ ] Import and validate original Blockbench geometry, transforms, and texture
- [ ] Custom mesh renderer and spawn item
- [ ] In-game visual validation and scale/orientation tuning
- [ ] Flight controls, passenger/deployment behavior, and final release

This repository is an active development workspace. It is not yet a finished or tested release.
