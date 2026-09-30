# Ryujinx 1.3.3 Linux x86-64 experimental cache repair

This optional developer repair contains `ARMeilleure.dll`, its source patch,
regression test and a Python bundle patcher. It was used for the successful
smoke test of the accompanying TOTK mod. It is not an official Ryujinx release.

The original cache can free an old region's function through a different region's
allocator, overwriting live code. The regression reproduces this; the included
patch keeps entries and allocation ownership per region. It also clears metadata
on cache reset. The repaired library passes all three regression checks.

The corresponding upstream work is
[instanced jit cache (#152)](https://git.h3cjp.net/H3cJP/ryujinx/commit/6fb71b08aeee2ddc310b5a0412d486928c2d1d90).
A newer emulator incorporating that fix may make this repair unnecessary, but
other versions were not tested with this mod.

## Supported binary

Only the tested Linux x86-64 Ryujinx 1.3.3 bundle is accepted. SHA-256:
`668cf770804dfed94d5362f2334844ad7665ce7e3b3edc4659ba24e1684e5a04`.

The supplied DLL has SHA-256:
`31d683cdaa4576142e6b8d912ff53eea280851eecd4293cd3a70eb23c7c7d357`.
The Python command checks both hashes before writing. A mismatch means this
repair is incompatible; do not bypass that check. Windows and ARM64 were not tested.

## Apply to a separate copy

Use a disk-backed working directory. Copy your installed emulator's entire
`bin` directory, including native libraries and companion files, to a new
directory such as `repaired-emulator`. Rename **the copy's** `Ryujinx` executable
to `Ryujinx.original`. From this kit's `ryujinx-fix` directory run:

```sh
python3 patch_bundle.py /path/to/repaired-emulator/Ryujinx.original ARMeilleure.dll /path/to/repaired-emulator/Ryujinx
```

This patches the copy only and does not launch anything. The resulting executable
SHA-256 should be:
`e78907f63d2b8efdf9c35da47370f482faa6932d1e8443905577fe93fa1dd477`.
The script verifies all other bundle bytes are unchanged. The host needs the
native dependencies required by the copied emulator; Flatpak's sandbox libraries
are not automatically available when running its executable outside Flatpak.

Use a separate profile directory with `--root-data-dir /path/to/test-profile`.
With Ryujinx closed, copy your own existing profile there if you want its saves
and firmware, and back up the saves first. Do not copy old shader or translation
caches. Add the generated mod to this test profile.

On a Linux system with systemd user scopes, a launch matching the test's resource
limits looks like this. Replace the example paths with existing **disk-backed**
directories; verify with `findmnt -T /path/to/disk-work` before running:

```sh
mkdir -p /path/to/disk-work/tmp /path/to/disk-work/logs
ulimit -c 0
export TMPDIR=/path/to/disk-work/tmp
export DOTNET_BUNDLE_EXTRACT_BASE_DIR=/path/to/disk-work/tmp/bundles
export DOTNET_DbgEnableMiniDump=0 COMPlus_DbgEnableMiniDump=0
systemd-run --user --scope -p MemoryMax=8G -p MemorySwapMax=0 \
  /path/to/repaired-emulator/Ryujinx --root-data-dir /path/to/test-profile \
  > /path/to/disk-work/logs/ryujinx.log 2>&1
```

Leave at least 10 GiB of RAM available before starting. The 8 GiB limit can
terminate the emulator if it needs more memory; it protects the rest of the
desktop, and is not a guarantee of game stability. Verify that the system applies
the limit. To revert, use your original emulator and profile.

## Source and offline regression

Obtain the [Ryujinx 1.3.3 source](https://git.h3cjp.net/H3cJP/ryujinx/archive/1.3.3.tar.gz)
and .NET SDK 9. Apply `region-ownership.patch` from the source root with
`git apply /path/to/region-ownership.patch`. From this directory run:

```sh
dotnet run --project CacheRegression.csproj -c Release -p:RyujinxSource=/path/to/ryujinx
```

The original source fails the cross-region check; the patched source prints three
PASS lines. The test maps inert bytes and does not start a game.
`PatchedLibrary.csproj` builds the supplied library from the repaired source:

```sh
dotnet build PatchedLibrary.csproj -c Release \
  -p:RyujinxSource=/path/to/ryujinx \
  -p:OriginalAssemblies=/path/to/extracted-original-managed-assemblies
```

`OriginalAssemblies` must contain the managed dependencies extracted from that
exact original .NET bundle. Bundle extraction tooling is not included. Assembly
version is 1.3.3.0. See `LICENSE-Ryujinx.txt` for the upstream MIT license.
