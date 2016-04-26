def compareList(f1, f2):  # 实现找出第二个文件在第一个文件中不存在的内容
    try:
        with open(f1, 'r', encoding='utf-8') as f:
            doc1 = f.readlines()
            if '\n' not in doc1[-1]:  # 最后一个元素可能没回车导致打乱后跟别的混合一起
                doc1[-1] += '\n'
        with open(f2, 'r', encoding='utf-8') as f:
            doc2 = f.readlines()
            if '\n' not in doc2[-1]:
                doc2[-1] += '\n'
    except:
        print("文件地址出错!!!")
    # newList = list(set(doc1) - set(doc2))
    newList = set(doc2).difference(set(doc1))  # 取第二个元素跟第一个不同的元素
    try:
        with open('diffrent.txt', 'w', encoding='utf-8') as f:
            f.writelines(newList)
    except:
        print("文件写入diffrent.txt失败!!!")


def main():
    f1 = input("请输入原始文件:")
    f2 = input("请输入要比较的文件地址:")
    compareList(f1, f2)
    print('已完成,生成新文件diffrent.txt')
if __name__ == '__main__':
    main()
