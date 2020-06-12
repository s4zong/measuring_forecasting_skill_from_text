
### extract numerical forecasts from analysts notes
### ATTENTION: it is only designed for CFRA reports

import re


def maskMapping(mask_name, input_string, start_idx, count1):

    def replaceStrIndex(text, index1, index2, replacement=''):
        return '%s%s%s' % (text[:index1], replacement, text[index2:])

    pattern_iter = re.finditer(mask_name, input_string)
    for tag_idx, match in enumerate(pattern_iter):
        curr_start_idx = match.start() + tag_idx * 3
        curr_end_idx = match.end() + tag_idx * 3
        input_string = replaceStrIndex(input_string, curr_start_idx, curr_end_idx,\
                               mask_name.replace('>', '-') + str(tag_idx+start_idx+count1).zfill(2) + '>')

    return input_string


def maskEntity(input_string, pattern_list, mask_name, count1):

    output_tuple = []
    num_total_replacement = 0
    for each_pattern in pattern_list:
        curr_matches = re.findall(each_pattern[0], input_string)
        input_string, count = re.subn(each_pattern[0], mask_name, input_string)
        input_string = maskMapping(mask_name, input_string, num_total_replacement, count1)
        # print(input_string, count)
        if curr_matches:
            output_tuple.append(([(mask_name.replace('>', '-')+str(idx+num_total_replacement+count1).zfill(2)+'>', i) for idx, i in enumerate(curr_matches)]))
        num_total_replacement = num_total_replacement + count

    output_tuple = [j for i in output_tuple for j in i]

    return input_string, output_tuple, num_total_replacement+count1


def maskNumSpecSign(input_string, sign, replacement, count):

    input_string_split = input_string.split(' ')
    ## find token
    token_chosen = [(idx, i) for idx, i in enumerate(input_string_split) if sign in i]
    ## replace and build mapping
    mapping = []
    for idx, i in enumerate(token_chosen):
        input_string_split[i[0]] = replacement.replace('>', '-') + str(idx+count).zfill(2) + '>'
        mapping.append((replacement.replace('>', '-') + str(idx+count).zfill(2) + '>', i[1]))
    output_string = ' '.join(input_string_split)

    return output_string, mapping, len(token_chosen)+count


def performMasking(input_string, count1=0, count2=0):

    time_pattern_list = [(r"'1\d 's", 'year'), (r"1\d 's", 'year'), (r"'1\d's", 'year'),
                         (r"1\d's", 'year'), (r"'1\d", 'year'), # year
                         (r"Q\d", 'quarter'),  # quarter
                         (r'\d+[ |-]month', 'time-span'),
                         (r'(\d+[ |-]year|\d+[ |-]yr)', 'time-span'),  # time
                         (r'FY [20]*1\d -LRB- [A-Za-z\.]{3,10}? -RRB-', 'FY'),
                         (r'FY 1\d', 'FY'), (r"201\d", 'year')]

    neg_value_list = [(r'-\$[0-9\.]+', 'neg_value'),
                      (r'a loss of \$[0-9\.]+', 'neg_value'),
                      (r'a loss per share of \$[0-9\.]+', 'neg_value'),
                      (r'\$[0-9\.]+ loss', 'neg_value'),
                      (r'\$[0-9\.]+ EPS', 'pos_value'),
                      (r'(\$[0-9\. ]+)(million|billion|M)', 'normal_value')]

    output_tuple = []

    ## time masking
    input_string, output_tuple_time, time_count = maskEntity(input_string, time_pattern_list,
                                                             '<TIME>', count1)
    output_tuple = output_tuple + output_tuple_time

    ## mask negative value
    #
    input_string, output_tuple_money_1, money_count = maskEntity(input_string, neg_value_list,
                                                                 '<MONEY>', count2)

    ## money masking
    input_string, output_tuple_money, money_count = maskNumSpecSign(input_string, '$', '<MONEY>', money_count)
    output_tuple = output_tuple + output_tuple_money_1 + output_tuple_money

    return (input_string, output_tuple), time_count, money_count



