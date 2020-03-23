# A simple illustration to work with multi-file projects in cpp

To compile and run the program, follow these steps - 

* Navigate to the src folder and open the folder in terminal. Use the -c flag to compile the files into object code. When the -c option is NOT used, the compiler will expect the command to give everything necessary to compile AND link -- to make the executable.

  * _g++ std=c++11 -c io.cpp_
  * _g++ std=c++11 -c main.cpp_

* Now to link the two files and create an executable file named io use the -o flag.

  * _g++ -o io io.o main.o_

* Now the executable file io.o has been created. To run the file, type the following.

  * _./io_

* Now, type the input and get the output.
