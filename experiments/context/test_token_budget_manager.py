from tokenizers import Tokenizer

from src.hr_assistant.context.token_budget_manager import (
    TokenBudgetManager
)


TOKENIZER_NAME = "mixedbread-ai/mxbai-embed-large-v1"


def main():

    tokenizer = Tokenizer.from_pretrained(
        TOKENIZER_NAME
    )

    manager = TokenBudgetManager(tokenizer)

    contexts = [
        "SOURCE 1\nPolicy: Leave Policy\nEmployees are entitled to annual leave.",
        "SOURCE 2\nPolicy: Grievance Policy\nEmployees can raise workplace grievances.",
        "SOURCE 3\nPolicy: Attendance Policy\nEmployees must follow attendance procedures."
    ]

    result = manager.fit_contexts(
        contexts=contexts,
        token_budget=40
    )

    print("\n--- TOKEN BUDGET MANAGEMENT ---")

    for key, value in result.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()