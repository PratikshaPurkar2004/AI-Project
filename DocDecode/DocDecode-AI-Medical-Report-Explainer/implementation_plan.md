# OCR for Scanned Reports

## Goal Description
Add OCR capability to the existing DocDecode app to extract text from scanned/image-only PDF radiology reports, enabling downstream explanation, extraction, and Q&A features.

## Proposed Changes
### app
- **[MODIFY] app.py**: Add a new Streamlit tab "OCR Upload" with file uploader for scanned PDFs. Use `pdf2image` to convert PDF pages to images and `pytesseract` for OCR. Insert preprocessing with Pillow (grayscale, threshold) and optional OpenCV deskew.
- **[NEW] ocr_utils.py**: Helper functions `pdf_to_images`, `preprocess_image`, `perform_ocr`.
- **[MODIFY] requirements.txt**: Add `pytesseract`, `pdf2image`, `Pillow` (and `opencv-python` if used).
- **[MODIFY] app.py**: Update session state to store `ocr_extracted_text` and allow user to edit before analysis.

### health_dashboard
- **[NEW] health_dashboard.py**: Streamlit page that visualizes health metrics (mock data). Uses `pandas`, `plotly`, and Streamlit widgets.
- **[MODIFY] app.py**: Add navigation to health dashboard via `st.sidebar` or multi‑page `pages/health_dashboard.py`.
- **[MODIFY] requirements.txt**: Add `pandas`, `plotly`.

### report_comparison
- **[NEW] compare.py**: Functions to load two reports (text) and compute similarity metrics (BLEU, ROUGE, cosine similarity using embeddings). Provide a Streamlit UI to upload two PDFs or paste texts and display side‑by‑side comparison with highlighted differences.
- **[MODIFY] app.py**: Add a new tab "Compare Reports" that uses `compare.py`.
- **[MODIFY] requirements.txt**: Add `nltk`, `rouge-score`, `sentence-transformers`.

## Verification Plan
### Automated Tests
- **test_ocr.py**: Unit test for `ocr_utils.perform_ocr` using a known sample image (generated via Pillow) and asserting extracted text contains expected words.
- **test_dashboard.py**: Smoke test that imports `health_dashboard` and calls a function to generate a Plotly figure; ensure no exceptions.
- **test_compare.py**: Test `compare.compute_similarity` with two short strings; verify similarity scores are within expected range.

All tests will be placed in `tests/` and run via `pytest`. Existing CI will pick them up.

### Manual Verification
1. **OCR Tab**: Upload a scanned PDF (provide sample image PDF). Verify extracted text appears in the text area and can be used by existing explanation/extraction features.
2. **Health Dashboard**: Navigate to the dashboard page, adjust date range, and confirm charts render and download button works.
3. **Report Comparison**: Upload two reports, view side‑by‑side view, and ensure similarity metrics display.

### Steps to Run Verification
```bash
# Install dependencies
pip install -r requirements.txt
# Run unit tests
pytest -q
# Launch the app
streamlit run app.py
```

**User Review Required**
- Preferred OCR library (pytesseract vs alternative) and whether Tesseract is installed on the target system.
- Desired data source for the health dashboard (mock data is fine or real CSV upload?).
- Specific comparison metrics or visual style for the report comparison feature.
- Any UI design preferences (color scheme, layout) to align with existing app aesthetics.
