# TODO: add reasonong
classification_prompt = """Classify the following pdf page based on its content.

It should be either one of the following forms first page or `other` if it does not match any of them.

The text itself contains obvious hints, whether is the name of the form or schedule, or definition as e.g. individual income tax return or form number.

Use the following form types for classification:
- `1040f` - Form 1040 (main individual income tax return)  
- `f1040sa` - Schedule A (itemized deductions)  
- `f1040sb` - Schedule B (interest and dividends)  
- `f1040sc` - Schedule C (business income)  
- `f1040sd` - Schedule D (capital gains/losses)  
- `f1040se` - Schedule E (rental and partnership income)  
- `f1040s1` - Schedule 1 (additional income)  
- `f1040s2` - Schedule 2 (additional taxes)  
- `f1040s3` - Schedule 3 (additional credits)  
- `f8863` - Form 8863 (education credits)  
- `f8812` - Form 8812 (child tax credit)  
- `f2441` - Form 2441 (child and dependent care expenses)
- `other` - if the form does not match any of the above types
"""
