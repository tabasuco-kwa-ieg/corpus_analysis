import re
import os
import sys


def infile(filename):
    """

    :type filename: string
    """
    with open(filename, 'r') as f:
        strtxt = f.read().split("\n")

    return strtxt


def outfile(filename, outlist):
    with open(filename, 'w') as f:
        f.write("\n".join(outlist))


if __name__ == '__main__':
    infilelist = []
    outfilelist = []

    for line1 in os.listdir(path='./C-XML'):
        for line2 in os.listdir(path='./C-XML/' + line1):
            for line3 in os.listdir(path='./C-XML/' + line1 + '/' + line2):
                infilelist.append('./C-XML/' + line1 + '/' + line2+'/'+line3)
                outfilelist.append('./raw/C-XML/' + line1 + '/' + line2+'/'+line3)
                os.makedirs('./raw/C-XML/'+line1+'/'+line2,exist_ok=True)

    for i in range(len(infilelist)):
        content = infile(infilelist[i])
        # content = ""
        pattern1 = r'.*sentence.*'
        repattern1 = re.compile(pattern1)
        list_result = []


        for line in content:
            result1 = repattern1.match(line)
            if not result1 is None:
                temp: str = result1.group()
                result2 = re.sub('</?[\w]*>|</?[\w]* [\w]*="(.+?)"( /)?>', '', temp)
                result2 = re.sub('<.*?>', '', temp)
                result3 = re.sub(r'^[　\t\f\r\n]', '', result2)
                if not result3 == '':
                    list_result.append(result3)


        outfile(outfilelist[i], list_result)
