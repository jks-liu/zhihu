import sys

def sort_txt(txt):
    with open(txt, 'rb') as f:
        lines = f.read().decode('gbk')
    
    qa = lines.replace("\r\n", "\n").split("\n\n")
    return sorted(qa)

def save_sorted(txt, qa):
    lines = "\n\n".join(qa)

    with open(txt, 'w') as f:
        f.write(lines)


def main():
    txt = sys.argv[1] if len(sys.argv)>1 else "2017-1031 题库电子版(v171031)/A_分类题库(供公布用)(201710311221).txt"
    save_sorted(txt+".sorted.txt", sort_txt(txt))

def main2():
    txt_a = "TXT题库包(v20210924)/A类题库(v20210924).txt"
    txt_b = "TXT题库包(v20210924)/B类题库(v20210924).txt"

    sorted_a = sort_txt(txt_a)
    sorted_b = sort_txt(txt_b)
    
    ia = 0
    ib = 0

    CREATE = []
    DELETE = []
    UPDATE = []


    while ia<len(sorted_a) or ib<len(sorted_b):
        key_a = sorted_a[ia][0:9]
        key_b = sorted_b[ib][0:9]

        if key_a < key_b:
            DELETE.append(sorted_a[ia])
            ia = ia+1
        elif key_a == key_b:
            if sorted_a[ia] != sorted_b[ib]:
                UPDATE.append(sorted_a[ia])
                UPDATE.append(sorted_b[ib])
            ia = ia+1
            ib = ib+1
        else:
            CREATE.append(sorted_b[ib])
            ib = ib+1

    save_sorted("create.txt", CREATE)
    save_sorted("delete.txt", DELETE)
    save_sorted("update.txt", UPDATE)
main2()