def maskTimeMoney(input_pred):
    """

    :param input_pred:
    :return: a new dict with each sentence masked
    """

    ## process tagging res
    # all_sent = []
    # for each_sent in input_pred.items():
    #     curr_sent = ' '.join([i for i in each_sent[1][0]])
    #     all_sent.append((each_sent[0], curr_sent))
    ## new version
    all_sent = input_pred
    ## masking
    curr_para_masking = []
    time_count, money_count = 0, 0
    for each_sent in all_sent:
        curr_id = each_sent[0]
        curr_sent_mask, time_count, money_count = performMasking(each_sent[1], time_count, money_count)
        curr_para_masking.append((curr_id, curr_sent_mask[0], curr_sent_mask[1]))
    # print(curr_para_masking)
    ## reorganizing
    curr_para_masking_dict = {}
    for i in curr_para_masking:
        curr_para_masking_dict[i[0]] = i[1]
    ## curr_mapping_dict
    curr_mapping = [j for i in curr_para_masking for j in i[-1] if j != []]
    curr_mapping_dict = {}
    for i in curr_mapping:
        curr_mapping_dict[i[0]] = i[1]

    return curr_para_masking_dict, curr_mapping_dict


def extractPatterns(input_pred):

    ##### input_pred should be just a single pred
    ##### largely copy from extractNumForecasts()

    EPS_AND = \
        [r'<TIME-\d+> and <TIME-\d+>.{0,10}EPS estimate[s]*.{0,40}to <MONEY-\d+> and <MONEY-\d+>',
         r'<TIME-\d+> and <TIME-\d+>.{0,10}EPS estimate[s]*.{0,40}at <MONEY-\d+> and <MONEY-\d+>',
         r'our <TIME-\d+> and <TIME-\d+>.{0,10}EPS estimate[s]* of <MONEY-\d+> and <MONEY-\d+>',
         r'.{0,10}EPS estimate[s]* for <TIME-\d+> and <TIME-\d+>.{0,20}at <MONEY-\d+> and '
         r'<MONEY-\d+>',
         r'EPS estimates for <TIME-\d+> and <TIME-\d+> remain <MONEY-\d+> and <MONEY-\d+>',
         r'EPS estimates for <TIME-\d+> and <TIME-\d+> to <MONEY-\d+>.{0,20}and <MONEY-\d+>.{0,20}',
         r'<TIME-\d+> and <TIME-\d+> EPS estimates of <MONEY-\d+> and <MONEY-\d+>']

    LOSS = [r'<TIME-\d+> [operating |adjusted ]*loss per share estimate of <MONEY-\d+>',
            r'<TIME-\d+> [operating |adjusted ]*loss per share estimate.{0,20}to <MONEY-\d+>']

    LOSS_AND = [
        r'<TIME-\d+> and <TIME-\d+> loss per share estimates.{0,40}to <MONEY-\d+> and <MONEY-\d+>']

    estimate_pattern_list = [r'[our]*.{0,20}EPS estimate[s]* for <TIME-\d+>.{0,20}to <MONEY-\d+>',
                             r'[our]* <TIME-\d+> [operating |adjusted ]*[EPS ]*estimate[s]* of '
                             r'<MONEY-\d+>',
                             r'[our]* <TIME-\d+> [operating |adjusted ]*EPS estimate[s]*.{0,'
                             r'20}to <MONEY-\d+>',
                             r'[our]* EPS estimate[s]* in <TIME-\d+>.{0,20}to <MONEY-\d+>',
                             r'and.{0,20}<TIME-\d+>.{0,20}to <MONEY-\d+>',
                             r'and.{0,20}<TIME-\d+>.{0,20}at <MONEY-\d+>',
                             r'but.{0,20}<TIME-\d+>.{0,20}to <MONEY-\d+>',
                             r'but.{0,20}<TIME-\d+>.{0,20}at <MONEY-\d+>',
                             r'and.{0,20}<MONEY-\d+>.{0,20}for <TIME-\d+>',
                             r'[our]* <TIME-\d+> [operating |adjusted ]*EPS estimate[s]*.{0,'
                             r'20}at <MONEY-\d+>',
                             r'[our]* EPS estimate in <TIME-\d+>.{0,20}to <MONEY-\d+>',
                             r'[our]* <MONEY-\d+> [operating |adjusted ]*EPS estimate[s]* for '
                             r'<TIME-\d+>',
                             r'[our]* <MONEY-\d+> <TIME-\d+> EPS estimate[s]*',
                             r'[operating |adjusted ]*EPS estimate[s]* of <MONEY-\d+> for '
                             r'<TIME-\d+>']

    extracted_patterns = []
    for each_sent in input_pred:

        ## for each sentence, identify the pattern and need to have the flag
        curr_sent_id = each_sent[0]
        curr_text = each_sent[1]
        num_and = len([i for i in curr_text.split(' ') if i == 'and'])

        curr_all_pattern = []

        ## global masking
        curr_text = re.sub('-LRB-.{0,30}-RRB-', '<RB_MASK>', curr_text)

        ## get num_and >= 2 processed
        # first masking
        curr_text = re.sub('from <MONEY-\d+> and <MONEY-\d+>', '<FROM_MASK>', curr_text)
        curr_text = re.sub('by <MONEY-\d+> and <MONEY-\d+>', '<BY_MASK>', curr_text)
        # get num_and >= 2 processed
        if num_and >= 2:
            for each_pattern in EPS_AND:
                curr_found_pattern = re.findall(each_pattern, curr_text)
                if curr_found_pattern:
                    for each_pattern in curr_found_pattern:
                        curr_text = curr_text.replace(each_pattern, '<PROCESSED_TWO_AND>')
                        extracted_patterns.append([each_pattern, 'TWO_AND'])
            for each_pattern in LOSS_AND:
                curr_found_pattern = re.findall(each_pattern, curr_text)
                # print(curr_found_pattern)
                if curr_found_pattern:
                    for each_pattern in curr_found_pattern:
                        curr_text = curr_text.replace(each_pattern, '<PROCESSED_TWO_AND>')
                        extracted_patterns.append([each_pattern, 'TWO_AND-LOSS'])

        ## then estimates
        # second masking
        curr_text = re.sub(r'by <MONEY-\d+>', '<BY_MASK>', curr_text)
        curr_text = re.sub(r'from <MONEY-\d+>', '<FROM_MASK>', curr_text)
        # find patterns
        for each_pattern in estimate_pattern_list:
            curr_found_pattern = re.findall(each_pattern, curr_text)
            if curr_found_pattern:
                for each_pattern in curr_found_pattern:
                    extracted_patterns.append([each_pattern, 'EPS_EST'])

        ## then loss
        for each_pattern in LOSS:
            curr_found_pattern = re.findall(each_pattern, curr_text)
            if curr_found_pattern:
                for each_pattern in curr_found_pattern:
                    extracted_patterns.append([each_pattern, 'LOSS'])

        # print(extracted_patterns)

    return extracted_patterns


