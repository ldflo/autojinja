#include <iostream>
#include <thread>

#include "Server.h"
#include "ClientApi.h"

std::ostream& operator<<(std::ostream& stream, const std::vector<char>& vector) {
    int size = vector.size();
    stream << '{';
    for (int i=0; i < size-1; ++i)
        stream << vector[i] << ",";
    for (int i=size-1; i < size; ++i)
        stream << vector[i];
    stream << '}';
    return stream;
}

int main(int argc, char** argv) {
    /// Start server
    Server server;
    std::thread server_thread([&server]{
        std::cout << "Server started" << std::endl;
        server.run();
        std::cout << "Server stopped" << std::endl;
    });

    /// Client calls
    auto result1 = ClientApi::add(1, 4.3f);
    std::cout << "ClientApi::add(1, 4.3f) == " << result1 << std::endl;
    auto result2 = ClientApi::strip("  test  ");
    std::cout << "ClientApi::strip(\"  test  \") == " << result2 << std::endl;
    auto result3 = ClientApi::tochars("test");
    std::cout << "ClientApi::tochar(\"test\") == " << result3 << std::endl;
    auto result4 = ClientApi::fromchars({'t','e','s','t'});
    std::cout << "ClientApi::fromchars({'t','e','s','t'}) == " << result4 << std::endl;

    /// Stop server
    server.stop();
    server_thread.join();
    return 0;
}
