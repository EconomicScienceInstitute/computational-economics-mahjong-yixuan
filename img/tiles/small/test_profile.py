import cProfile

def test_function():
    # 一个简单的测试函数
    result = 0
    for i in range(1000000):
        result += i
    return result

if __name__ == "__main__":
    # 使用 cProfile 分析性能
    cProfile.run('test_function()') 