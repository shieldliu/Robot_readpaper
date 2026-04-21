import fitz
import os

doc = fitz.open("C:/Users/admin/Documents/read_paper/Robot_readpaper/paper-2026-04-16-pi0-7/paper.pdf")
os.makedirs("C:/Users/admin/Documents/read_paper/Robot_readpaper/paper-2026-04-16-pi0-7/figures", exist_ok=True)
img_count = 0
for page_num in range(len(doc)):
    page = doc[page_num]
    images = page.get_images(full=True)
    for img in images:
        xref = img[0]
        base_image = doc.extract_image(xref)
        image_bytes = base_image["image"]
        image_ext = base_image["ext"]
        with open(f"C:/Users/admin/Documents/read_paper/Robot_readpaper/paper-2026-04-16-pi0-7/figures/fig-{img_count:03d}.{image_ext}", "wb") as f:
            f.write(image_bytes)
        print(f"Extracted: fig-{img_count:03d}.{image_ext} (page {page_num + 1})")
        img_count += 1
print(f"Total: {img_count} figures extracted")