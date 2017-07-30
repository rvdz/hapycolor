CC=clang++
CFLAGS=-std=c++11 -I. -g
DEPS=color_reducer.hpp
OBJ=color_reducer.o 

EXEC=color_reducer

all: $(EXEC) 

%.o: %.cpp $(DEPS)
		$(CC) -c -o $@ $(CFLAGS) $<

color_reducer: $(OBJ)
		$(CC) $(CFLAGS) -o $@ $^ 

run: $(EXEC)
	./$<

clean:
	rm -f $(OBJ) $(EXEC)
