
### Some sample code for processing pdf files

import numpy as np
import re

import tabula


def extractNumfromTable(input_string, num_year=5):
    """
    :param input_string: input from pdf
    :param num_year: how many lines
    :return:
    """
    trail_table_split = input_string.split('\n')

    earning_table_idx = [idx for idx, i in enumerate(trail_table_split) if 'Earnings Per Share' in i]

    if earning_table_idx:
        column_name = trail_table_split[earning_table_idx[0]+1].split(' ')
        num_values = trail_table_split[earning_table_idx[0]+2:earning_table_idx[0]+2+num_year]
        num_values = [i.replace('E ', 'E').split(' ') for i in num_values]
        return [column_name] + num_values
    else:
        return None


def extractAnnoNotesfromText(input_string):

    if 'Analyst Research Notes and other Company News' in input_string:
        curr_split = re.split(r'[a-zA-Z]+ \d+, 201\d\n', input_string)
        # if curr_split:
        extracted_time = re.findall(r'[a-zA-Z]+ \d+, 201\d\n', input_string)
        output = []
        for i in range(len(curr_split[1:])):
            curr_text = extracted_time[i]+curr_split[1+i].replace('\n', ' ')
            ## deal with two cases
            if "Note: Research notes reflect CFRA's published" in curr_text:
                curr_text = curr_text.split("Note: Research notes reflect CFRA's published")[0]
            elif "Stock Report |" in curr_text:
                curr_text = curr_text.split("Stock Report |")[0]
            output = output + [curr_text.strip()]
        return output
    else:
        return None


def extractHeaderInfo(input_string):

    curr_header = re.findall(r"Stock Report .*\n.*\n", input_string)

    if curr_header:
        curr_header = curr_header[0]
        curr_symbol = re.findall(r"Symbol:[ \.A-Z]+", curr_header)[0].split(':')[-1].strip()
        header_info = (curr_header, curr_symbol)
        return header_info
    else:
        return None


### It is an example of how to use tabula to extract information for financial reports from UBS
def extractUBS(pdf_path):

    def mappingFromEnd(header, content):

        mapping = []
        for i in range(1, len(header) + 1):
            mapping.append([header[-i], content[-i]])
        return mapping

    def removeNaN(df):

        df_no_nan = []
        for each_line in df[0].values.tolist():
            df_no_nan.append([i for i in each_line if str(i) != 'nan'])

        return df_no_nan

    def reorganizeEstimate(required_format):
        """

        :param required_format: input format should be ('2015A', '$2.59')
        :return:
        """

        if 'A' in required_format[0]:
            flag = 'Actual'
        if 'E' in required_format[0]:
            flag = 'Estimate'
        reorg_output = None
        try:
            reorg_output = [required_format[0].strip('A').strip('E'), flag,
                            float(required_format[-1].strip('$').strip('A').strip('E'))]
        except:
            pass

        return reorg_output

    ## extract from pdf
    df = tabula.read_pdf(pdf_path, pages='1', multiple_tables=True,
                         area=[70, 0, 90, 100], relative_area=True, stream=True)

    # print(df)

    ## remove NaN
    table = removeNaN(df)

    header_idx = None
    curr_header = None
    curr_content = None
    for idx, each_line in enumerate(table):
        try:
            curr_line = ' '.join(each_line)
            if 'Highlights (US$m)' in curr_line:
                curr_header = curr_line.replace('Highlights (US$m) ', '').split(' ')
                # print(curr_header)
            if 'EPS' in curr_line[:20]:
                curr_content = curr_line.split(' ')
                # print(curr_content)
        except:
            pass

    mapping = []
    if curr_header and curr_content:
        mapping = mappingFromEnd(curr_header, curr_content)

    # print(mapping)

    ## reorganize
    if mapping:
        mapping_new = []
        for each_one in mapping:
            each_one[0] = '20' + each_one[0].split('/')[-1]
            if 'E' not in each_one[0]:
                each_one[0] = each_one[0] + 'A'
            mapping_new.append([each_one[0], each_one[1]])
        mapping = [reorganizeEstimate(i) for i in mapping_new]

    return mapping

