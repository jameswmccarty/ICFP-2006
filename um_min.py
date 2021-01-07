#!/usr/bin/python

import copy


if __name__ == "__main__":

	"""eight registers"""
	"""32-bits each"""
	regs = [0,0,0,0,0,0,0,0]
	mem = dict()
	used_addrs = {0}
	stdin_buff = ''
	ip = 0

	with open("sandmark.umz", 'rb') as infile:
		raw_data = infile.read()

	mem[0] = []

	while(len(raw_data) > 0):
		mem[0].append(int.from_bytes(raw_data[0:4], byteorder='big'))
		raw_data = raw_data[4:]

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
			addr = min(set(_ for _ in range(max(used_addrs)+2)).difference(used_addrs))
			used_addrs.add(addr)
			if addr > 0xFFFFFFFF:
				print("Out of Memory condition.")
				exit()
			mem[addr] = [0]*regs[c]
			regs[b] = addr
		elif func == 9:
			used_addrs.remove(regs[c])
			del mem[regs[c]]
		elif func == 10:
			print(chr(regs[c]), end='')
		elif func == 11:
			while len(stdin_buff) == 0:
				stdin_buff = input()
				stdin_buff += chr(0xFF)
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
