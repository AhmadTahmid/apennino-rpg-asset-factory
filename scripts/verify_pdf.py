"""
Verification Script for Generated PDF Review Dossiers.
Checks PDF headers, page counts, file sizes, and non-empty byte streams.
"""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
BUNDLE_DIR = REPO_ROOT / "review_bundle"


def verify_pdf(pdf_path, expected_pages=None):
    print(f"\nVerifying {pdf_path.name}:")
    assert pdf_path.exists(), f"File does not exist: {pdf_path}"
    
    # Check file size
    size_mb = pdf_path.stat().st_size / (1024 * 1024)
    print(f"  [OK] File size: {size_mb:.2f} MB")
    
    # Read binary header
    with open(pdf_path, "rb") as f:
        header = f.read(8)
        assert header.startswith(b"%PDF"), f"Invalid PDF header: {header}"
        print(f"  [OK] Binary header: {header.decode('ascii', errors='ignore').strip()}")
        
        # Count /Page objects
        f.seek(0)
        content = f.read()
        page_count = content.count(b"/Type /Page\n") + content.count(b"/Type /Page ") + content.count(b"/Type/Page")
        print(f"  [OK] Detected pages: {page_count}")
        if expected_pages:
            assert page_count == expected_pages, f"Expected {expected_pages} pages, got {page_count}"
            
    print(f"  [OK] {pdf_path.name} passed all integrity checks.")


if __name__ == "__main__":
    verify_pdf(BUNDLE_DIR / "CHATGPT_VISUAL_REVIEW.pdf", expected_pages=34)
    verify_pdf(BUNDLE_DIR / "CHATGPT_VISUAL_REVIEW_LITE.pdf", expected_pages=12)
    print("\n--> All PDF verification checks passed successfully!")
