# TOTK 1.4.3 — Dynamic 60 FPS

An experimental dynamic timing mod for *The Legend of Zelda: Tears of the
Kingdom* **1.4.3**. It adjusts the game's frame interval using elapsed time while
retaining a 60 FPS rendering cap. This replaces this project's earlier static
FPS patch as the active implementation.

**[Download v0.2.0](https://github.com/flabanabba8/totk-60fps-1.4.3/releases/tag/v0.2.0)**
· **[Installation instructions](dynamic/README.md)**
· **[Timing source](dynamic/timing.s)**
· **[Installer source](dynamic/build_dynamic.py)**

## Before installing

This is a local build kit, not a drop-in patch. You need Python 3 and your own
unmodified, decompressed ExeFS `main` from game update **1.4.3**. The installer
checks its full hash before generating your private `exefs/main`. The generated
file contains game code and must not be redistributed. No game files, keys,
firmware or saves are included in the repository or release kit.

**Unmodified Ryujinx 1.3.3 crashed during testing.** The successful run used a
Linux x86-64 cache repair included in the release, with its
[source patch and instructions](dynamic/ryujinx-fix/README.md). That repair accepts
only the exact tested emulator binary. Other emulator builds and platforms are
unverified. Read the compatibility notes before changing your setup.

## Upgrade from the static mod

1. Close the game and back up your saves.
2. Disable/remove `60fps-1.4.3` and other FPS/speed mods, including any mod that
   replaces `exefs/main`.
3. Download the **v0.2.0 release ZIP** and follow its README to generate
   `dynamic-60fps-1.4.3/exefs/main` from your own executable.
4. Add that generated folder in Ryujinx's **Manage Mods** and enable it in the
   profile you use with the compatible emulator.

The base game and update are unchanged. To uninstall, close the game and disable
or remove the generated mod folder. Do not enable static and dynamic timing mods
together. The old implementation is retained under [legacy-static](legacy-static/)
for reference; its v0.1.0 release is superseded.

## What is validated

- Offline tests execute the ARM64 hook against controlled timer samples at
  20/30/45/60/120/240 FPS, checking calculations, hitch/pause handling and
  register preservation.
- The release kit reproduced the exact mod executable and repaired emulator used
  in the successful test. Wrong-input and overwrite rejection checks passed.
- A roughly five-minute smoke test on Linux with an RTX 4090 passed startup,
  save loading, movement and camera input. Gameplay samples reached 60 FPS at
  Docked 2× resolution, with no runtime crash or OOM in that run.

**Still experimental:** stopwatch comparisons of game speed, physics, cutscenes,
shrines, Ultrahand and long-session stability remain unverified. Performance below
20 FPS can still slow gameplay. This is not a complete DynamicFPS++ port or a
guarantee that your hardware will sustain 60 FPS.

## Source, tests and packaging

The active source lives in [dynamic](dynamic/). From that directory:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install keystone-engine==0.9.2 capstone==5.0.9 unicorn==2.1.4
.venv/bin/python test_dynamic.py
```

The [emulator repair directory](dynamic/ryujinx-fix/) includes the cache patch,
.NET build project, regression test, bundle patcher and upstream license.
The release ZIP supplies the tested compiled repair library; it is not tracked
as a binary in Git. To recreate the kit from the repository root, use that DLL
(or rebuild and verify it as described in the repair documentation):

```sh
python3 dynamic/package_release.py /path/to/ARMeilleure.dll
```

This writes a ZIP and checksum under `dist/` using an explicit file allowlist.
It never packages a game executable or starts the emulator.

## Reports and license

[Report an issue](https://github.com/flabanabba8/totk-60fps-1.4.3/issues) with your
game/emulator versions, platform, active mods, scene and reproduction steps.
Attach only short, sanitized log excerpts; keep game files, keys, saves and
crash dumps private.

The timing hook is original code informed by studying
[DynamicFPS++](https://github.com/MaxLastBreath/TOTK-DFPS); it is not a full port.
Rendering-interval changes retain the approach documented in the
[legacy technical notes](legacy-static/TECHNICAL.md). The supplied older patch's
original author was not identifiable; attribution can be corrected if identified.
Project-authored code is [MIT licensed](LICENSE), and the emulator repair retains
the [Ryujinx license](dynamic/ryujinx-fix/LICENSE-Ryujinx.txt). This project is not
affiliated with Nintendo or Ryujinx.
