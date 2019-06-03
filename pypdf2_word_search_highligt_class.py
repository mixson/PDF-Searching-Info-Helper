import PyPDF2
from PyPDF2 import PdfFileWriter, PdfFileReader
import fitz
import os

from search_catalog_program.acro_request_test.pypdf2_highlight import createHighlight, addHighlightToPage

class pdf_parser():

    _fullLinkFlag_ = False
    _directoryRecusive_ = False

    def __init__(self, sourceFile, keywordFile, outputDirectory = os.getcwd()):
        self.sourceFile_ = sourceFile
        self.keywordFile_ = keywordFile

        self.keywordList_ = []
        self.pdfList_ = []

        self.outputDirectory_ = outputDirectory  # default current woring directory
        self.outputFileName_ = ""

    def parsingSourceFileTxt(self, sourceFile = ""):
        # Parameter
        # sourceFile : txt file
        # return list combined by full filepath pdf
        if sourceFile:
            self.sourceFile_ = sourceFile
        if not self.sourceFile_:
            raise Exception("Target source file location is missing")

        sourceFileFullPath = os.path.join(os.getcwd(), self.sourceFile_)

        with open(sourceFileFullPath, "r") as file:
            lines = file.read().splitlines()
            lines = [line for line in lines if line != ""] # excepting empty line
            directoryList = [line for line in lines if ('.') not in line] # files and hidden folders is excepted
            fileList = [line for line in lines if '.' in line] # assume hidden folder will not be in the source file

        for directory in directoryList:
            for root, _, files in os.walk(directory): # root, dirs, files
                if ("." not in root):
                    for file in files:
                        fileList.append(os.path.join(root, file))

        pdfList = [element for element in fileList if '.pdf' in element] # only get the pdf File

        # turn filename into full filename
        for i in range(len(pdfList)):
            if "\\" not in pdfList[i]:
                pdfList[i] = os.getcwd() + "\\" + pdfList[i]

        self.pdfList_ = list(set(pdfList))
        return self.pdfList_

    def parsingKeywordFile(self, keywordFile):
        # Parameter
        # sourceFile : txt file
        # return list combined by full filepath pdf
        if keywordFile:
            self.keywordFile_ = keywordFile
        if not self.keywordFile_:
            raise Exception("Target keyword file location is missing")

        keywordFileFullPath = os.path.join(os.getcwd(), self.keywordFile_)

        with open(keywordFileFullPath, "r") as file:
            lines = file.read().splitlines()
            lines = [line for line in lines if line != ""]  # excepting empty line
            keyword = lines

        self.keywordList_ = list(set(keyword))
        return self.keywordList_


pdfParser = pdf_parser("source.txt", "keyword.txt")
pdfList = pdfParser.parsingSourceFileTxt("source.txt")
print("abc")