#include "shared_memory.h"

/// Mutex
std::mutex shared_memory::mutex;
std::condition_variable shared_memory::cv;

/// Buffer
char shared_memory::buffer[];
char* shared_memory::ptr = buffer;
