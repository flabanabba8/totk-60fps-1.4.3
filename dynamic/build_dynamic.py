"""Generate a private ExeFS override from the user's decompressed 1.4.3 NSO.

The output contains Nintendo executable data. Never upload or distribute it.
Only this builder and its original hook source may be shared.
"""
import argparse
import hashlib
import struct
from pathlib import Path
from keystone import Ks, KS_ARCH_ARM64, KS_MODE_LITTLE_ENDIAN

BUILD = '277178B7DBA1B6D4949A84778D4ABC58B31B34F5'
ORIGINAL_SHA256 = '1ff28d5d262419897f728f84e1954cefff95b14af645235e905d19f915ecf7d4'
HOOK = 0x3E6818
CAVE = 0x2BB9C00
STATE = 0x3ADF000
CAP = [(0x2DB2DC, 'a11e0012', '21008052'),
       (0xBE1BF4, '211c0012', '21008052'),
       (0x2DB21C, 'f503092a', '35008052'),
       (0x2DB364, 'f5030a2a', '35008052')]


def assemble():
    source = Path(__file__).with_name('timing.s').read_text()
    # Keystone's parser does not accept // comments.
    source = '\n'.join(line.split('//')[0] for line in source.splitlines())
    source = source.replace('STATE_PAGE', hex(STATE & ~0xFFF))
    source = source.replace('STATE_LOW', hex(STATE & 0xFFF))
    source = source.replace('RETURN_ADDRESS', hex(HOOK + 4))
    assembler = Ks(KS_ARCH_ARM64, KS_MODE_LITTLE_ENDIAN)
    code, _ = assembler.asm(source, addr=CAVE)
    branch, _ = assembler.asm(f'b {CAVE:#x}', addr=HOOK)
    return bytes(code), bytes(branch)


def build(original):
    if hashlib.sha256(original).hexdigest() != ORIGINAL_SHA256:
        raise ValueError('Expected the verified, unmodified decompressed TOTK 1.4.3 main NSO')
    if original[0x40:0x54].hex().upper() != BUILD:
        raise ValueError('Build ID mismatch')
    result = bytearray(original)
    text_file, text_address, text_size = struct.unpack_from('<III', result, 0x10)
    ro_file, ro_address, ro_size = struct.unpack_from('<III', result, 0x20)
    data_file, data_address, data_size = struct.unpack_from('<III', result, 0x30)
    bss_size = struct.unpack_from('<I', result, 0x3C)[0]
    if data_address + data_size + bss_size != STATE or text_size != CAVE:
        raise ValueError('Unexpected NSO memory layout')
    code, branch = assemble()
    if len(code) > ro_address - CAVE:
        raise ValueError('Hook exceeds executable padding')
    cave_file = text_file + CAVE - text_address
    if any(result[cave_file:cave_file + len(code)]):
        raise ValueError('Expected zero executable padding')
    hook_file = text_file + HOOK - text_address
    if result[hook_file:hook_file+4] != bytes.fromhex('0108221e'):
        raise ValueError('Timing instruction mismatch')
    result[cave_file:cave_file + len(code)] = code
    result[hook_file:hook_file+4] = branch
    for address, before, after in CAP:
        offset = text_file + address - text_address
        if result[offset:offset+4] != bytes.fromhex(before):
            raise ValueError(f'Cap instruction mismatch: {address:#x}')
        result[offset:offset+4] = bytes.fromhex(after)
    # Extend text into existing alignment padding, and allocate 16 private BSS bytes.
    new_text_size = text_size + len(code)
    struct.pack_into('<I', result, 0x18, new_text_size)
    struct.pack_into('<I', result, 0x60, new_text_size)
    struct.pack_into('<I', result, 0x3C, bss_size + 16)
    mod_address = struct.unpack_from('<I', result, text_file + 4)[0]
    mod_file = ro_file + mod_address - ro_address
    if result[mod_file:mod_file+4] != b'MOD0':
        raise ValueError('MOD0 header missing')
    mod_bss_end = struct.unpack_from('<I', result, mod_file + 0xC)[0]
    if mod_address + mod_bss_end != STATE - 0x30:
        raise ValueError('MOD0 BSS boundary mismatch')
    struct.pack_into('<I', result, mod_file + 0xC, STATE + 16 - mod_address)
    # The supplied NSO is uncompressed; refresh both modified segment hashes.
    for header, offset, size in ((0xA0, text_file, new_text_size),
                                  (0xC0, ro_file, ro_size),
                                  (0xE0, data_file, data_size)):
        result[header:header+32] = hashlib.sha256(result[offset:offset+size]).digest()
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('main', type=Path)
    parser.add_argument('output', type=Path, help='Private output file named main')
    args = parser.parse_args()
    if args.output.exists() or args.output.resolve() == args.main.resolve():
        parser.error('Output must be a new file; never overwrite your original main')
    if args.main.stat().st_size != 60972640:
        parser.error('Expected the 60,972,640-byte decompressed TOTK 1.4.3 main')
    result = build(args.main.read_bytes())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('xb') as output:
        output.write(result)
    print(f'Built {args.output} ({len(result):,} bytes). Keep this file private.')
    print('SHA256:', hashlib.sha256(result).hexdigest())
