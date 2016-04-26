import os


def delRepUrls(filePath):
    try:
        with open(filePath, 'r', encoding='utf-8') as f:
            urls = f.readlines()
        firstUrl = urls[0]
        if '\ufeff' in firstUrl:  # 如果文本是utf-8会出现这样字符
            urls[0] = urls[0].strip('\ufeff')
        lastUrl = urls[len(urls) - 1]
        if '\n' not in lastUrl:  # 避免最后一个没有回车重复
            urls[len(urls) - 1] += '\n'
        tempUrls = set(urls)  # 例用集合唯一值的特性
        newUrls = list(tempUrls)
        try:
            with open(filePath, 'w', encoding='utf-8') as f:
                f.writelines(newUrls)
                print("%s已完成" % filePath)
        except:
            print("文件无法写入%s" % filePath)
    except Exception as e:
        print("%s文件无法打开读取,检查是否存在,格式是否为utf-8\n" % (filePath), e)


def listFolder():
    filePath = input('输入文件或文件夹所在地址:')
    if '\\' in filePath:
        filePath = filePath.replace('\\', '/')
    if os.path.isdir(filePath):
        docs = os.listdir(filePath)
        for doc in docs:
            doc = filePath + '/' + doc
            if os.path.isfile(doc):
                delRepUrls(doc)
            else:
                pass
                print("请注意此路径中有其他文件夹%s暂未做处理" % doc)

    else:
        delRepUrls(filePath)


def main():
    listFolder()
if __name__ == "__main__":
    main()
