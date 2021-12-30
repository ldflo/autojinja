#pragma once

#include <cstring>
#include <string>
#include <array>
#include <vector>
#include <map>

/// @brief Copies the given value at destination pointer.
///        The pointer then advances at the end of the copied value.
/// @example
///     serialize(1, dst);                           // dst = 0x00 -> dst = 0x04
///     serialize("test", dst);                      // dst = 0x04 -> dst = 0x0C
///     serialize(std::vector<int>({1, 2, 3}), dst); // dst = 0x0C -> dst = 0xFC
///
void serialize(int8_t value, char*& dst);
void serialize(int16_t value, char*& dst);
void serialize(int32_t value, char*& dst);
void serialize(int64_t value, char*& dst);
void serialize(uint8_t value, char*& dst);
void serialize(uint16_t value, char*& dst);
void serialize(uint32_t value, char*& dst);
void serialize(uint64_t value, char*& dst);
void serialize(bool value, char*& dst);
void serialize(char value, char*& dst);
void serialize(float value, char*& dst);
void serialize(double value, char*& dst);
void serialize(const char* value, char*& dst);
void serialize(const std::string& value, char*& dst);
template <typename T, size_t N>
void serialize(const std::array<T, N>& value, char*& dst);
template <typename T, size_t N>
void serialize(const T (&value)[N], char*& dst);
template <typename T>
void serialize(const T value[], size_t size, char*& dst);
template <typename T, typename A>
void serialize(const std::vector<T, A>& value, char*& dst);
template <typename T1, typename T2>
void serialize(const std::pair<T1, T2>& value, char*& dst);
template <typename K, typename T, typename A>
void serialize(const std::map<K, T, A>& value, char*& dst);

/// @brief Retrieves the given typed value at source pointer.
///        The pointer then advances at the end of the retrieved value.
/// @example
///     auto r1 = deserialize<int>(src);              // src = 0x00 -> src = 0x04
///     auto r2 = deserialize<std::string>(src);      // src = 0x04 -> src = 0x0C
///     auto r3 = deserialize<std::vector<int>>(src); // src = 0x0C -> src = 0xFC
///
template <typename T>
T deserialize(char*& src);

#include "serializer_impl.hpp"