def genForecastTuples(extracted_patterns):

    not_matched = []
    curr_matched_tuple = []

    for each_pred_tuple in extracted_patterns:

        each_pred = each_pred_tuple[0]
        each_pred_flag = each_pred_tuple[1]

        ## count number of time and money tags
        curr_time_label = re.findall(r'<TIME-\d+>', each_pred)
        curr_money_label = re.findall(r'<MONEY-\d+>', each_pred)
        to_part = re.findall(r'to <MONEY-\d+>', each_pred)
        to_and_part = re.findall(r'to <MONEY-\d+> and <MONEY-\d+>', each_pred)

        if len(curr_time_label) == len(curr_money_label):
            curr_matched_tuple = curr_matched_tuple + \
                                 [(curr_time_label[i], curr_money_label[i], each_pred, each_pred_flag) for i in
                                  range(len(curr_time_label))]
        elif len(to_part) == len(curr_time_label):
            to_part_money = re.findall(r'<MONEY-\d+>', ' '.join(to_part))
            curr_matched_tuple = curr_matched_tuple + \
                                 [(curr_time_label[i], to_part_money[i], each_pred, each_pred_flag) for i in
                                  range(len(curr_time_label))]
        elif len(to_and_part) * 2 == len(curr_time_label):
            to_and_part_money = re.findall(r'<MONEY-\d+>', ' '.join(to_and_part))
            curr_matched_tuple = curr_matched_tuple + \
                                 [(curr_time_label[i], to_and_part_money[i], each_pred, each_pred_flag) for i in
                                  range(len(curr_time_label))]
        else:
            not_matched.append(each_pred_tuple)
    # deduplication
    curr_matched_tuple_dedup = list(set(curr_matched_tuple))

    return curr_matched_tuple_dedup, not_matched


