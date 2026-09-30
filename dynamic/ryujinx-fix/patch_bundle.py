"""Replace ARMeilleure in a COPY of the installed .NET 6-format Linux bundle.

No app is launched. Requires an uncompressed assembly slot large enough to fit
the replacement. The other bundled files and native host remain unchanged.
Format: dotnet/runtime, Microsoft.NET.HostModel/Bundle/{Manifest,FileEntry}.cs.
"""
import argparse
import hashlib
import mmap
from pathlib import Path
import shutil
import struct

SIGNATURE = bytes.fromhex(
    '8b1202b96a612038727b930214d7a03213f5b9e6efae3318ee3b2dce24b36aae')


def read_string(file):
    length = 0
    for shift in range(0, 35, 7):
        byte = file.read(1)[0]
        length |= (byte & 127) << shift
        if byte < 128:
            if length > 4096:
                raise ValueError('Unexpected bundle string length')
            return file.read(length).decode('utf-8')
    raise ValueError('Invalid string length')


def replace(original, library, output):
    if output.exists() or output.resolve() == original.resolve():
        raise ValueError('Output must be a new file; never overwrite the installed app')
    code = library.read_bytes()
    with original.open('rb') as file, mmap.mmap(file.fileno(), 0, access=mmap.ACCESS_READ) as data:
        marker = data.find(SIGNATURE)
        if marker < 8:
            raise ValueError('Bundle signature missing')
        header = struct.unpack_from('<Q', data, marker - 8)[0]
        file.seek(header)
        major, minor, count = struct.unpack('<III', file.read(12))
        if (major, minor) != (6, 0) or not 0 < count < 4096:
            raise ValueError('Unsupported bundle format')
        read_string(file)
        file.read(40)  # deps/runtimeconfig locations and flags
        matches = []
        for _ in range(count):
            entry = file.tell()
            offset, size, compressed, kind = struct.unpack('<qqqB', file.read(25))
            if read_string(file) == 'ARMeilleure.dll':
                matches.append((entry, offset, size, compressed, kind))
        if len(matches) != 1:
            raise ValueError('Expected exactly one ARMeilleure assembly')
        entry, offset, size, compressed, kind = matches[0]
        if compressed or kind != 1 or not 0 < len(code) <= size or not 0 <= offset < offset + size <= header:
            raise ValueError('Replacement does not fit the uncompressed assembly slot')
    output.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(original, output)
    with output.open('r+b') as file:
        file.seek(offset)
        file.write(code)
        file.write(bytes(size - len(code)))
        file.seek(entry + 8)
        file.write(struct.pack('<q', len(code)))
    # Check the entire result, allowing changes only in the assembly slot and its size field.
    with original.open('rb') as before, output.open('rb') as after:
        for start, end in ((0, offset), (offset + size, entry + 8), (entry + 16, original.stat().st_size)):
            before.seek(start)
            after.seek(start)
            remaining = end - start
            while remaining:
                length = min(remaining, 1024 * 1024)
                assert before.read(length) == after.read(length), 'Unrelated bundle bytes changed'
                remaining -= length
        after.seek(offset)
        assert after.read(len(code)) == code, 'Replacement bytes differ'
    print(f'Created {output}; verified that only ARMeilleure and its size field changed.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('original', type=Path)
    parser.add_argument('library', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    expected = ((args.original, '668cf770804dfed94d5362f2334844ad7665ce7e3b3edc4659ba24e1684e5a04'),
                (args.library, '31d683cdaa4576142e6b8d912ff53eea280851eecd4293cd3a70eb23c7c7d357'))
    for path, digest in expected:
        checksum = hashlib.sha256()
        with path.open('rb') as file:
            for chunk in iter(lambda: file.read(1024 * 1024), b''):
                checksum.update(chunk)
        if checksum.hexdigest() != digest:
            parser.error(f'{path.name}: hash mismatch; this repair supports only the tested Linux x86-64 Ryujinx 1.3.3 bundle and library')
    replace(args.original, args.library, args.output)
