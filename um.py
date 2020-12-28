#!/usr/bin/python

ip = 0

"""eight registers"""
"""32-bits each"""
regs = {
	0 : 0,
	1 : 0,
	2 : 0,
	3 : 0,
	4 : 0,
	5 : 0,
	6 : 0,
	7 : 0,
	8 : 0}

mem = dict()

stdin_buff = ''

"""
  Standard Operators.
  -------------------

  Each Standard Operator performs an errand using three registers,
  called A, B, and C. Each register is described by a three bit
  segment of the instruction platter. The register C is described by
  the three least meaningful bits, the register B by the three next
  more meaningful than those, and the register A by the three next
  more meaningful than those.

                                      A     C
                                      |     |
                                      vvv   vvv
              .--------------------------------.
              |VUTSRQPONMLKJIHGFEDCBA9876543210|
              `--------------------------------'
               ^^^^                      ^^^
               |                         |
               operator number           B
"""


"""
#0. Conditional Move.

The register A receives the value in register B,
unless the register C contains 0.
"""
def cond_mv(a, b, c):
	global regs
	if regs[c] != 0:
		regs[a] = regs[b]


"""
#1. Array Index.

The register A receives the value stored at offset
in register C in the array identified by B.
"""
def array_idx(a, b, c):
	global regs
	global mem
	regs[a] = mem[regs[b]][regs[c]]


"""
#2. Array Amendment.

The array identified by A is amended at the offset
in register B to store the value in register C.
"""
def array_write(a, b, c):
	global regs
	global mem
	mem[regs[a]][regs[b]] = regs[c]

"""
#3. Addition.

The register A receives the value in register B plus 
the value in register C, modulo 2^32.
"""
def add(a, b, c):
	global regs
	regs[a] = (regs[b]+regs[c]) & 0xFFFFFFFF

"""
#4. Multiplication.

The register A receives the value in register B times
the value in register C, modulo 2^32.
"""
def mult(a, b, c):
	global regs
	regs[a] = (regs[b]*regs[c]) & 0xFFFFFFFF

"""
#5. Division.

The register A receives the value in register B
divided by the value in register C, if any, where
each quantity is treated treated as an unsigned 32
bit number.
"""
def div(a, b, c):
	global regs
	regs[a] = (regs[b]//regs[c]) & 0xFFFFFFFF

"""
#6. Not-And.

Each bit in the register A receives the 1 bit if
either register B or register C has a 0 bit in that
position.  Otherwise the bit in register A receives
the 0 bit.
"""
def nand(a, b, c):
	global regs
	regs[a] = ~(regs[b]&regs[c]) & 0xFFFFFFFF

"""
#7. Halt.

The universal machine stops computation.
"""
def halt(a, b, c):
	exit()

"""
#8. Allocation.

A new array is created with a capacity of platters
commensurate to the value in the register C. This
new array is initialized entirely with platters
holding the value 0. A bit pattern not consisting of
exclusively the 0 bit, and that identifies no other
active allocated array, is placed in the B register.
"""
def alloc(a, b, c):
	global regs
	global mem
	# Locate lowest available open address
	# Or one position higher than current highest address
	addr = min(set(x for x in range(max(mem.keys())+2)).difference(set(mem.keys())))
	mem[addr] = [ 0 for x in range(regs[c]) ]
	regs[b] = addr

"""
#9. Abandonment.

The array identified by the register C is abandoned.
Future allocations may then reuse that identifier.
"""
def free(a, b, c):
	global mem
	mem.pop(regs[c])

"""
#10. Output.

The value in the register C is displayed on the console
immediately. Only values between and including 0 and 255
are allowed.
"""
def out(a, b, c):
	global regs
	print(chr(regs[c]), end='')

"""
#11. Input.

The universal machine waits for input on the console.
When input arrives, the register C is loaded with the
input, which must be between and including 0 and 255.
If the end of input has been signaled, then the 
register C is endowed with a uniform value pattern
where every place is pregnant with the 1 bit.
"""
def inpt(a, b, c):
	global regs
	global stdin_buff
	while len(stdin_buff) == 0:
		stdin_buff = input(">")
		stdin_buff += chr(0xFF)
	regs[c] = ord(stdin_buff[0])
	stdin_buff = stdin_buff[1:]


"""
#12. Load Program.

The array identified by the B register is duplicated
and the duplicate shall replace the '0' array,
regardless of size. The execution finger is placed
to indicate the platter of this array that is
described by the offset given in C, where the value
0 denotes the first platter, 1 the second, et
cetera.

The '0' array shall be the most sublime choice for
loading, and shall be handled with the utmost
velocity.
"""
def load(a, b, c):
	global regs
	global mem
	global ip
	mem[0] = [ x for x in mem[regs[b]] ]
	ip = regs[c]-1

"""

  Special Operators.
  ------------------

  One special operator does not describe registers in the same way.
  Instead the three bits immediately less significant than the four
  instruction indicator bits describe a single register A. The
  remainder twenty five bits indicate a value, which is loaded
  forthwith into the register A.

                   A  
                   |  
                   vvv
              .--------------------------------.
              |VUTSRQPONMLKJIHGFEDCBA9876543210|
              `--------------------------------'
               ^^^^   ^^^^^^^^^^^^^^^^^^^^^^^^^
               |      |
               |      value
               |
               operator number

               Figure 3. Special Operators

#13. Orthography.

The value indicated is loaded into the register A
forthwith.
"""
def load_im(a, value):
	global regs
	regs[a] = value

def read_regs(word):
	c_mask = 0x7
	b_mask = 0x7 << 3
	a_mask = 0x7 << 6
	c = word & c_mask
	b = (word & b_mask) >> 3
	a = (word & a_mask) >> 6
	return (a, b, c)

if __name__ == "__main__":

	with open("sandmark.umz", 'rb') as infile:
		raw_data = infile.read()

	mem[0] = []

	while(len(raw_data) > 0):
		mem[0].append(int.from_bytes(raw_data[0:4], byteorder='big'))
		raw_data = raw_data[4:]


	ops = [cond_mv, array_idx, array_write, add, mult, div, nand, halt, alloc, free, out, inpt, load, load_im]

	while True:
		func = ops[(mem[0][ip] & (0xF << 28)) >> 28]
		if func != load_im:
			a, b, c = read_regs(mem[0][ip])
			func(a, b, c)
		elif func == load_im:
			value = mem[0][ip] & 0x1FFFFFF
			reg   = (mem[0][ip] & (0x7 << 25)) >> 25
			func(reg, value)
		else:
			print("Invalid OPCODE.")
			exit()
		ip += 1
		ip %= len(mem[0])