def extractEstimatesNew(input_data):

    # we process record one by one
    for each_pred in input_data:

        ## perform masking
        curr_masking, curr_mapping = maskTimeMoney(each_pred['tagging'])
        each_pred['text_masking_dict'] = curr_masking
        each_pred['mapping'] = curr_mapping

        # print(each_pred['note_main'])

        ## control input sequences
        sent_pending_process = [i for i in each_pred['text_masking_dict'].items()
                                if 'EPS estimate' in i[1]
                                or 'loss per share estimate' in i[1]
                                or 'per share loss estimate' in i[1]]

        ## extract patterns
        curr_extracted_patterns = extractPatterns(sent_pending_process)
        # print(curr_extracted_patterns)

        ## generate forecasts
        curr_extracted_tuples, not_matched = genForecastTuples(curr_extracted_patterns)
        # if not_matched != []:
        #     print(each_pred['note_main'])
        #     print(each_pred['id'])
        #     print(not_matched)

        ## mapping back and reverse label
        curr_extracted_est = []
        for each_tuple in curr_extracted_tuples:
            if 'LOSS' in each_tuple[3]:
                curr_extracted_est.append([each_pred['mapping'][each_tuple[0]],
                                           '-' + each_pred['mapping'][each_tuple[1]],
                                           each_tuple[2],
                                           each_tuple[3]])
            else:
                curr_extracted_est.append([each_pred['mapping'][each_tuple[0]],
                                           each_pred['mapping'][each_tuple[1]],
                                           each_tuple[2],
                                           each_tuple[3]])
        # print(curr_extracted_est)
        each_pred['pred'] = curr_extracted_est

        ## organize format
        reorganized_pred = []
        # deal with a loss of:
        for each_est in curr_extracted_est:
            if 'loss' in each_est[1]:
                each_est[1] = each_est[1].replace('a loss of', '').replace('loss', '').replace(' ', '')
            if 'EPS' in each_est[1]:
                each_est[1] = each_est[1].replace('EPS', '')
        for each_est in curr_extracted_est:
            if '14' in each_est[0]:
                reorganized_pred.append(('2014', each_est[1].replace('$', '').replace('US', '')))
            elif '15' in each_est[0]:
                reorganized_pred.append(('2015', each_est[1].replace('$', '').replace('US', '')))
            elif '16' in each_est[0]:
                reorganized_pred.append(('2016', each_est[1].replace('$', '').replace('US', '')))
            elif '17' in each_est[0]:
                reorganized_pred.append(('2017', each_est[1].replace('$', '').replace('US', '')))
            elif '18' in each_est[0]:
                reorganized_pred.append(('2018', each_est[1].replace('$', '').replace('US', '')))
            #     print(i['pred'], curr_pred_trans)

        if each_pred['pred']:
            each_pred['pred_updated'] = sorted(reorganized_pred, key=lambda x: x[0])
        else:
            each_pred['pred_updated'] = []

        # print(each_pred['pred_updated'])

    return input_data