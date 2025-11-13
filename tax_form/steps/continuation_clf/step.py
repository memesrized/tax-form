from langchain.messages import HumanMessage
from langchain_core.language_models.chat_models import BaseChatModel

from tax_form.steps.continuation_clf.prompts import classification_prompt
from tax_form.steps.continuation_clf.structured_outputs import ClassificationResult
from tax_form.dataset import Page


def classify_continuation_page(
    current_page: Page, previous_page: Page, start_page: Page, llm: BaseChatModel
) -> bool:
    human_message = HumanMessage(
        content=[
            {"type": "text", "text": classification_prompt},
            {"type": "text", "text": "Form start page image:"},
            {
                "type": "image",
                "base64": start_page.image,
                "mime_type": "image/png",
            },
            {"type": "text", "text": "Previous page image:"},
            {
                "type": "image",
                "base64": previous_page.image,
                "mime_type": "image/png",
            },
            {"type": "text", "text": "Current page image:"},
            {
                "type": "image",
                "base64": current_page.image,
                "mime_type": "image/png",
            },
        ]
    )

    # method="json_schema" is required by groq
    result = llm.with_structured_output(
        ClassificationResult, method="json_schema"
    ).invoke([human_message])
    return result.is_continuation
