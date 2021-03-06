import random
import string
import json
import matplotlib.pyplot as plt
import numpy as np
import math
import os


class Files:
    endLetter = ''
    lettersArr = []
    numFiles = 0
    allFiles = []

    def __init__(self, endLetter, rangeUpper, rangeLower, numFiles=len([name for name in os.listdir("DOCS") if os.path.isfile(os.path.join("DOCS", name))]), useOld=False):

        self.endLetter = endLetter
        self.lettersArr = self.createLettersArr(endLetter)
        self.numFiles = numFiles
        self.genrate_files(rangeUpper, rangeLower, useOld)
        self.TermDocFreq = self.getTermDocFreq()

    def statistical_model(self, query):
        temparr = {i: 0 for i in self.lettersArr}
        for i in query:
            temparr[i] = query[i]
        for i in self.allFiles:
            i.statistical_model_score = np.dot(np.array(list(temparr.values())),
                                               np.array(i.TermFreq))

    def getTermDocFreq(self):
        """getTermDocFreq"""
        df = {}
        for f in self.allFiles:
            for term in f.Contentmap:
                if(f.Contentmap[term] > 0):
                    if(term not in df):
                        df[term] = 1
                    else:
                        df[term] += 1
        return {key: math.log((self.numFiles/value), 2)
                for (key, value) in sorted(df.items())}

    def vectorSpace_model(self, files, query):
        for f in files.allFiles:
            f.idfi = f.Contentmap
            for j, i in zip(f.TF, files.TermDocFreq):
                f.idfi[i] = files.TermDocFreq[i] * j
        """Query"""
        temparr = {i: 0 for i in files.lettersArr}
        for i in query:
            temparr[i] = query[i]

        for f in files.allFiles:
            fo2 = (
                np.dot(np.array(list(f.idfi.values())), np.array(list(temparr.values()))))

            idfiP2 = np.power(np.array(list(f.idfi.values())), 2)
            tempP2 = np.power(np.array(list(temparr.values())), 2)

            t7t = math.sqrt(sum(idfiP2)*sum(tempP2))

            f.vectorSpace_model_score = (fo2/t7t) if (t7t > 0) else 0

    def createLettersArr(self, letter):
        if(isinstance(letter, int)):
            letter += (ord('a')-1)
            letter = str(chr(letter))
        return [_letter for _letter in string.ascii_lowercase if(
            _letter <= letter)]

    def genrateFilecontent(self, fileSize):
        strcontent = " "
        for _ in range(fileSize):
            strcontent += random.choice(self.lettersArr) + " "
        return strcontent

    def genrate_files(self, rangeUpper, rangeLower, useOld):
        self.allFiles = []
        if useOld:
            for fileID in os.listdir("DOCS"):
                filename = os.path.join("DOCS", fileID)
                f = open(filename, "r+")
                fileContent = (f.read()).lower()
                fileSize = (len(fileContent.strip())+1)//2
                f.close()
                # print(filename)
                self.allFiles.append(
                    File(fileID, fileSize, fileContent, self.lettersArr, useOld))
        else:
            for f in range(self.numFiles):
                fileID = "DOC_{}".format(f)
                fileSize = random.randint(rangeUpper, rangeLower)
                fileContent = self.genrateFilecontent(fileSize)
                self.allFiles.append(
                    File(fileID, fileSize, fileContent, self.lettersArr, useOld))


class File:
    def __init__(self, fileID, fileSize, fileContent, lettersArr, useOld):
        self.fileID = fileID
        self.fileSize = fileSize
        self.fileContent = fileContent
        self.Contentmap = {i: 0 for i in lettersArr}
        self.ContentmapGen(fileContent)
        self.TermFreq = self.getFreq()
        self.TF = self.getTF()
        if not useOld:
            self.createFile()

    def createFile(self):
        f = open("DOCS/{}.txt".format(self.fileID), "w")
        f.write(self.fileContent)
        f.close()

    def ContentmapGen(self, fileContent):
        for word in fileContent:
            if(word not in self.Contentmap):
                self.Contentmap[word] = 1
            else:
                self.Contentmap[word] += 1
        self.Contentmap.pop(' ', None)

    def getFreq(self):
        return [v / self.fileSize for v in self.Contentmap.values()]

    def getTF(self):
        maximum = max(self.Contentmap.values())
        return [v / maximum for v in self.Contentmap.values()]

    def __str__(self):
        return "FileID:" + str(self.fileID) + ",\t Size:"+str(self.fileSize)+"\n \t\tTermFreq:"+str(self.TermFreq)+"\n \t\tVS_TF:"+str(self.TF)+"\n\t\tContentmap:"+str(self.Contentmap)


def prepQuery(files, query):
    query = query.lower()
    query = query.strip()
    print('<' in query)
    if '<' in query:
        query = query.replace("<", "", 1)
        query = query.replace(">", "", 1)
        query = query.split(";")
        query = {i.split(":")[0]: float(i.split(":")[1]) for i in query}
        return query
    else:
        temp = { i:0 for i in files.TermDocFreq}
        for i in temp:
            temp[i]=0
        for char in query:
            temp[char]+=1
        maxV = max(list(temp.values()))
        for t in temp:
            temp[t]/=maxV

        for term in files.TermDocFreq:
            temp[term] = temp[term]*files.TermDocFreq[term]
        return temp


def Search_Statistical(files, query):
    query = prepQuery(files, query)

    files.statistical_model(query)
    files.allFiles.sort(
        key=lambda files: files.statistical_model_score, reverse=True)

    out = "<h1>Statistical Model</h1><br>"
    for f in files.allFiles:
        out += "File: %s, Score: %s<br>" % (
            f.fileID, f.statistical_model_score)
    return out+"<br>"


def Search_VectorSpace(filesV, query):
    query = prepQuery(filesV, query)

    filesV.vectorSpace_model(files=filesV, query=query)
    filesV.allFiles.sort(
        key=lambda files: files.vectorSpace_model_score, reverse=True)

    out = "<h1>Vector-Space Model</h1><br>"
    for f in filesV.allFiles:
        out += "File: %s, Score: %s<br>" % (
            f.fileID, f.vectorSpace_model_score)
    return out+"<br>"


if __name__ == "__main__":
    files = Files(numFiles=10, endLetter='f', rangeUpper=5,
                  rangeLower=10, useOld=True)
    # for f in files.allFiles:
    #     print(f.TermFreq)
    # print(Search_Statistical(files, "<A:0.3;B:0.6;c:0.8;f:0.1>"))
    # for f in files.allFiles:
    # print(files.TermDocFreq)
    # print(Search_VectorSpace(files, "<A:0.3;B:0.6;c:0.8;f:0.1>"))
    print(Search_VectorSpace(files, "ACFBB"))
