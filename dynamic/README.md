# TOTK 1.4.3 Dynamic 60 FPS — experimental 0.2.0

An experimental timing hook that adjusts game speed to elapsed frame time while
keeping a 60 FPS rendering cap. This is an advanced installation kit, not a
drop-in mod: generate the executable locally from your own game dump.

## Compatibility and validation

- Only TOTK **1.4.3**, title ID `0100F2C0115B6000`, build ID
  `277178B7DBA1B6D4949A84778D4ABC58B31B34F5`.
- Tested on Linux x86-64 with a locally repaired Ryujinx 1.3.3 and RTX 4090.
  **Unmodified Ryujinx 1.3.3 crashed during testing.** See
  [the included emulator repair](ryujinx-fix/README.md) before installing.
- The repaired build passed startup, save loading, movement and camera checks
  in a roughly five-minute run. Gameplay samples reached 60 FPS; no crash or
  OOM occurred during that run. This is not a long-session stability guarantee.
- Game speed against a stopwatch, physics, cutscenes, shrines and Ultrahand
  still need validation. Sustained performance below 20 FPS can slow gameplay.
  Windows, macOS, ARM64 and Switch hardware have not been tested.

## Generate your private mod

Requires Python 3 and your own **unmodified, decompressed ExeFS `main` from the
updated 1.4.3 game**. A base-game executable, compressed NSO, NSP or XCI is not
accepted. Dumping/extraction/decompression tools and game data are not included.

Expected input size: `60972640` bytes. Expected input SHA-256:
`1ff28d5d262419897f728f84e1954cefff95b14af645235e905d19f915ecf7d4`.

Extract this ZIP, open a terminal in its folder, and run:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install keystone-engine==0.9.2
.venv/bin/python build_dynamic.py /path/to/your/decompressed/main ./dynamic-60fps-1.4.3/exefs/main
```

The installer checks the entire input hash and refuses to overwrite an existing
output. Expected output SHA-256:
`7f17483047cb12a27b4aa24362a1e435f39aa9720d72bb464afe4eae175393d4`.

Close the game and back up your saves. Disable other FPS/speed mods and any mod
that replaces `exefs/main`. In Ryujinx, right-click TOTK, open **Manage Mods**,
and add the generated `dynamic-60fps-1.4.3` folder. Enable only this timing mod.
The resulting layout is `dynamic-60fps-1.4.3/exefs/main`.

To uninstall, close the game and disable/remove that folder. Your base game and
update are unchanged. Re-enable your previous FPS mod only after removing this one.

**Share this ZIP, not the generated `main` or generated mod folder.** The output
contains your game's executable. This ZIP contains no game executable, firmware,
keys, saves or diagnostic dumps.

## Source and tests

`build_dynamic.py` verifies and patches the NSO; `timing.s` contains the original
ARM64 timing hook. It extends executable padding and BSS and updates the segment
hashes. It uses the emulated ARM timer, bounds elapsed time to 1/240–1/20 second,
and falls back to 1/60 second on initialization, object changes or long pauses.
It is not a complete DynamicFPS++ port; movie and shrine-specific fixes are absent.

Optional offline tests (these do not launch the game):

```sh
.venv/bin/python -m pip install capstone==5.0.9 unicorn==2.1.4
.venv/bin/python test_dynamic.py
```

Tests execute the hook with controlled timer samples and check calculations and
register preservation. For gameplay reports include emulator version, platform,
game build, active mods, scene and reproduction steps. Never attach game files,
keys, saves or crash cores. Use disk-backed storage for diagnostic logs and keep
core dumps disabled when testing the included repair.

MIT licensed; see `LICENSE`. The emulator repair has its own license notice.
