import re
import os
import sys
import datetime
import pprint
import spacy
import ginza
import xml.etree.ElementTree as ET


def infile(filename):
    """

    :type filename: string
    """
    with open(filename, 'r') as f:
        strtxt = f.read()

    return strtxt


def outfile(filename, outlist):
    with open(filename, 'w') as f:
        f.write("\n".join(outlist))


def search_sentence(root):
    output = []
    temp = []
    output_text = ''

    if not root is None:
        if root.tag == 'quotation' or root.tag == 'citation' or root.tag == 'source' or root.tag == 'speech' or root.tag == 'speaker':
            output_text = ET.tostring(root, encoding='unicode')
            if re.search(r'<.*?paragraph.*?>', output_text):
                output_text = output_text+'[renketu]'
                output.append(output_text)
            else:
                for child in root:
                    temp = search_sentence(child)
                    if not temp == None:
                        output += temp
        elif root.tag == 'sentence' or root.tag == 'superSentence':
            output_text = ET.tostring(root, encoding='unicode')
            output.append(output_text)
        else:
            for child in root:
                temp = search_sentence(child)
                if not temp == None:
                    output += temp

    return output

def Getfilenamelist(root):
    output = []
    temp = []
    for name in os.listdir(path=root):
        if os.path.isdir(root+'/'+name):
            temp = Getfilenamelist(root+'/'+name)
            output += temp
        elif os.path.isfile(root+'/'+name):
            output.append(root+'/'+name)
            os.makedirs('raw/' + root, exist_ok=True)
    return output


if __name__ == '__main__':
    infilelist = []
    outfilelist = []
    logfile = 'debug.log'
    infilelist = Getfilenamelist('LB')
    for line in infilelist:
        outfilelist.append('raw/'+line)
    with open(logfile,'w') as fd:
        fd.write('---rawdata_make---\n')
    resultlist = []
    file_length = len(infilelist)

    for i in range(len(infilelist)):
        fd = open(logfile, 'a')
        print('['+str(i)+']('+str(file_length)+'),filename:'+infilelist[i]+',rawdata_make,start,'+str(datetime.datetime.now()))
        fd.write('['+str(i)+']('+str(file_length)+'),filename:'+infilelist[i]+',rawdata_make,start,'+str(datetime.datetime.now())+'\n')

        content = infile(infilelist[i])
        # content = ""
        pattern_s = r'<sentence.*?>'
        pattern_e = r'</sentence>'

        root = ET.fromstring(content)
        resultlist = search_sentence(root)
        origin = []
        resultlist2 = []
        flag = 0

        resultlist2 = []
        for line in resultlist:
            if not line == '':
                temp = re.sub('<.*?>', '', line)
                temp = re.sub('[  \t\f\r\n]$', '', temp)
                temp = re.sub('\n', '', temp)
                temp = re.sub('^[　\t\f\r\n]', '', temp)
                origin.append(temp)

        for oi in range(len(origin)):
            if not oi == 0 and re.search(r'\[renketu\]', origin[oi]):
                resultlist2[-1] = resultlist2[-1] + re.sub('\[renketu\]','',origin[oi])
                flag = 1
            elif flag:
                resultlist2[-1] = resultlist2[-1] + origin[oi]
                flag = 0
            else:
                resultlist2.append(origin[oi])

        outfile(outfilelist[i], resultlist2)

        print('['+str(i)+']('+str(file_length)+'):filename:' + infilelist[i] + ',rawdata_make,end,' + str(datetime.datetime.now()))
        fd.write('['+str(i)+']('+str(file_length)+'):filename:' + infilelist[i] + ',rawdata_make,end,' + str(datetime.datetime.now())+'\n')
        fd.close()

    #ginzaの解析ここから

    nlp = spacy.load('ja_ginza')
    parselist = []

    infilelist = []
    outfilelist = []

    infilelist = Getfilenamelist('raw')
    for line in infilelist:
        outfilelist.append('parse/'+line)
    with open(logfile,'a') as fd:
        fd.write('---parsedata_make---\n')
    file_length = len(infilelist)
    temp = []
    rawlist1 = []
    rawlist2 = []
    for i in range(len(infilelist)):
        fd = open(logfile, 'a')
        print('['+str(i)+']('+str(file_length)+'),filename:'+infilelist[i]+',parsedata_make,start,'+str(datetime.datetime.now()))
        fd.write('['+str(i)+']('+str(file_length)+'),filename:'+infilelist[i]+',parsedata_make,start,'+str(datetime.datetime.now())+'\n')

        rawlist1 = infile(infilelist[i])
        rawlist2 = rawlist1.split()
        for line in rawlist2:
            line = re.sub('\n', '', line)
            doc = nlp(line)
            for sent in doc.sents:
                for token in sent:
                    token_text = ''
                    token_text = '{},{},{},{},{},{},{},{}'.format(
                        str(token.i),  # トークン番号
                        token.text,  # テキスト
                        token.lemma_,  # レンマ
                        ginza.reading_form(token),  # 読みカナ
                        token.pos_,
                        token.tag_,  # 品詞詳細
                        str(token.head.i),
                        token.dep_)
                    if token.ent_type_ == '':
                        token_text += ',NotNER'
                    else:
                        token_text += ',' + token.ent_type_

                    parselist.append(token_text)
                parselist.append(
                    '*EOS'
                )

        outfile(outfilelist[i], parselist)
        print('['+str(i)+']('+str(file_length)+'):filename:' + infilelist[i] + ',parsedata_make,end,' + str(datetime.datetime.now()))
        fd.write('['+str(i)+']('+str(file_length)+'):filename:' + infilelist[i] + ',parsedata_make,end,' + str(datetime.datetime.now())+'\n')
        fd.close()



