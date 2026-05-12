from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED


BASE_DIR = Path(__file__).resolve().parent.parent
source = BASE_DIR / "docs" / "documento_analisi.md"
target = BASE_DIR / "docs" / "documento_analisi.docx"


def xml_escape(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def build_document_xml(paragraphs: list[str]) -> str:
    body = []
    for paragraph in paragraphs:
        text = xml_escape(paragraph)
        body.append(
            "<w:p><w:r><w:t xml:space=\"preserve\">"
            f"{text}"
            "</w:t></w:r></w:p>"
        )
    body_xml = "".join(body)
    return (
        "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>"
        "<w:document xmlns:w=\"http://schemas.openxmlformats.org/wordprocessingml/2006/main\">"
        f"<w:body>{body_xml}<w:sectPr/></w:body>"
        "</w:document>"
    )


def build_docx() -> None:
    paragraphs = [line.rstrip() for line in source.read_text(encoding="utf-8").splitlines()]
    content_types = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>
"""
    rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>
"""
    with ZipFile(target, "w", ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", content_types)
        archive.writestr("_rels/.rels", rels)
        archive.writestr("word/document.xml", build_document_xml(paragraphs))


if __name__ == "__main__":
    build_docx()
