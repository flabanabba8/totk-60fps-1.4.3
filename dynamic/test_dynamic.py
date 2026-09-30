"""Execute the actual ARM64 hook against controlled clock samples with Unicorn."""
import struct
import unittest
from capstone import Cs, CS_ARCH_ARM64, CS_MODE_LITTLE_ENDIAN
from unicorn import Uc, UC_ARCH_ARM64, UC_MODE_ARM, UC_HOOK_CODE
from unicorn.arm64_const import *
from build_dynamic import assemble, CAVE, STATE, HOOK


def float_bits(value):
    return struct.unpack('<I', struct.pack('<f', value))[0]


def as_float(value):
    return struct.unpack('<f', struct.pack('<I', value & 0xFFFFFFFF))[0]


class TimingTest(unittest.TestCase):
    def execute(self, seconds, previous=19200000, old_object=0x100000):
        code, _ = assemble()
        vm = Uc(UC_ARCH_ARM64, UC_MODE_ARM)
        for address, size in ((CAVE & ~4095, 4096), (STATE, 4096),
                              (HOOK & ~4095, 4096), (0x100000, 4096),
                              (0x200000, 8192)):
            vm.mem_map(address, size)
        vm.mem_write(CAVE, code)
        vm.mem_write(STATE, struct.pack('<QQ', previous, old_object))
        vm.reg_write(UC_ARM64_REG_SP, 0x201000)
        vm.reg_write(UC_ARM64_REG_X0, 0x100000)
        for register in (UC_ARM64_REG_X8, UC_ARM64_REG_X9, UC_ARM64_REG_X10, UC_ARM64_REG_X11):
            vm.reg_write(register, 0x123456789ABC)
        vm.reg_write(UC_ARM64_REG_Q2, float_bits(0.5))
        vm.reg_write(UC_ARM64_REG_Q3, 0xABCD1234)
        now = previous + round(seconds * 19200000)
        instructions = {i.address: i for i in Cs(CS_ARCH_ARM64, CS_MODE_LITTLE_ENDIAN).disasm(code, CAVE)}
        def clock(machine, address, size, _):
            instruction = instructions.get(address)
            if instruction and instruction.mnemonic == 'mrs':
                if 'cntpct_el0' in instruction.op_str:
                    machine.reg_write(UC_ARM64_REG_X8, now)
                else:
                    machine.reg_write(UC_ARM64_REG_X11, 19200000)
                machine.reg_write(UC_ARM64_REG_PC, address + 4)
        vm.hook_add(UC_HOOK_CODE, clock)
        vm.emu_start(CAVE, HOOK + 4, count=200)
        self.assertEqual(vm.reg_read(UC_ARM64_REG_PC), HOOK + 4)
        self.assertEqual(vm.reg_read(UC_ARM64_REG_SP), 0x201000)
        self.assertEqual(vm.reg_read(UC_ARM64_REG_X0), 0x100000)
        for register in (UC_ARM64_REG_X8, UC_ARM64_REG_X9, UC_ARM64_REG_X10, UC_ARM64_REG_X11):
            self.assertEqual(vm.reg_read(register), 0x123456789ABC)
        self.assertEqual(vm.reg_read(UC_ARM64_REG_Q2), float_bits(0.5))
        self.assertEqual(vm.reg_read(UC_ARM64_REG_Q3), 0xABCD1234)
        self.assertEqual(struct.unpack('<QQ', vm.mem_read(STATE, 16)), (now, 0x100000))
        return as_float(vm.reg_read(UC_ARM64_REG_S0)), as_float(vm.reg_read(UC_ARM64_REG_S1))

    def test_variable_frame_rates(self):
        for fps in (20, 30, 45, 60, 120, 240):
            with self.subTest(fps=fps):
                interval, speed = self.execute(1/fps)
                self.assertAlmostEqual(interval, 60/fps, places=4)
                self.assertAlmostEqual(speed, 30/fps, places=4)

    def test_hitch_limit(self):
        for seconds in (0.1, 0.5):
            interval, speed = self.execute(seconds)
            self.assertAlmostEqual(interval, 3, places=5)
            self.assertAlmostEqual(speed, 1.5, places=5)

    def test_reset_and_pause(self):
        for kwargs in ({'seconds': 2}, {'seconds': 0}, {'seconds': -0.01},
                       {'seconds': 0.01, 'previous': 0},
                       {'seconds': 0.01, 'old_object': 0x100100}):
            interval, speed = self.execute(**kwargs)
            self.assertAlmostEqual(interval, 1, places=5)
            self.assertAlmostEqual(speed, 0.5, places=5)

    def test_maximum_rate(self):
        interval, speed = self.execute(0.001)
        self.assertAlmostEqual(interval, 0.25, places=5)
        self.assertAlmostEqual(speed, 0.125, places=5)


if __name__ == '__main__':
    unittest.main()
