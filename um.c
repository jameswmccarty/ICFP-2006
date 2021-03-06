#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <malloc.h>

#define BUFFMAX 2048
#define ADDRBUFFER 4000

unsigned int ip = 0;
unsigned int regs[8] = {0};
char stdinbuff[BUFFMAX] = {0};

/* memory management */
unsigned int **addrmap;
unsigned int  *sizemap;
unsigned int start_size = ADDRBUFFER;

unsigned int insert_addr(unsigned int *input, unsigned int size) {
	unsigned static int bookmark = 0;
	unsigned int i, t;
	for(;bookmark<start_size; bookmark++) {
		if(addrmap[bookmark] == NULL) {
			addrmap[bookmark] = input;
			sizemap[bookmark] = size;
			i = bookmark;
			return i;
		}
	}
	/* overran buffer size */
	for(i=0;i<start_size;i++) {
		if(addrmap[i] == NULL) {
			addrmap[i] = input;
			sizemap[i] = size;
			bookmark = i;
			return i;
		}
	}
	/* all other addresses exhausted */

	start_size *= 2;
	t = i;
	addrmap = (unsigned int **) realloc(addrmap, start_size*sizeof(unsigned int *));
	if(addrmap == NULL) {
		printf("Realloc Failed in insert_addr.\n");
	}
	sizemap = (unsigned int*) realloc(sizemap, start_size*sizeof(unsigned int));
	if(sizemap == NULL) {
		printf("Realloc Failed in insert_addr.\n");
	}
	addrmap[t] = input;
	sizemap[t] = size;
	for(i=t+1; i<start_size; i++) {
		addrmap[i] = NULL;
		sizemap[i] = 0;
	}
	bookmark = t+1;
	return t;
}

unsigned int byteswap(unsigned int b) {
	return	((b>>24) & 0xFF) |
			((b>>8) & 0xFF00) |
			((b<<24) & 0xFF000000) |
			((b<<8) & 0xFF0000);
}

int main(int argc, char **argv) {

	FILE *infile;
	unsigned int in_idx = 0; /* index input buffer */
	unsigned int a, b, c; /* register values */
	unsigned int *t; /* holds calloc'd pointer */

	if(argc != 2) {
		printf("Usage: %s <program.umz>\n", argv[0]);
		return 0;
	}

	/* read input file into the mem buffer */
	infile = fopen(argv[1],"rb");
	if(!infile) {
		printf("Unable to open file!\n");
		return 1;
	}
	fseek(infile, 0L, SEEK_END);
	ip = (unsigned int) ftell(infile);
	fseek(infile, 0L, SEEK_SET);

	addrmap = (unsigned int **) calloc(start_size, sizeof(unsigned int *));
	if(addrmap == NULL) {
		printf("Calloc failed.\n");
		return -1;
	}

	sizemap = (unsigned int *) calloc(start_size, sizeof(unsigned int));
	if(sizemap == NULL) {
		printf("Calloc failed.\n");
		return -1;
	}
	addrmap[0] = (unsigned int *) malloc(ip/4 * sizeof(unsigned int));
	sizemap[0] = ip/4 * sizeof(unsigned int);

	if(addrmap[0] == NULL) {
		printf("Malloc failed.\n");
		return -1;
	}
	while(in_idx < ip/4) {
		if(fread(&b, sizeof(unsigned int), 1, infile) != 1) {
			printf("Error reading input file.\n");
			return -1;
		}
		addrmap[0][in_idx++] = byteswap(b);
	}
	/* done reading inputs */
	fclose(infile);
	in_idx = 0;
	ip = 0;

	while(1) {
		/* prep register values for the cycle */
		c = addrmap[0][ip] & 0x7;
		b = (addrmap[0][ip] >> 3) & 0x7;
		a = (addrmap[0][ip] >> 6) & 0x7;
		switch((addrmap[0][ip] >> 28) & 0xF) { /* read OPCODE */
			case 0: /* Conditional Move */
				if(regs[c] != 0) {
					regs[a] = regs[b];
				}
				break;
			case 1: /* Array Index */
				regs[a] = addrmap[regs[b]][regs[c]];
				break;
			case 2: /* Array Amendment */
				addrmap[regs[a]][regs[b]] = regs[c];
				break;
			case 3: /* Addition */
				regs[a] = (regs[b]+regs[c]) & 0xFFFFFFFF;
				break;
			case 4: /* Multiplication */
				regs[a] = (regs[b]*regs[c]) & 0xFFFFFFFF;
				break;
			case 5: /* Division */
				if(regs[c] == 0) {
					printf("Caught DIV by Zero.\n");
					return -1;
				}
				regs[a]= (regs[b]/regs[c]) & 0xFFFFFFFF;
				break;
			case 6: /* Not-And */
				regs[a] = ~(regs[b] & regs[c]) & 0xFFFFFFFF;
				break;
			case 7: /* Halt */
				/* Attempt to cleanup and exit cleanly */
				for(a=0;a<start_size;a++) {
					/* will hold malloc'd array or NULL */
					free(addrmap[a]); 
				}
				free(addrmap);
				free(sizemap);
				return 0;
				break;
			case 8: /* Allocation */
				t = (unsigned int *) calloc(regs[c], sizeof(unsigned int));
				if(t == NULL) {
					printf("Calloc failed.\n");
					return -1;
				}
				regs[b] = insert_addr(t, regs[c]*sizeof(unsigned int));
				break;
			case 9: /* Abandonment */
				free(addrmap[regs[c]]);
				addrmap[regs[c]] = NULL;
				sizemap[regs[c]] = 0;
				break;
			case 10: /* Output */
				printf("%c", (char) regs[c]);
				break;
			case 11: /* Input */
				if(in_idx == 0 || stdinbuff[in_idx] == (char) 0xFF) {
					memset(stdinbuff, 0xFF, BUFFMAX);
					if(fgets(stdinbuff, BUFFMAX-1, stdin)==NULL)
						return -1;
				}
				if(!(in_idx == 0 && stdinbuff[in_idx] == (char) 0xFF)) {
					regs[c] = (unsigned int) stdinbuff[in_idx];
				}
				in_idx++;
				if(in_idx == BUFFMAX-1 || (in_idx > 0 && stdinbuff[in_idx-1] == (char) 0xFF) || (in_idx >= 1 && stdinbuff[in_idx-1] == '\n'))
					in_idx = 0;
				break;
			case 12: /* Load Program */
				if(regs[b] != 0) {
					sizemap[0] = sizemap[regs[b]];
					addrmap[0] = (unsigned int *) realloc(addrmap[0], sizemap[0]);
					if(addrmap[0] == NULL) {
						printf("Realloc failed.\n");
						return -1;
					}
					t = memcpy(addrmap[0], addrmap[regs[b]], sizemap[0]);
					if(t == NULL) {
						printf("Memcpy failed.\n");
						return -1;
					}
				}
				ip = regs[c] - 1;
				break;
			case 13: /* Orthography */
				regs[(addrmap[0][ip] >> 25) & 0x7] = (addrmap[0][ip] & 0x1FFFFFF);
				break;
			default:
				return 1;
		}
		ip++;
	}
	return 0;
}
