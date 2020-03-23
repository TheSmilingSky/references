#include "../build/io.h"
#include <iostream>

int take_input(){
	int input;
	std::cin>>input;
	return input;
}

void display_output(int x){
	std::cout<<x<<'\n';
}