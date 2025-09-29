import pymupdf

# 打开MOBI文档
doc = pymupdf.open("data/book.mobi")
text = ""
# 逐页提取文本
for page in doc:
    text += page.get_text()

doc.close()
print(text)