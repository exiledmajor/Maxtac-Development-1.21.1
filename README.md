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

The GitHub Actions workflow fetches the authoritative V11 `.bbmodel` and 512×512 texture from the public `Reference-2` repository, runs the mesh conversion utility, and packages the generated assets into the mod jar. Successful CI builds are uploaded as workflow artifacts.

## In-game testing
Once a build containing the renderer passes CI, install the jar on a NeoForge 1.21.1 client and use:

```
/summon maxtac_development:warden_av ~ ~1 ~
```

The entity is currently a static, no-gravity display entity. Flight controls, passengers, deployment behavior, collision tuning, and sound are not implemented.

## Source model and conversion limitations
The source is the Warden AV V11 generic Blockbench model. The initial converter extracts mesh faces, triangulates polygons, and carries UV coordinates into a runtime mesh resource. It does not yet fully reproduce Blockbench group transforms, pivots, rotations, or all material semantics. The resulting in-game appearance must be visually compared with the source and corrected before calling the model integration final.

## Implementation status
- [x] NeoForge 1.21.1 project scaffold and CI
- [x] Warden AV entity registration and base entity
- [x] CI retrieval of original V11 model and texture
- [x] Initial mesh/UV conversion pipeline
- [x] Initial client-side textured mesh renderer
- [ ] Confirm renderer compiles and verify model in-game
- [ ] Validate transforms, scale, orientation, and texture appearance
- [ ] Add spawn item and flight/passenger/deployment behavior
- [ ] In-game playtest and release

This is an active development workspace, not yet a verified playtest release.
