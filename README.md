# TOTK 1.4.3 — experimental 60 FPS patch

A small **static 60 FPS** ExeFS patch for *The Legend of Zelda: Tears of the Kingdom* **1.4.3**, tested locally with Ryujinx 1.3.3 on Linux.

**Status: experimental.** The patch was accepted by the emulator and raised the title screen to approximately 60 FPS. Opening-cave gameplay initially measured about 48 FPS at 2× resolution; after a restart, the tester reported roughly 60 FPS. These are observations from one machine, not a full-game benchmark or a guarantee of performance.

This is a static frame-rate patch. It does **not** provide dynamic timing compensation, a resolution patch, or a general performance optimizer. Gameplay speed, physics, animations and cutscenes across the full game have not been validated. Below 60 FPS, slowdown or timing problems are possible.

## Download and install

1. Download `60fps-1.4.3.zip` from the [release page](https://github.com/flabanabba8/totk-60fps-1.4.3/releases).
2. Stop the game before changing mods.
3. Confirm that Ryujinx launches the game with update **1.4.3**. The game title in the emulator window should show that version.
4. In Ryujinx's game list, right-click **Tears of the Kingdom** and choose **Open Mods Directory**.
5. Extract the ZIP directly into that directory. Keep the `60fps-1.4.3` folder intact.
6. Disable other FPS or timing mods for this test. If your Ryujinx build has **Manage Mods**, check that this mod is enabled there.
7. Launch the game and check its frame-rate display. Allow shader compilation and CPU translation to settle before judging performance.

The resulting directory tree must be:

```text
<game mods directory>/
└── 60fps-1.4.3/
    └── exefs/
        └── 1.4.3.pchtxt
```

Avoid an extra wrapper such as `60fps-1.4.3/60fps-1.4.3/exefs`.

### Manual paths

Using **Open Mods Directory** is preferred because data locations differ between emulator packages and portable installations. Common locations are:

| Installation | Game mods directory |
| --- | --- |
| Windows, standard Ryujinx | `%APPDATA%\Ryujinx\mods\contents\0100f2c0115b6000` |
| Linux, standard Ryujinx | `~/.config/Ryujinx/mods/contents/0100f2c0115b6000` |
| Linux, `io.github.ryubing.Ryujinx` Flatpak | `~/.var/app/io.github.ryubing.Ryujinx/config/Ryujinx/mods/contents/0100f2c0115b6000` |

Only the Linux Flatpak installation was tested for this release. Windows and other emulator builds are unverified.

## Compatibility

| Item | Requirement / status |
| --- | --- |
| Game | Tears of the Kingdom |
| Title ID | `0100F2C0115B6000` |
| Update | **1.4.3** |
| Main executable build ID | `277178B7DBA1B6D4949A84778D4ABC58B31B34F5` |
| Format | IPSwitch `.pchtxt`, installed as an ExeFS mod |
| Tested emulator | Ryujinx 1.3.3, Linux Flatpak |
| Other game versions | Unsupported; matching build ID is required |
| Other emulators | Not tested |
| Dynamic FPS / other FPS mods | Compatibility not tested; disable them for the baseline test |

A version label alone is not sufficient if an executable has a different build ID. Never rename the build ID or reuse these offsets for another update.

## Does 60 FPS speed up the game?

The intended behavior is normal game speed with smoother motion at 60 FPS. This port has not been validated against a timed 30 FPS baseline, so correct simulation speed is not established. Some timing-sensitive animations or physics could run too fast; below 60 FPS, slowdown is also possible. A frame counter alone cannot establish timing correctness.

## Resolution and GPU

Resolution scaling is controlled by the emulator, separately from this mod. The local test used **Docked mode, 2× resolution scaling**, Vulkan, and an **NVIDIA GeForce RTX 4090**. A 2× scale is not a promise of fixed 2560×1440 internal rendering; the game's own rendering behavior still matters.

To confirm the selected GPU, inspect the Ryujinx log for `Gpu PrintGpuInformation`. Our run explicitly identified `NVIDIA GeForce RTX 4090`. On NVIDIA Linux systems, `nvidia-smi` can also show the running Ryujinx process and GPU memory use.

## Known issues and troubleshooting

### Crash: `PrepoService command ID: 10107 is not implemented`

This exact exception occurred in the local Ryujinx 1.3.3 test. The exception identifies an unimplemented emulator game-reporting service; removing the FPS patch is not established as a fix for that exception.

We enabled **Ignore Missing Services** in Ryujinx's system settings and relaunched with the patch still enabled. No repeat crash was observed during the short follow-up run. This is a provisional workaround, not proof of long-term stability. A newer emulator build that implements this service may be preferable.

If your build exposes this setting only through its configuration file, close Ryujinx, back up `Config.json`, and change the existing entry to:

```json
"ignore_missing_services": true
```

Preserve the rest of the JSON file. This changes how the emulator handles missing services globally; restore the setting if it causes problems with other games. If the exception persists, report the emulator version and sanitized log excerpt.

### The game still runs at 30 FPS

- Check that update **1.4.3** is actually selected and loaded.
- Check the folder tree above and that the mod is enabled.
- Search the log for a matching IPSwitch patch named `1.4.3.pchtxt` in `60fps-1.4.3`.
- Check that the loaded build ID matches the compatibility table.
- Disable overlapping FPS or timing patches and retry.

### FPS drops or the game slows down

Wait for shader compilation to settle, then try a lower resolution scale. CPU emulation can also limit performance, so lower resolution may not improve every scene. The patch changes the requested rendering interval; it cannot make the machine sustain 60 FPS or compensate for missed frames.

### Animation, physics or cutscene problems

Disable the patch, relaunch, and repeat the same scene. If the problem disappears, leave the mod disabled and report the scene, emulator version, game build and approximate FPS. Full-game timing behavior has not been tested.

### Remove or disable the mod

Stop the game. Disable `60fps-1.4.3` in **Manage Mods**, or move its folder out of the game's mods directory. Relaunch. The patch does not modify the original NSP or install itself into your save data. Keep normal save backups while testing experimental mods.

## What was tested

Local environment: Linux/KDE, Ryzen 9 8945HS, RTX 4090, Vulkan, Ryujinx 1.3.3, firmware 22.1.0, game update 1.4.3, Docked mode, 2× scale.

| Check | Observation |
| --- | --- |
| Executable verification | Build ID and all four original instruction bytes matched |
| Emulator patch loading | Matching patch was logged and game launched as 1.4.3 |
| GPU selection | RTX 4090 confirmed in emulator log and `nvidia-smi` |
| Title screen | Approximately 56–60 FPS |
| Initial opening-cave sample | Approximately 48 FPS |
| Opening cutscene sample after restart | Approximately 53 FPS in one screenshot |
| Tester observation after restart | Roughly 60 FPS consistently in the scene being played |
| Service workaround follow-up | Relaunched successfully; no repeat crash during short observation |

These samples do not establish average FPS, frame pacing, correct simulation speed, or stability throughout the game. Outdoor areas, combat, shrines, later cutscenes and prolonged sessions remain untested.

## Technical details and verification

See [TECHNICAL.md](TECHNICAL.md) for the four instruction changes, the build check and how to regenerate the patch from your own executable.

The repository contains the patch and original support code only. No ROMs, updates, firmware, keys, executable dumps or saves are included. Supply your own game and update; this project does not obtain them.

## Reporting a problem

Open a [GitHub issue](https://github.com/flabanabba8/totk-60fps-1.4.3/issues) with:

- Game version and executable build ID.
- Emulator version, operating system, CPU, GPU and graphics backend.
- Resolution scale and a list of other enabled mods.
- Scene / reproduction steps and whether the problem occurs with this mod disabled.
- A short, sanitized log excerpt showing patch loading or the exception.

Do not attach keys, game files, executable dumps, saves or complete logs containing private data.

## Credits and license

This port started from a locally supplied four-instruction 1.0.0 60 FPS patch. Its author was not identifiable from the supplied file; this project does not claim to have invented the underlying interval-patching technique. The 1.4.3 offsets were located by comparing instruction patterns and inspecting the updated ARM64 code. Attribution can be corrected if the original author is identified.

Original support code and this repository's authored documentation and patch contributions are provided under the [MIT license](LICENSE). This license does not grant rights to Nintendo game content or third-party material. This is an independent project with no affiliation with Nintendo or Ryujinx.
