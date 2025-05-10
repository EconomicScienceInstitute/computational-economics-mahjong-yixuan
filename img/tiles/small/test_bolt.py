from bolt import profile

@profile
def test_function():
    # 一个简单的测试函数
    result = 0
    for i in range(1000000):
        result += i
    return result

if __name__ == "__main__":
    # 运行测试函数
    result = test_function()
    print(f"Result: {result}") 