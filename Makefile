#Makefile for Universal Machine

CC = gcc
CFLAGS = -ansi -pedantic -Werror -Wall -O3
LFLAGS = 

all: um

um: um.c
	$(CC) $(CFLAGS) um.c -o um $(LFLAGS)

debug: um.c
	$(CC) -ansi -pedantic -Werror -Wall -g -O0 um.c -o um $(LFLAGS)

clean:
	\rm um
