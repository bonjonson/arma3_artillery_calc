'''
Конвертация csv-файла в структуру данных со вложенными словарями. CSV-файл с разделителем ";"
'''
g = open('mortar.csv', 'r')
f = open('mortar.txt', 'a')
for l in g:
    l = "'" + l.rstrip() + "],"
    l = l.replace(";", ":")
    l = l.replace(":", "': [", 1)
    l = l[:8] + l[8:].replace(":", ", ") + "\n"
    f.write(l)
g.close()
f.close()