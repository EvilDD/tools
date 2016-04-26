def removeString(f, s):
    # 替换或去除某字符串
    with open(f, 'r', encoding='utf-8') as tempFile:
        urls = tempFile.readlines()
    newList = []
    for url in urls:
        if s in url:
            url = url.replace(s, '')
            newList.append(url)
        else:
            print('文本中不存在')
    with open(f, 'w', encoding='utf-8') as temp:
        temp.writelines(newList)
        print('替换成功')


def main():
    f = input('输入文件路径:')
    s = input('输入要替换为空的字符串:')
    try:
        removeString(f, s)
    except:
        print("文件不存在!!!")

if __name__ == '__main__':
    main()
