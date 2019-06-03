import os
import argparse
from acora import AcoraBuilder
from pprint import pprint
import datetime
import calendar
import time
import PyPDF2
from tabulate import tabulate
import pandas as pd

from PyPDF2 import PdfFileWriter, PdfFileReader
import fitz
from search_catalog_program.acro_request_test.pypdf2_highlight import createHighlight, addHighlightToPage


def parsing_argument():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--source', type=str,
                        help='the keyword file')  # txt, csv, excel, (database)
    parser.add_argument('-t', '--target_folder', type=str,
                        default=os.getcwd(),
                        help='starting folder')
    parser.add_argument('-f', '--target_files',
                        help='target_files')
    parser.add_argument('-o', '--output',
                        default=os.getcwd(),
                        help='output_location')
    parser.add_argument('-p', '--pdf', action='store_true',
                        help='create new pdf')
    args = parser.parse_args()
    return args

def pypdf2_performance(filename ):
    pdfFileObj = open(filename, 'rb')
    start_time = time.time()
    pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
    num_pages = pdfReader.numPages
    count = 0
    text = []
    pdf_start_time = time.time()
    while count < num_pages:
        page_start_time = time.time()
        pageObj = pdfReader.getPage(count)
        count += 1
        text.append(pageObj.extractText())
        print("Processing {0} : Page {1} using {2} s, Total {3} s".format(filename, count, round(time.time()-page_start_time, 2), round(time.time()-pdf_start_time, 2)))

    total_time = round(time.time() - start_time, 2)
    return text, total_time

def pypdf2_and_fitz(filename, keywords_list):
    # search all keywords in different pages, return the pdf output stream and time used
    start_time = time.time()

    pdfOutput = PdfFileWriter()
    pdfFileObj = open(filename, 'rb')
    pypdf_pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
    fitz_pdfReader = fitz.open(pdfFileObj)
    num_pages = pypdf_pdfReader.numPages
    count = 0
    text = []
    pdf_start_time = time.time()

    while count < num_pages:
        page_start_time = time.time()
        text.append(pypdf_pdfReader.getPage(count))
        page_layout = text[-1].mediaBox
        for keyword in keywords_list:
            text_instances = fitz_pdfReader[count].searchFor(keyword)
            text_highlight_objects = []
            for instance in text_instances:
                text_highlight_objects.append(createHighlight(instance.x0, float(page_layout[3]) - instance.y1,
                                                              instance.x1, float(page_layout[3]) - instance.y0,
                                                              {"author": "",
                                                               "contents": keyword
                                                               }))
            for text_highlight_object in text_highlight_objects:
                addHighlightToPage(text_highlight_object, text[-1], pdfOutput)

        pdfOutput.addPage(text[-1])
        count += 1
        print("Processing {0} : Page {1} using {2} s, Total {3} s".format(filename, count, round(time.time()-page_start_time, 2), round(time.time()-pdf_start_time, 2)))

    total_time = round(time.time() - start_time, 2)
    return pdfOutput, total_time

def combine_column_to_dict(source_list):
    # Using keywords as column, and combine and the location of word into a list

    source_set = set(element_source[0] for element_source in source_list)
    output_dict = dict.fromkeys(source_set, "")
    for source_list_element in source_list:
        if source_list_element[0] in source_set:
            output_dict[str(source_list_element[0])] = str(output_dict[source_list_element[0]]) + str(source_list_element[1]) + ", "

    for key, values in output_dict.items(): # remove last ", "
        output_dict[key] = values[:-2]

    return output_dict


if __name__ == "__main__":
    args = parsing_argument()

    if not args.source:
        raise Exception("Please input the source file")
    with open(args.source, 'r') as file:
        keywords = file.read().splitlines()  # Reading the source file

    ac = AcoraBuilder(keywords)
    ac = ac.build() # build the model for searching the keywords

    # Reading the target files
    if args.target_files:
        with open(args.target_files, 'r') as file:
            target_files = file.read().splitlines()
            target_file = [target_file for target_file in target_files if ".pdf" in target_file or ".html" in target_file]
    else:
        target_files = [os.path.join(paths, file) for paths, _, files in os.walk(args.target_folder)
                        for file in files
                        if '.pdf' in file or '.html' in file]

    pprint("Searching file: \n")
    pprint(70* "=") # Variables initiations
    pprint(target_files)
    result_print = []
    x = 0

    # Process the pdf file one by one
    for target_file in target_files:
        x += 1
        i = 0

        file_texts, time_used = pypdf2_performance(target_file)
        result_print.append([target_file, time_used])
        pprint(70 * "=")

        with open(target_file.split("\\")[-1].replace(".pdf", "") + "_py_pdf.txt",
                  "a+") as file:  # insert the seperate line and datetime everytime run the program
            file.write(70 * '=' + "\n")
            file.write(str(datetime.datetime.now()) + "( {0} )\n".format(calendar.day_name[datetime.datetime.today().weekday()]))
        # Process the page one by one
        for file_text in file_texts:
            i += 1
            ac = AcoraBuilder(keywords)
            ac = ac.build()
            result_list = [list(element) for element in ac.findall(file_text)]  # turn tuple in the list into List object -- Bug: cannot turn int into list
            result_dict = {}
            result_dict = combine_column_to_dict(result_list)

            if result_dict:  # only found result, it will write a line
                with open(target_file.split("\\")[-1].replace(".pdf", "") + "_py_pdf.txt", "a+") as file:  # insert the search result
                    file.write("Page {0} : ".format(i) + "\n")
                    for key, values in result_dict.items():
                        file.write(str(key) + ": " + str(values) + " [Total: {0}".format(len(values.split(","))) + "]\n")

                    file.write(40 * '-' + "\n")

    result_print = pd.DataFrame(result_print, columns=["File Name", "Time"])
    pprint(result_print)

    # indivdiually highlight the word, and output the pdf files
    for target_file in target_files_:
        pypdf2_and_fitz(target_file, keywords)
