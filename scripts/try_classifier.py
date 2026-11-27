from clauselens.config import get_settings
from clauselens.ingest.parser import parse_pdf
from clauselens.llm.cache import ResponseCache
from clauselens.llm.router import make_client
from clauselens.classify.classifier import classify_document


def main():
    settings = get_settings()
    client = make_client(settings)
    cache = ResponseCache(settings.cache_dir)

    pdf_path = "data/lease_01.pdf"  # Adjust to an existing PDF path.

    blocks = parse_pdf(pdf_path)

    first_page_text = "\n".join(
        block.text for block in blocks if block.page == 1
    )

    result = classify_document(
        client,
        settings,
        cache,
        first_page_text,
    )

    print("Document type:", result.doc_type)
    print("Reason:", result.reason)


if __name__ == "__main__":
    main()