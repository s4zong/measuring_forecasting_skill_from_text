
# Measuring Forecasting Skill from Text

This repository contains the resources from the following paper:

Measuring Forecasting Skill from Text

Shi Zong, Alan Ritter, Eduard Hovy

ACL 2020

https://www.aclweb.org/anthology/2020.acl-main.473.pdf

```
@inproceedings{zong-etal-2020-measuring,
    title = "Measuring Forecasting Skill from Text",
    author = "Zong, Shi  and
      Ritter, Alan  and
      Hovy, Eduard",
    booktitle = "Proceedings of the 58th Annual Meeting of the Association for Computational Linguistics",
    month = jul,
    year = "2020",
    address = "Online",
    publisher = "Association for Computational Linguistics",
    url = "https://www.aclweb.org/anthology/2020.acl-main.473",
    pages = "5317--5331",
}
```

### Dataset descriptions

Due to privacy and policy restrictions, we are only able to provide the question IDs for Good Judgment Open dataset and report IDs (from THOMSON ONE database) for financial dataset under `dataset` folder. Please check library subscriptions of your institution for accessing THOMSON ONE database.

### Extracting information from PDF files

#### Preprocess PDF files

We provide some suggestions / methods that we find useful in practice when converting pdf files into text.

- We suggest first split pdf files into single pages, then combine pages with same layout for easier batch process.
- When extracting paragraph contents from pdf files, we suggest open files by using pdf readers (e.g., Adobe) and directly copy text out. Using some automatic tools may introduce many line breaks, making it hard to recover the original paragraph structures.
- We suggest crop pdf pages into the area needed to make the post process easier.
- Automatic tools (e.g., [tabula](https://github.com/tabulapdf/tabula)) could be used for structured table extractions.
- Always add some separators in header part of pdf files to divide different pages.

We provide some sample processing codes under `extraction` folder. Note that you may need to adjust the parameters (for example the number of blank spaces and the pixel location for extraction areas) for your own needs.

#### Extract financial numerical estimates

We provide our code for extracting financial numerical estimates from analysts notes in `extract_numerical_forecasts.py`.

We tokenize our financial analyst notes by Stanford CoreNLP. The tagging results shall be organized in .jsonl format: each line has a 'tagging' field containing a list, with each element a tuple `[a_sentence_id, a_tokenized_sentence]` (note that tokenized money values need to be recovered, e.g., to reconnect '$' and '10' into '$10' as shown in the following example). Then run `extractEstimatesNew(input_data)` to get the extraction results.

```angular2
[{'tagging': 
      [['23038356-0-0', 'We are keeping our EPS forecast for CI , but boost our target price by $10 to $97 ,
                        on revised P/E analysis .'],
       ['23038356-0-1', 'X X X'],
       ['23038356-0-2', 'X X X']]}
]
```


### Computational linguistic tools used

We list the computational linguistic tools used in this paper.

- Uncertainty: https://github.com/heikeadel/attention_methods
- LIWC: https://liwc.wpengine.com/
- SO-CAL: https://github.com/sfu-discourse-lab/SO-CAL
- Discourse lexicon: http://connective-lex.info/
- Financial sentiment: https://sraf.nd.edu/textual-analysis/resources/


