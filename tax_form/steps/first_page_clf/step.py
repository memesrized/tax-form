from langchain_core.language_models.chat_models import BaseChatModel

from tax_form.dataset import Page
from tax_form.steps.first_page_clf.prompts import classification_prompt
from tax_form.steps.first_page_clf.structured_outputs import ClassificationResult


# TODO: add image + shots ?
# not sure if image useful without shots
def classify_form_start(page: Page, llm: BaseChatModel) -> str:
    prompt = classification_prompt
    prompt += "\n---\n"
    prompt += f"Text content of the page:\n```{page.text}```\n"

    # method="json_schema" is required by groq
    result: ClassificationResult = llm.with_structured_output(
        ClassificationResult, method="json_schema"
    ).invoke(prompt)
    return result.page_type
