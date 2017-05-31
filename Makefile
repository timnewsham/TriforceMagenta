CFLAGS= -g -Wall

all : inputs testAfl

testAfl : testAfl.o
	$(CC) $(CFLAGS) -o $@ testAfl.o

inputs : gen.py
	test -d inputs || mkdir inputs
	./gen.py

clean:
	rm -f testAfl.o

