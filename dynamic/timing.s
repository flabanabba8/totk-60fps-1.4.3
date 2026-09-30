// TOTK 1.4.3 timing hook. Tokens are substituted by build_dynamic.py.
// Input s0 is a frame interval; x0 is the game's timing object.
// Preserve scratch registers, change s0 to elapsed seconds * 60,
// then reproduce the displaced fmul s1, s0, s2.
stp x8, x9, [sp, #-96]!
stp x10, x11, [sp, #16]
stp q2, q3, [sp, #32]
mrs x8, cntpct_el0
adrp x9, STATE_PAGE
add x9, x9, STATE_LOW
ldp x10, x11, [x9]
stp x8, x0, [x9]
cbz x10, fallback
cmp x11, x0
b.ne fallback
subs x10, x8, x10
b.ls fallback
ucvtf s0, x10
mrs x11, cntfrq_el0
cbz x11, fallback
ucvtf s3, x11
fdiv s0, s0, s3
fmov s3, #1.0
fcmp s0, s3
b.ge fallback
ldr s3, maximum_dt
fmin s0, s0, s3
ldr s3, minimum_dt
fmax s0, s0, s3
b convert
fallback:
ldr s0, nominal_dt
convert:
ldr s3, sixty
fmul s0, s0, s3
ldp q2, q3, [sp, #32]
ldp x10, x11, [sp, #16]
ldp x8, x9, [sp], #96
fmul s1, s0, s2
b RETURN_ADDRESS
nominal_dt:
.word 0x3c888889
maximum_dt:
.word 0x3d4ccccd
minimum_dt:
.word 0x3b888889
sixty:
.word 0x42700000
