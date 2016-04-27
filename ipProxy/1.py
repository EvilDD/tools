thread_num = 10
threads = []
timeout = 5  # 设置延时
validIp = []  # 过滤出的有效ip
exitFlag = 0


def main():
    globals exitFlag
    print(thread_num)
    exitFlag = 1
main()
print(exitFlag)
