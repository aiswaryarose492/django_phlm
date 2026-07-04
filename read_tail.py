
with open('out.txt', 'r', encoding='utf-8') as f:
    f.seek(0, 2)
    size = f.tell()
    f.seek(max(0, size - 2000))
    print(f.read())
