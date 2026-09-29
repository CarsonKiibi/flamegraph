#include <cstdint>
#include <cstdio>

static volatile std::uint64_t sink = 0;

[[gnu::noinline]] static void spin(std::uint64_t iterations) {
    for (std::uint64_t i = 0; i < iterations; ++i) {
        sink += i * i;
    }
}

[[gnu::noinline]] static void fast_path() {
    spin(12'000'000);
}

[[gnu::noinline]] static void slow_path() {
    spin(48'000'000);
}

[[gnu::noinline]] static void dispatch(int i) {
    if (i % 3 == 0) {
        slow_path();
    } else {
        fast_path();
    }
}

[[gnu::noinline]] static void process_batch(int batch) {
    for (int i = 0; i < 10; ++i) {
        dispatch(batch * 10 + i);
    }
}

[[gnu::noinline]] static void run_workload() {
    for (int batch = 0; batch < 5; ++batch) {
        process_batch(batch);
    }
}

int main() {
    run_workload();
    std::printf("done, sink=%llu\n", static_cast<unsigned long long>(sink));
    return 0;
}
