import json
from pathlib import Path
from whoosh import index
from whoosh.fields import Schema, TEXT, ID
from whoosh.analysis import StemmingAnalyzer

DOCS_PATH = Path("data/docs.jsonl")
INDEX_DIR = Path("index")

def build_index():
    INDEX_DIR.mkdir(exist_ok=True)
    schema = Schema(
        url=ID(stored=True, unique=True),
        title=TEXT(stored=True, analyzer=StemmingAnalyzer()),
        section=TEXT(stored=True, analyzer=StemmingAnalyzer()),
        content=TEXT(stored=True, analyzer=StemmingAnalyzer())
    )
    if index.exists_in(INDEX_DIR):
        ix = index.open_dir(INDEX_DIR)
        ix.close()
        # recreate for deterministic rebuild
        for p in INDEX_DIR.glob("*"):
            p.unlink()
    ix = index.create_in(INDEX_DIR, schema)
    writer = ix.writer(limitmb=256, procs=1, multisegment=True)

    doc_count = 0
    with DOCS_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            d = json.loads(line)
            doc_count += 1
            # Deduplicate by URL + section
            unique_url = d["url"] + ("#" + d["section"] if d.get("section") else "")
            writer.update_document(
                url=unique_url,
                title=d.get("title", ""),
                section=d.get("section", ""),
                content=d.get("content", "")
            )
            if doc_count % 50 == 0:
                print(f"BUILDING: Processed {doc_count} document sections")
    writer.commit()
    print("Index built at", INDEX_DIR)

if __name__ == "__main__":
    build_index()