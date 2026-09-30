# Patch notes and reproducibility

## Target

- Game: Tears of the Kingdom 1.4.3.
- Main NSO build ID: `277178B7DBA1B6D4949A84778D4ABC58B31B34F5`.
- SHA-256 of the **decompressed NSO used in development**: `1ff28d5d262419897f728f84e1954cefff95b14af645235e905d19f915ecf7d4`.

The hash describes the development input, not an NSP, an update package or every possible decompression tool's output. The verifier checks the NSO magic, build ID and original instruction bytes rather than requiring this full-file hash.

## Instruction changes

Addresses below are text-relative offsets. Hex bytes are in little-endian file order.

| Offset | Original bytes / instruction | Replacement bytes / instruction | Intended effect |
| --- | --- | --- | --- |
| `0x002DB2DC` | `A11E0012` / `and w1, w21, #0xff` | `21008052` / `mov w1, #1` | Request one tick at the rendering interval call |
| `0x00BE1BF4` | `211C0012` / `and w1, w1, #0xff` | `21008052` / `mov w1, #1` | Request one tick in the shared interval setter |
| `0x002DB21C` | `F503092A` / `mov w21, w9` | `35008052` / `mov w21, #1` | Force the retained adaptive interval to one |
| `0x002DB364` | `F5030A2A` / `mov w21, w10` | `35008052` / `mov w21, #1` | Force this increased-interval path to one |

The `.pchtxt` uses `@flag offset_shift 0x100` for the NSO header. The verification script likewise reads each instruction at `offset + 0x100` in a decompressed NSO with the expected text layout.

The intended result is a one-tick interval on the game's 60 Hz timing base. This is a static port of the earlier four-site approach. It is not a comprehensive timing analysis: there may be other interval paths or timing-sensitive systems that require changes. An observed 60 FPS counter alone does not prove correct game speed.

## Regenerate from your own executable

Python 3.9 or later is sufficient; no third-party Python packages are needed.

You must provide your own already-decompressed `main` NSO for the exact build above. Extraction, decryption and obtaining game files are outside this repository. A compressed NSO or a different text layout will fail instruction verification.

```sh
python3 make_patch.py /path/to/your/decompressed/main
```

The script verifies the input before writing `60fps-1.4.3/exefs/1.4.3.pchtxt`. It prints the input hash for comparison. It never modifies the supplied executable.

Run the offline consistency check from the repository directory:

```sh
python3 -m unittest test_patch.py
```

This check uses synthetic bytes to test build/instruction rejection and compares the generated patch text with the shipped file. It requires no game files and does not test gameplay behavior.

## Package locally

From the repository directory, use Python's standard-library ZIP tool:

```sh
python3 -m zipfile -c 60fps-1.4.3.zip 60fps-1.4.3
python3 -m zipfile -t 60fps-1.4.3.zip
```

The release ZIP contains only the mod folder. Documentation and verification tools stay in the repository. Release checksums are supplied alongside the ZIP.

## Development provenance

A local 1.0.0 patch supplied four earlier instruction locations. Candidate locations in 1.4.3 were found through normalized instruction-pattern comparison, then inspected with Capstone. The updated SDK placed interval initialization in a shared setter. The four original bytes were verified against the target executable before producing this port.

No game-derived binaries or extraction tools are distributed here. There is no automatic support for another update: each new build needs fresh analysis and testing.
