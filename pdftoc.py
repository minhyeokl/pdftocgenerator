import fitz
from operator import itemgetter
import re
from PyPDF2 import PdfFileWriter, PdfFileReader
from fitz.fitz import Page
import sys

def fonts(doc):
    styles = {}
    font_counts = {}

    for page in doc:
        blocks = page.getText("dict")["blocks"]
        for b in blocks:
            if b['type'] == 0:
                for l in b["lines"]:
                    for s in l["spans"]:
                    
                        identifier = "{0}".format(s['size'])
                        styles[identifier] = {'size': s['size'], 'font': s['font']}

                        font_counts[identifier] = font_counts.get(identifier, 0) + 1 

    font_counts = sorted(font_counts.items(), key=itemgetter(1), reverse=True)

    if len(font_counts) < 1:
        raise ValueError("Zero discriminating fonts found!")

    return font_counts, styles

def font_tags(font_counts, styles):
    p_style = styles[font_counts[0][0]]
    p_size = p_style['size']
    
    font_sizes = []
    for (font_size, count) in font_counts:
        font_sizes.append(float(font_size))
    font_sizes.sort(reverse=True)

    hidx = 1
    sidx = 1
    size_tag = {}
    for size in font_sizes:
        if size == p_size:
            size_tag[size] = 'p'
        if size > p_size:
            size_tag[size] = 'h{0}'.format(hidx)
            hidx += 1
        elif size < p_size:
            size_tag[size] = 's{0}'.format(sidx)
            sidx += 1

    return size_tag

def headers_para(doc, size_tag):
    header_para = []

    for page in doc:
        blocks = page.getText("dict")["blocks"]
        for b in blocks:
            if b['type'] == 0:
                for l in b["lines"]:
                    line = ""
                    header = size_tag[l["spans"][0]['size']]

                    for s in l["spans"]:
                        line += s['text']

                line = line.replace('\u2002',' ').strip()

                if line != '' and header[0] == 'h':
                    rdata = {'tag': int(header[1:]), 'text': line, 'page': page.number}
                    header_para.append(rdata)
    return header_para

def get_toc_data(data):
    toc_data = []
    txt_toc = []
    h2 = re.compile('^([0-9]+|[A-Z])\.[0-9]+ ')
    h3 = re.compile('^([0-9]+|[A-Z])\.[0-9]+\.[0-9]+ ')
    h2tag = 0
    h3tag = 0
    for line in data:  
        if line['page'] < 50: # 앞부속이 50페이지를 넘으면 수정 필요
            continue
        if h2.match(line['text']) != None:
            if h2tag == 0:
                h2tag = line['tag']
        if h3.match(line['text']) != None:
            if h3tag == 0:
                h3tag = line['tag']
        if h2tag != 0 and h3tag != 0:
            break

    for line in data:
        if line['tag'] == h2tag or line['tag'] == h3tag:
            txt_toc.append(line)
    for line in txt_toc:
        if h2.match(line['text']) != None:
            toc_data.append(line)
        if h3.match(line['text']) != None:
            toc_data.append(line)
    return toc_data, h2tag, txt_toc

def make_pdf_toc(toc_data, h2tag, txt_toc, filename):
    output = PdfFileWriter()
    input = PdfFileReader(open(filename, 'rb'))
    n = input.getNumPages()
    for i in range(n):
        output.addPage(input.getPage(i))

    h1 = re.compile('^([0-9]+|[A-Z])\.1 ')
    for mark in toc_data:
        if mark['tag'] == h2tag:
            if h1.match(mark['text']) != None:
                chno = mark['text'].split('.')
                chno = chno[0]
                h1par = output.addBookmark(chno, mark['page'], parent=None)
            h2par = output.addBookmark(mark['text'], mark['page'], parent=h1par)
        else:
            output.addBookmark(mark['text'], mark['page'], parent=h2par)
    
    outputname = filename[:-4] + '_목차적용.pdf'
    txtname = filename[:-4] + '.txt'
    
    outputtxt = open(txtname, 'w', encoding='utf8')
    outputStream = open(outputname,'wb')

    for line in txt_toc:
        if line['text'][0:4] == 'Part':
            outputtxt.write('\n')
        if h1.match(line['text']) != None:
            outputtxt.write('\n')
            chno = line['text'].split('.')
            chno = chno[0]
            outputtxt.write(chno + '\n')
        txtdata = line['text'] + '\t' + str(line['page']) + '\n'
        outputtxt.write(txtdata)
    outputtxt.close()
    
    output.write(outputStream)
    outputStream.close()

def pdftoc(filename):
    doc = fitz.open(filename)
    font_counts, styles = fonts(doc)
    size_tag = font_tags(font_counts, styles)

    data = headers_para(doc, size_tag)
    toc_data, h2tag, txt_toc = get_toc_data(data)
    
    make_pdf_toc(toc_data, h2tag, txt_toc, filename)

if __name__ == '__main__':
    pdftoc(sys.argv[1])

    
