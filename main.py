from urls import delRepeatUrls
from urls import removeString
from urls import compareList


def authorInfo():
    print("===============================")
    print("*********纯属娱乐勿喷**********")
    print("                author:  Evi1m1")
    print("                  Data: 16.4.17")
    print("===============================")


def showInfo():
    print("请选择你要的操作:")
    print("1.urls去重复,支持文夹件批量操作")
    print("2.去长字符串中除指定的短符串")
    print("3.后一个文件去除前一个文件中已存在的字符串")
    print("\n")
if __name__ == "__main__":
    authorInfo()
    showInfo()
    command = input("请输入对应操作数字:")
    comId = int(command)
    if comId == 1:
        delRepeatUrls.main()
    elif comId == 2:
        removeString.main()
    elif comId == 3:
        compareList.main()
    else:
        print("未识别命令,敬请开放新功能!")
