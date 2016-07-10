#pragma once

#include <string>
#include <sstream>
#include <vector>
#include <iostream>

const int N = 42;

template<typename T>
T square(T x) {
    return x*x;
}

std::vector<int> reverse(std::vector<int> xs);


class Hz {
public:
    int a;
    std::string b;
    Hz() : a(0) {
        std::cout << "Hz default constructor" << std::endl;
    }
    Hz(const Hz &other) {
        std::cout << "Hz copy constructor" << std::endl;
        a = other.a;
        b = other.b;
    }
    ~Hz() {
        std::cout << "Hz destructor" << std::endl;
    }
    std::string __str__() {
        std::ostringstream out;
        out << "Hz(" << a << ", " << b << ")";
        return out.str();
    }
};
