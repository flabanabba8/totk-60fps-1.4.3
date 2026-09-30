"""Verify a user-supplied decompressed NSO and regenerate the 1.4.3 patch."""
import argparse
import hashlib
from pathlib import Path

BUILD = '277178B7DBA1B6D4949A84778D4ABC58B31B34F5'
CHANGES = [
    (0x2DB2DC, 'a11e0012', '21008052'),  # rendering interval argument
    (0xBE1BF4, '211c0012', '21008052'),  # shared interval setter
    (0x2DB21C, 'f503092a', '35008052'),  # retained interval
    (0x2DB364, 'f5030a2a', '35008052'),  # increased interval
]


def verify(binary):
    if binary[:4] != b'NSO0':
        raise ValueError('Expected a decompressed NSO executable')
    if binary[0x40:0x54].hex().upper() != BUILD:
        raise ValueError('Executable build does not match TOTK 1.4.3')
    for address, before, after in CHANGES:
        if binary[address + 0x100:address + 0x104] != bytes.fromhex(before):
            raise ValueError(f'Original instruction mismatch at 0x{address:08X}')
        if len(bytes.fromhex(after)) != 4:
            raise ValueError('Replacement must be one ARM64 instruction')


def patch_text():
    return '\n'.join([
        f'@nsobid-{BUILD}',
        '// Experimental local static 60 FPS port. Not a dynamic FPS fix.',
        '@flag offset_shift 0x100',
        '@enabled',
        *(f'{address:08X} {after.upper()}' for address, _, after in CHANGES),
        '@stop', '',
    ])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('main', type=Path, help='Your decompressed TOTK 1.4.3 main NSO')
    args = parser.parse_args()
    binary = args.main.read_bytes()
    try:
        verify(binary)
    except ValueError as error:
        parser.error(str(error))
    out = Path(__file__).parent / '60fps-1.4.3' / 'exefs' / '1.4.3.pchtxt'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(patch_text(), encoding='utf-8')
    print('Verified build and all four original instructions.')
    print('Executable SHA256:', hashlib.sha256(binary).hexdigest())
    print('Patch:', out)
