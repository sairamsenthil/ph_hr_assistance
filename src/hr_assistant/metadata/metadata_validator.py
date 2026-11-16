def validate_documents(documents: list[dict]) -> list[str]:
    """
    Validate required metadata and page-level consistency.

    Returns a list of validation errors.
    An empty list means validation passed.
    """

    errors = []
    seen_pages = set()
    document_registry = {}

    required_fields = [
        "document_id",
        "source",
        "document_type",
        "page"
    ]

    if not documents:
        return ["No documents provided for validation."]

    for index, document in enumerate(documents, start=1):

        metadata = document.get("metadata")

        if not isinstance(metadata, dict):
            errors.append(
                f"Record {index}: metadata must be a dictionary."
            )
            continue

        # Check required fields.
        for field in required_fields:
            if field not in metadata:
                errors.append(
                    f"Record {index}: missing metadata field '{field}'."
                )

        # Validate string fields.
        for field in ["document_id", "source", "document_type"]:
            value = metadata.get(field)

            if not isinstance(value, str) or not value.strip():
                errors.append(
                    f"Record {index}: '{field}' must be a non-empty string."
                )

        # Validate page number.
        page = metadata.get("page")

        if type(page) is not int or page <= 0:
            errors.append(
                f"Record {index}: 'page' must be a positive integer."
            )
            continue

        document_id = metadata.get("document_id")
        source = metadata.get("source")
        document_type = metadata.get("document_type")

        # Check duplicate page identity.
        if isinstance(document_id, str) and document_id.strip():

            page_identity = (document_id, page)

            if page_identity in seen_pages:
                errors.append(
                    f"Record {index}: duplicate page {page} "
                    f"for document '{document_id}'."
                )
            else:
                seen_pages.add(page_identity)

            # Check document-level consistency.
            if isinstance(source, str) and isinstance(document_type, str):

                current_identity = (source, document_type)

                if document_id in document_registry:
                    if document_registry[document_id] != current_identity:
                        errors.append(
                            f"Record {index}: inconsistent source or "
                            f"document_type for document '{document_id}'."
                        )
                else:
                    document_registry[document_id] = current_identity

    return errors


if __name__ == "__main__":

    import json

    from ..config import PROCESSED_DATA_DIR

    input_file = PROCESSED_DATA_DIR / "hr_policy_pages.jsonl"

    documents = []

    with input_file.open("r", encoding="utf-8") as file:
        for line in file:
            documents.append(json.loads(line))

    validation_errors = validate_documents(documents)

    print("\n--- METADATA VALIDATION REPORT ---")
    print("Total records:", len(documents))

    if validation_errors:
        print("Validation status: FAILED")
        print("Total errors:", len(validation_errors))

        for error in validation_errors:
            print("-", error)
    else:
        print("Validation status: PASSED")
        print("Total errors: 0")
        print("All metadata checks passed.")