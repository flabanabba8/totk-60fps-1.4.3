// Exercises the real cache allocator with inert bytes. Never executes guest code.
using System;
using System.Runtime.InteropServices;
using ARMeilleure.CodeGen;
using ARMeilleure.Translation.Cache;
using Ryujinx.Cpu.Jit;

const int RegionSize = 256 * 1024 * 1024;

static nint Map(int size, byte marker)
{
    byte[] bytes = new byte[size];
    bytes[0] = marker;
    return JitCache.Map(new CompiledFunction(bytes, default, default));
}

static void Require(bool condition, string message)
{
    if (!condition)
    {
        Console.WriteLine("FAIL: " + message);
        Environment.Exit(1);
    }
}

JitCache.Initialize(new JitMemoryAllocator());
nint oldRegionFunction = Map(32, 0x11);
Map(RegionSize - 32, 0x22);
nint liveFunction = Map(64, 0x33); // Forces a second region, reusing offset zero.
JitCache.Unmap(oldRegionFunction);
nint replacement = Map(16, 0x44);
Require(replacement != liveFunction && Marshal.ReadByte(liveFunction) == 0x33,
    "Freeing a function in region 0 overwrote a live function in region 1.");
Console.WriteLine("PASS: freeing an older region preserves the active region's code.");

JitCache.Unmap(liveFunction);
nint reused = Map(64, 0x55);
Require(reused == liveFunction, "Freed space in the active region was not reclaimed.");
Require(Marshal.ReadByte(replacement) == 0x44,
    "Equal offsets in different regions caused the wrong allocation size to be freed.");
Console.WriteLine("PASS: equal offsets retain separate sizes and can be reused safely.");

JitCache.Initialize(new JitMemoryAllocator());
Require(!JitCache.TryFind(0, out _, out _), "Cache metadata survived a complete reset.");
Console.WriteLine("PASS: resetting the cache also clears its metadata.");
