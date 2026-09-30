"""Small offline check: no game executable or third-party packages needed."""
import unittest
from pathlib import Path
from make_patch import BUILD, CHANGES, patch_text, verify


class PatchCheck(unittest.TestCase):
    def test_patch_and_rejection(self):
        binary = bytearray(max(a for a, _, _ in CHANGES) + 0x104)
        binary[:4] = b'NSO0'
        binary[0x40:0x54] = bytes.fromhex(BUILD)
        for address, before, _ in CHANGES:
            binary[address + 0x100:address + 0x104] = bytes.fromhex(before)
        verify(binary)
        shipped = Path(__file__).parent / '60fps-1.4.3/exefs/1.4.3.pchtxt'
        self.assertEqual(shipped.read_text(encoding='utf-8'), patch_text())
        binary[0x40] ^= 1
        with self.assertRaisesRegex(ValueError, 'build'):
            verify(binary)
        binary[0x40] ^= 1
        binary[CHANGES[0][0] + 0x100] ^= 1
        with self.assertRaisesRegex(ValueError, 'instruction'):
            verify(binary)
        with self.assertRaisesRegex(ValueError, 'NSO'):
            verify(b'')


if __name__ == '__main__':
    unittest.main()
