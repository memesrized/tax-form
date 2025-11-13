# tax-form

It's a small repo for take home task.

# Task
TL;DR 
You need to detect spans of pages that are pre defined tax forms.
You have give 10 documents, ground truth for those documents and classes of tax forms.

# Data
PDFs with dozens of pages with tax forms and additional documents/information.
Ground truth is a json file for each document with the following structure:
```
[
    {
        "start_page": 1,
        "end_page": 10,
        "document_type": "%type%"
    },
    ...
]
```

# General Idea

TL;DR *classify pages one by one to find the start of a form -> check each of the following pages if they belong to the form -> if the end of the form is reached, start looking for another form start page.*

The easiest way is to give an LLM the whole PDF in one or another way (e.g. depends on API features for internal PDF parsing provider provides or in availability of vision capabilities of the LLM).

This is inefficient (especially with shots), too complex, hallucination prone, we may hit context window limits depending on PDF size. 

More optimized approach is to use sliding/expanding window (add pages to the input untill we reach the end of a form), but it's still logN context size and ~logN^2 (not really, but you got the point) compute time. Some problems are mitigated, but still exist.

My approach is to make log1 context size and logN time by using 2 step approach.
1. Detect if the page if the first page of a form (and what is the form)
2. Until we hit the end of the form detect if this page belongs to the form where form represented by the very first page and the previous page to the current.

# Implementation

TL;DR *final implementation*
1. *process PDFs (for each page extract image and text with pymupdf, prepare shots)*
    - *images with reasonable dpi, as small is possible to make text more or less visible*
    - i use gpt-5 (not the first pick), strong enough, vision capabilities
2. *run the pipeline*
    1. *load model from config with langchain* - any vendor, you just need proper extension for langchain installed
    2. *first page classification*
        - *LLM based, input is text from the page*
        - *parse structured output*
    3. *form continuation page classification*
        - *LLM based, input is images*
            - *start of the form, previous page, current page*
        - *parse structured output*
3. *eval*
    1. *prepare data*
    2. *run F1 score with micro (among all forms) and macro (among documens) averaging*
        - *this is basically NER task with (start, end, label) entries*
        - *so there are two modes: exact and overlap*
---
Data processing:
- I started with data processing implementation and added shots for firsrt page classification but they were not used in the end, but there they are.
- As for pdf parsing lib I picked pymupdf because I used it before on the similar project and it worked very well.
- I picked the DPI manually testing iteratively how bad the output image is. Started with ~300 ended with 55. 

The pipeline:
- Then I implemented classification of the first page of form
    - The first idea was to use plain text as it contains enough hints to detect (almost exact words)
        - In this setup it can be even rules since forms should be pretty restricted to a certain format
        - But it requires EDA and some statistics to check if this true for all docs that we have (or to research US forms documentation)
        - It's not the case for such short project, so it was decided to just use a sledgehammer (llm) to crack a nut.
    - It didn't work with OSS-120b, the quality was too poor.
        - Then I thought that probablt it's lack of the information about page layout.
        - So it's time to add images to the input.
            - *Yes, we could use it from the start, but ask LLM to do OCR (not literally, but internally to understand the text on the picture) toghether with classification may lead to hallucinations and poor performance due to the complexity of the task.*
        - But OSS models don't support multimodality.
        - So it's time to switch to VLMs
            - I have OpenAI key, so I decided to use it, but it can be any model. The same was with groq and OSS-120b, I just have the key from another pet project.
        - So it's GPT-5 with low reasoning.
    - And it magically works without picture, just with text.
        - Not sure why OSS-120b it that weak, it served me well before, but it is what it is.
        - We don't need images for first page classification anymore.
    - Here it is. GPT-5, low reasoning, text from the page.
- Form continuation classification
    - My assumption for this task is that it's not obvious only from text if the page continues the form.
    - Let's use images directly without text since we rather need structural information.
    - To be honest we still need a little bit of text understanding from pictures, but it should be ok in this setup.
    - Used the same GPT-5 with low reasoning.
    - Works very well for a naked eye.
- The pipeline itself is a bunch of ifs and whiles, nothing to see here.

Evaluation:
- We can reformulate the problem that we have as a NER, since we have start, end and label as target.
- So we can have exact matches or at least overlaps (e.g. we don't catch the last page)
    - In some scenarious it can be helpful, e.g. if the result is still human validated.
- Other than that it's just F1, precision and recall.
    - Not sure if we prefer recall or precision
    - But probably recall, we can add another layer of filtering later, I guess.

# Metrics

```
============================================================
MICRO-AVERAGED METRICS (Overall - Exact Match)
============================================================
Precision: 0.8475
Recall:    0.7937
F1 Score:  0.8197

True Positives:  50
False Positives: 9
False Negatives: 13


============================================================
MACRO-AVERAGED METRICS (Mean per Document - Exact Match)
============================================================
Precision: 0.7726
Recall:    0.7464
F1 Score:  0.7571

Number of Documents: 10
```

# Room for improvements

Since the main trade off was between simplicity (i.e. development time) and overall quality, the project has a lot to improve.
- Notebooks to scripts
    - Add proper async, it won't help for a single document since it's a sequential process, but would drastically speed up whole dataset processing.
    - Easier to embed in a pipeine like Airflow
    - Just a good practice not to keep and maintain production ready code in notebooks, only experiments (which is the whole this repo to be hones due to timelimits)
- LLMs
    - Add support for non-reasoning models with "reasoning" field in structured outputs.
    - Play around with different setups for input data, it requires a proper evaluation, just assumptoins is not enough. Maybe we can use only pictures.
        - Also it should impact the processing speed depending on the number of tokens from an image (and image size) vs text
    - Try other models besides GPT, something definitely should be cheaper and faster, but with reasonable quality (local models included).
    - Add shots if necessary for quality improvements, tests are needed.
- Processing
    - Proper async as mentioned
        - Proper handling for rate limits (tokens/requests)
    - Error handling, retries
    - Proper logging for logs and error
    - Store outputs in db, not in files 
- Eval
    - other metrics, align with business needs
    - output in a file
- Repo
    - linters/fromatter + check on pull requests (flake8 + Ruff)    
        - check my [another repo](https://github.com/memesrized/yadbil) for precommit and linter/formatter configuration if needed
    - optional requirements with pyproject.toml
    - Input and output data via git-lfs? for illustrative purposes


# How to run

1. copy data into `data/` folder
    - `data/input` - list of pdfs
    -  `data/target` - list of jsons
2. ofc reqs
    - `pip install -r requirements.txt`
    - `pip install .`
3. create model config (for openai you can skip it)
4. add .env with api_key key from model config and the api_key itself
5. run notebooks (with proper paths specified)
    1. data_processing.ipynb
    2. pipeline.ipynb
    3. eval.ipynb

# AI usage
Most of the time just autocomplete with copilot.

Evals metrics generated with copilot agent w/ sonnet 4.5, just a couple of prompts, nothing special.