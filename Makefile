CXX := g++
CXXFLAGS := -std=c++23 -Wall -Wextra -O2 -g -fno-omit-frame-pointer -fno-optimize-sibling-calls
OUT := out
TARGET := $(OUT)/main

SRCS := $(wildcard *.cpp)
OBJS := $(SRCS:%.cpp=$(OUT)/%.o)
DEPS := $(OBJS:.o=.d)

.PHONY: all clean

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CXX) $(CXXFLAGS) $^ -o $@

$(OUT)/%.o: %.cpp | $(OUT)
	$(CXX) $(CXXFLAGS) -MMD -MP -c $< -o $@

$(OUT):
	mkdir -p $(OUT)

clean:
	rm -rf $(OUT)

-include $(DEPS)
