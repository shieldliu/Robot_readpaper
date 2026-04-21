import os

import fitz  # PyMuPDF


def main() -> None:
    pdf_path = "paper.pdf"
    out_dir = "figures"
    os.makedirs(out_dir, exist_ok=True)

    doc = fitz.open(pdf_path)
    img_count = 0
    seen_xrefs: set[int] = set()

    for page_num in range(len(doc)):
        page = doc[page_num]
        for img in page.get_images(full=True):
            xref = int(img[0])
            if xref in seen_xrefs:
                continue
            seen_xrefs.add(xref)

            base = doc.extract_image(xref)
            ext = base.get("ext", "bin")
            data = base["image"]

            out_path = os.path.join(out_dir, f"fig-{img_count:03d}.{ext}")
            with open(out_path, "wb") as f:
                f.write(data)
            print(f"Extracted: {out_path} (page {page_num + 1}, {len(data)} bytes)")
            img_count += 1

    print(f"Total: {img_count} figures extracted")


if __name__ == "__main__":
    main()

