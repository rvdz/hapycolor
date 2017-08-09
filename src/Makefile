CC=g++
CFLAGS=-std=c++11 -O3
DEPS=mcqd.h
OBJ=mcqd.o 
SRC=color_reducer.cpp

EXE=color_reducer

OS := "$(shell uname)"
	
ifeq ($(OS),"Darwin")
	LIB := libcolor_reducer.dylib
else
	LIB := libcolor_reducer.so
endif

all: $(LIB) 

exec: $(EXEC)
lib: $(LIB)

%.o: %.cpp $(DEPS)
		$(CC) -c $(DEBUG) -o  $@ $(CFLAGS) $<

color_reducer: $(OBJ)
		$(CC) $(CFLAGS) -o $@ $^ 

run: $(EXE)
	./$<

clean:
	rm -f $(OBJ) $(EXE)
	if [[ $(OS) -eq "Darwin" ]]; then   \
		rm -f *.dylib; 				    \
	else  							    \
		rm -f *.so;  				    \
	fi;									

$(LIB): $(SRC) $(DEPS)
	if [[ $(OS) -eq "Darwin" ]]; then 				\
		$(CC) $(CFLAGS) -dynamiclib -o $@ $<;  		\
	else											\
		$(CC) $(CFLAGS) -fPIC -shared $< -o $@; 	\
	fi;												\

