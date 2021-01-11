#!/usr/bin/python

import copy
import sys

mem = dict()

def next_addr():
	start_size = 8000
	avail = set(_ for _ in range(start_size))
	avail.discard(0)
	while True:
		if len(avail) > 0:
			yield avail.pop()
		else:
			avail = set(_ for _ in range(start_size)).difference(set(mem.keys()))
			if len(avail) == 0:
				avail = set(_ for _ in range(start_size, start_size*2))
				start_size *= 2

if __name__ == "__main__":

	"""eight registers"""
	"""32-bits each"""
	regs = [0,0,0,0,0,0,0,0]
	stdin_buff = ''
	ip = 0

	if len(sys.argv) != 2:
		print('python '+sys.argv[0]+' <filename.umz>')
		exit()

	with open(sys.argv[1], 'rb') as infile:
		raw_data = infile.read()

	mem[0] = []
	read_idx = 0
	while(read_idx < len(raw_data)):
		mem[0].append(int.from_bytes(raw_data[read_idx:read_idx+4], byteorder='big'))
		read_idx += 4

	addr_gen = next_addr()

	while True:
		word = mem[0][ip]
		func = (word >> 28) & 0xF
		c =  word & 0x7
		b = (word >> 3) & 0x7
		a = (word >> 6) & 0x7
		if func == 0:
			if regs[c] != 0:
				regs[a] = regs[b]
		elif func == 1:
			regs[a] = mem[regs[b]][regs[c]]
		elif func == 2:
			mem[regs[a]][regs[b]] = regs[c]
		elif func == 3:
			regs[a] = (regs[b]+regs[c]) & 0xFFFFFFFF
		elif func == 4:
			regs[a] = (regs[b]*regs[c]) & 0xFFFFFFFF
		elif func == 5:
			regs[a] = (regs[b]//regs[c]) & 0xFFFFFFFF
		elif func == 6:
			regs[a] = ~(regs[b]&regs[c]) & 0xFFFFFFFF
		elif func == 7:
			exit()
		elif func == 8:
			addr = next(addr_gen)
			mem[addr] = [0 for _ in range(regs[c])]
			regs[b] = addr
		elif func == 9:
			del mem[regs[c]]
		elif func == 10:
			print(chr(regs[c]), end='')
		elif func == 11:
			while len(stdin_buff) == 0:
				stdin_buff = input()
				stdin_buff += chr(10)
			regs[c] = ord(stdin_buff[0])
			stdin_buff = stdin_buff[1:]
		elif func == 12:
			if regs[b] != 0:
				mem[0] = copy.deepcopy(mem[regs[b]])
			ip = regs[c]-1
		elif func == 13:
			regs[(word>> 25) & 0x7] = word & 0x1FFFFFF
		else:
			print("Invalid OPCODE.")
			exit()
		ip += 1
