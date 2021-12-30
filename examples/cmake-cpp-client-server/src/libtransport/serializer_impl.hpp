namespace detail
{
    template <typename T>
    inline void serialize_numeric(T value, char*& dst) {
        constexpr size_t size = sizeof(T);
        std::memcpy(dst, &value, size);
        dst += size;
    }
}

inline void serialize(int8_t value, char*& dst) { detail::serialize_numeric(value, dst); }
inline void serialize(int16_t value, char*& dst) { detail::serialize_numeric(value, dst); }
inline void serialize(int32_t value, char*& dst) { detail::serialize_numeric(value, dst); }
inline void serialize(int64_t value, char*& dst) { detail::serialize_numeric(value, dst); }
inline void serialize(uint8_t value, char*& dst) { detail::serialize_numeric(value, dst); }
inline void serialize(uint16_t value, char*& dst) { detail::serialize_numeric(value, dst); }
inline void serialize(uint32_t value, char*& dst) { detail::serialize_numeric(value, dst); }
inline void serialize(uint64_t value, char*& dst) { detail::serialize_numeric(value, dst); }
inline void serialize(bool value, char*& dst) { detail::serialize_numeric(value, dst); }
inline void serialize(char value, char*& dst) { detail::serialize_numeric(value, dst); }
inline void serialize(float value, char*& dst) { detail::serialize_numeric(value, dst); }
inline void serialize(double value, char*& dst) { detail::serialize_numeric(value, dst); }

inline void serialize(const char* value, char*& dst) {
    size_t size = strlen(value);
    ::serialize(size, dst);
    std::memcpy(dst, value, size);
    dst += size;
}

inline void serialize(const std::string& value, char*& dst) {
    size_t size = value.size();
    ::serialize(size, dst);
    std::memcpy(dst, value.data(), size);
    dst += size;
}

template <typename T, size_t N>
inline void serialize(const std::array<T, N>& value, char*& dst) {
    constexpr size_t size = N;
    ::serialize(size, dst);
    for (const T& v : value)
        ::serialize(v, dst);
}

template <typename T, size_t N>
inline void serialize(const T (&value)[N], char*& dst) {
    constexpr size_t size = N;
    ::serialize(size, dst);
    for (const T& v : value)
        ::serialize(v, dst);
}

template <typename T>
inline void serialize(const T value[], size_t size, char*& dst) {
    ::serialize(size, dst);
    for (const T& v : value)
        ::serialize(v, dst);
}

template <typename T, typename A>
inline void serialize(const std::vector<T, A>& value, char*& dst) {
    size_t size = value.size();
    ::serialize(size, dst);
    for (const T& v : value)
        ::serialize(v, dst);
}

template <typename T1, typename T2>
inline void serialize(const std::pair<T1, T2>& value, char*& dst) {
    ::serialize(value.first, dst);
    ::serialize(value.second, dst);
}

template <typename K, typename T, typename A>
inline void serialize(const std::map<K, T, A>& value, char*& dst) {
    size_t size = value.size();
    ::serialize(size, dst);
    for (const auto& it : value)
        ::serialize(it, dst);
}

namespace detail
{
    template <typename T>
    inline T deserialize_numeric(char*& src) {
        constexpr size_t size = sizeof(T);
        T value;
        std::memcpy(&value, src, size);
        src += size;
        return value;
    }

    inline int8_t deserialize(char*& src, int8_t*) { return deserialize_numeric<int8_t>(src); }
    inline int16_t deserialize(char*& src, int16_t*) { return deserialize_numeric<int16_t>(src); }
    inline int32_t deserialize(char*& src, int32_t*) { return deserialize_numeric<int32_t>(src); }
    inline int64_t deserialize(char*& src, int64_t*) { return deserialize_numeric<int64_t>(src); }
    inline uint8_t deserialize(char*& src, uint8_t*) { return deserialize_numeric<uint8_t>(src); }
    inline uint16_t deserialize(char*& src, uint16_t*) { return deserialize_numeric<uint16_t>(src); }
    inline uint32_t deserialize(char*& src, uint32_t*) { return deserialize_numeric<uint32_t>(src); }
    inline uint64_t deserialize(char*& src, uint64_t*) { return deserialize_numeric<uint64_t>(src); }
    inline bool deserialize(char*& src, bool*) { return deserialize_numeric<bool>(src); }
    inline char deserialize(char*& src, char*) { return deserialize_numeric<char>(src); }
    inline float deserialize(char*& src, float*) { return deserialize_numeric<float>(src); }
    inline double deserialize(char*& src, double*) { return deserialize_numeric<double>(src); }

    inline char* deserialize(char*& src, char**) {
        size_t size = ::deserialize<size_t>(src);
        char* value = new char[size + 1];
        std::memcpy(value, src, size);
        value[size] = '\0';
        src += size;
        return value;
    }

    inline std::string deserialize(char*& src, std::string*) {
        size_t size = ::deserialize<size_t>(src);
        std::string value = std::string(src, size);
        src += size;
        return value;
    }

    template <typename T, typename A>
    inline std::vector<T, A> deserialize(char*& src, std::vector<T, A>*) {
        size_t size = ::deserialize<size_t>(src);
        std::vector<T, A> value(size);
        for (size_t i=0; i < size; ++i)
            value[i] = ::deserialize<T>(src);
        return value;
    }

    template <typename T1, typename T2>
    inline std::pair<T1, T2> deserialize(char*& src, std::pair<T1, T2>*) {
        return { ::deserialize<T1>(src), ::deserialize<T2>(src) };
    }

    template <typename K, typename T, typename A>
    inline std::map<K, T, A> deserialize(char*& src, std::map<K, T, A>*) {
        size_t size = ::deserialize<size_t>(src);
        std::map<K, T, A> value;
        for (size_t i=0; i < size; ++i) {
            auto pair = ::deserialize<std::pair<K, T>>(src);
            value[pair.first] = pair.second;
        }
        return value;
    }
}

template <typename T>
inline T deserialize(char*& src) { return detail::deserialize(src, static_cast<T*>(0)); }
