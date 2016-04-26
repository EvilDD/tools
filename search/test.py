# ipR = '(.*?):'  # 拆分出ip
# protR = ':(\d+)'
# import re
# s = '192.168.1.1:80'
# a = re.findall(ipR, s)
# b = re.findall(protR, s)
# print(a[0], '=====', b[0])
values = []
for i in range(20):
    values.append((i, 'hi rollen' + str(i)))
print(values)
