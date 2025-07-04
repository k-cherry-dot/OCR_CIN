import cv2
import pytesseract
import re
import pandas as pd
from datetime import datetime
from difflib import SequenceMatcher
from pdf2image import convert_from_path
from PIL import Image
import os


#now debugged for multiple given names and surnames


pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
# path problems with tesseract so i have to manually set this up

# extraction part (unchanged)

def preprocess_mrz_region(image, mrz_height_ratio=0.20):
    """
    crop the bottom portion of the card (where mrz lives), convert to grayscale,
    apply a binary threshold, and return the processed image.

    mrz_height_ratio: fraction of image height to treat as mrz (e.g. bottom 20%).
    """
    h, w = image.shape[:2]
    mrz_start_y = int(h * (1 - mrz_height_ratio))
    mrz_crop = image[mrz_start_y: h, 0: w]

    gray = cv2.cvtColor(mrz_crop, cv2.COLOR_BGR2GRAY)
    # apply a moderate gaussian blur to reduce noise
    # equalize histogram to boost contrast
    gray = cv2.equalizeHist(gray)
    gray = cv2.GaussianBlur(gray, (3, 3), 0)

    # adaptive threshold (works well with varying lighting)
    th = cv2.adaptiveThreshold(
        gray,
        maxValue=255,
        adaptiveMethod=cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        thresholdType=cv2.THRESH_BINARY_INV,
        blockSize=31,
        C=15
    )

    # invert back so characters are dark on light if needed (pytesseract prefers dark-on-light)
    processed = cv2.bitwise_not(th)
    return processed, mrz_crop

#if Tesseract doesnt return exactly 3 28-32 char lines, we fall back to taking the three longest lines overall, instead of failing
def ocr_mrz_lines(processed_img):
    """
    run tesseract on the preprocessed MRZ image, force a whitelist,
    then pick the 3 best lines (by length & confidence), padding/truncating to 30 chars.
    """
    # 1) OCR with explicit config
    custom_config = (
        "--oem 3 --psm 6 "  # psm 6 = assume uniform block of text
        "-c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789<"
    )
    # get both text **and** detailed per-line confidences
    raw = pytesseract.image_to_string(processed_img, config=custom_config)

    # 2) split into non-empty lines, strip spaces
    lines = [l.replace(" ", "").strip() for l in raw.splitlines() if l.strip()]
    if not lines:
        raise ValueError("No text detected in MRZ region")

    # 3) filter for MRZ-like lengths (28–32 chars)
    candidates = [ln for ln in lines if 28 <= len(ln) <= 32]

    # 4) if fewer than 3, **also** consider any longer/shorter lines as backup
    if len(candidates) < 3:
        # take the 3 longest lines overall
        candidates = sorted(lines, key=len, reverse=True)[:3]

    # 5) still fewer than 3? give up now
    if len(candidates) < 3:
        raise ValueError(f"Could not detect 3 MRZ lines. OCR output: {lines}")

    # 6) pick the top 3 by length, then normalize to exactly 30 chars
    top3 = sorted(candidates, key=len, reverse=True)[:3]
    mrz_lines = [(ln + "<" * 30)[:30] for ln in top3]
    return mrz_lines



def parse_mrz_data(line1, line2, line3):
    """
    parse three 30-char mrz lines to extract:
      - card_number: the 8-char id that follows a single '<' + one filler char
      - date_of_birth: positions 0–5 on line2 → yyyy-mm-dd
      - gender: position 7 on line2
      - surname & given_names from line3 (split on '<<')

    this uses regex for card_number instead of fixed positions.
    """
    # normalize any stray 'x' → '<'
    line1 = line1.replace("X", "<")
    line3 = line3.replace("X", "<")

    # ─── extract card_number via regex ──────────────────────────────────
    # look for: one '<', then exactly one filler char, then 8 alphanumerics
    m = re.search(r"<.(?P<id>[A-Z0-9]{8})", line1)
    if m:
        card_number = m.group("id")
    else:
        # fallback to the old slice if regex fails
        raw_card = line1[16:24]
        card_number = raw_card.replace("<", "")

    # ─── date of birth (yy mm dd → yyyy-mm-dd) ────────────────────────
    dob_raw = line2[0:6]
    try:
        yy = int(dob_raw[0:2])
        year = 2000 + yy if yy <= 25 else 1900 + yy
        month = int(dob_raw[2:4])
        day = int(dob_raw[4:6])
        date_of_birth = datetime(year, month, day).strftime("%Y-%m-%d")
    except:
        date_of_birth = f"invalid({dob_raw})"

    # ─── gender ────────────────────────────────────────────────────────
    gender = line2[7] if line2[7] in ("M", "F") else "?"

    # ─── names: split surname vs given by '<<' ─────────────────────────
    name_field = line3.rstrip("<")
    if "<<" in name_field:
        surname_raw, given_raw = name_field.split("<<", 1)
    else:
        surname_raw, given_raw = name_field, ""

    # handle multiple surnames (single '<' separators)
    surnames = [part for part in surname_raw.split("<") if part]
    surname = " ".join(surnames)

    # handle multiple given names (single '<' separators)
    given_parts = [part for part in given_raw.split("<") if part]
    given_names = " ".join(given_parts)

    return {
        "card_number":   card_number,
        "date_of_birth": date_of_birth,
        "gender":        gender,
        "surname":       surname,
        "given_names":   given_names
    }

def extract_from_image(input_path):
    """
    Si input_path finit par .pdf → convertit la page en image avant OCR.
    Retourne le même dict que précédemment.
    """
    # 1) obtenir un fichier image sur le disque
    ext = os.path.splitext(input_path)[1].lower()
    if ext == '.pdf':
        # convertit la page 1 en image (PIL)
        images = convert_from_path(input_path, first_page=1, last_page=1)
        if not images:
            raise ValueError("Impossible de convertir le PDF en image")
        # enregistre temporairement
        temp_img_path = input_path + '.jpg'
        images[0].save(temp_img_path, 'JPEG')
        img_path = temp_img_path
    else:
        img_path = input_path

    # 2) charger l’image avec OpenCV
    img = cv2.imread(img_path)
    if img is None:
        raise FileNotFoundError(f"Impossible de lire l’image à '{img_path}'")
    #auto crop white border (car fichier pdf)
    gray_full = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    #invert white en black so the card becomes a white blob
    _, bw = cv2.threshold(gray_full, 240, 255, cv2.THRESH_BINARY_INV)
    cnts, _ = cv2.findContours(bw, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if cnts :
        c = max(cnts, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(c)
        img = img[y:y+h, x:x+w]


    # 3) exécuter la pipeline MRZ existante
    processed_mrz, mrz_crop = preprocess_mrz_region(img, mrz_height_ratio=0.40)
    mrz_lines = ocr_mrz_lines(processed_mrz)
    line1, line2, line3 = mrz_lines
    data = parse_mrz_data(line1, line2, line3)

    # 4) nettoyer le fichier temporaire si c’était un PDF
    if ext == '.pdf' and os.path.exists(temp_img_path):
        os.remove(temp_img_path)

    return data


# comparison part (uses csv) (works now)

def normalize_date(date_str):
    """
    Normalize various date formats to YYYY-MM-DD
    Handles: YYYY-MM-DD, DD/MM/YYYY, MM/DD/YYYY, DD-MM-YYYY, etc.
    """
    if not date_str or date_str.strip().upper() in ['', 'NAN', 'NULL', 'NONE']:
        return ""

    date_str = date_str.strip()

    # If already in YYYY-MM-DD format
    if re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
        return date_str

    # diff date patterns
    patterns = [
        (r'^(\d{2})/(\d{2})/(\d{4})$', lambda m: f"{m.group(3)}-{m.group(2)}-{m.group(1)}"),  # DD/MM/YYYY
        (r'^(\d{2})/(\d{2})/(\d{2})$', lambda m: f"20{m.group(3)}-{m.group(2)}-{m.group(1)}"),  # DD/MM/YY
        (r'^(\d{4})/(\d{2})/(\d{2})$', lambda m: f"{m.group(1)}-{m.group(2)}-{m.group(3)}"),  # YYYY/MM/DD
        (r'^(\d{2})-(\d{2})-(\d{4})$', lambda m: f"{m.group(3)}-{m.group(2)}-{m.group(1)}"),  # DD-MM-YYYY
        (r'^(\d{6})$', lambda m: f"20{m.group(1)[4:6]}-{m.group(1)[2:4]}-{m.group(1)[0:2]}"),  # DDMMYY
    ]

    for pattern, converter in patterns:
        match = re.match(pattern, date_str)
        if match:
            try:
                return converter(match)
            except:
                continue

    return date_str  #returns as is if there are no matches


def similarity_score(str1, str2):
    """Calculate similarity score between two strings (0-1, where 1 is identical)"""
    if not str1 and not str2:
        return 1.0
    if not str1 or not str2:
        return 0.0
    return SequenceMatcher(None, str1.upper(), str2.upper()).ratio()


def compare_with_csv(extracted: dict, csv_path: str, similarity_threshold: float = 0.8):
    """
    Enhanced comparison function with better handling of date formats and fuzzy matching

    Parameters:
        extracted: dict from parse_mrz_data
        csv_path: path to CSV file
        similarity_threshold: minimum similarity score for fuzzy matching (0-1)

    Returns:
        result: dict with detailed comparison results
    """
    # 1) loading the csv file
    try:
        df = pd.read_csv(csv_path, dtype=str)
    except Exception as e:
        raise RuntimeError(f"Could not read '{csv_path}': {e}")

    # stripping whitespace (added this after leaving a whitespace in one of my columns)
    df.columns = df.columns.str.strip()

    required_cols = ["card_number", "surname", "given_names", "date_of_birth", "gender"]
    for col in required_cols:
        if col not in df.columns:
            raise KeyError(f"Expected column '{col}' not found in CSV. Found: {list(df.columns)}")

    # 2) normalizing the extracted data
    extracted_norm = {}
    for key, value in extracted.items():
        if key == "date_of_birth":
            extracted_norm[key] = normalize_date(str(value))
        else:
            extracted_norm[key] = str(value).strip().upper() if value else ""

    # 3) find matching rows by card number (exact match) (this is bcs in the csv file, there will be a loooot of info)
    df_clean = df.copy()
    for col in required_cols:
        df_clean[col] = df_clean[col].astype(str).str.strip().str.upper()

    # First try exact card number match
    mask = df_clean["card_number"] == extracted_norm["card_number"]
    matched_rows = df_clean[mask]

    result = {
        "found_row": False,
        "matches": {},
        "similarity_scores": {},
        "expected": {},
        "extracted": extracted_norm,
        "issues_found": []
    }

    if matched_rows.shape[0] == 0:
        # try fuzzy matching on card number if exact match fails (added this after having some trouble)
        best_match_idx = None
        best_score = 0

        for idx, row in df_clean.iterrows():
            score = similarity_score(extracted_norm["card_number"], row["card_number"])
            if score > best_score and score >= similarity_threshold:
                best_score = score
                best_match_idx = idx

        if best_match_idx is not None:
            matched_rows = df_clean.iloc[[best_match_idx]]
            result["issues_found"].append(f"Card number fuzzy match (similarity: {best_score:.2f})")
        else:
            result["issues_found"].append("No matching card number found")
            return result

    # take the first matching row
    row = matched_rows.iloc[0]
    result["found_row"] = True

    # 4) normalize the expected data from CSV
    expected = {}
    for key in required_cols:
        if key == "date_of_birth":
            expected[key] = normalize_date(row[key])
        else:
            expected[key] = str(row[key]).strip().upper() if pd.notna(row[key]) else ""

    result["expected"] = expected

    # 5) perform detailed comparison
    for field in required_cols:
        extracted_val = extracted_norm[field]
        expected_val = expected[field]

        # Calculate similarity score
        sim_score = similarity_score(extracted_val, expected_val)
        result["similarity_scores"][field] = sim_score

        # determine if it's a match (exact or high similarity) (the treshold is 0.8)
        if extracted_val == expected_val:
            result["matches"][field] = True
        elif sim_score >= similarity_threshold:
            result["matches"][field] = True
            result["issues_found"].append(f"{field}: High similarity match ({sim_score:.2f})")
        else:
            result["matches"][field] = False
            result["issues_found"].append(
                f"{field}: Mismatch - extracted='{extracted_val}' vs expected='{expected_val}'")

    return result


def print_detailed_comparison(comparison_result):
    """Print a detailed comparison report"""
    print("DETAILED COMPARISON REPORT")

    if not comparison_result["found_row"]:
        print("No matching record found in CSV")
        return

    print("Matching record found in CSV\n")

    # print field-by-field comparison
    for field in ["card_number", "surname", "given_names", "date_of_birth", "gender"]:
        extracted = comparison_result["extracted"][field]
        expected = comparison_result["expected"][field]
        match = comparison_result["matches"][field]
        similarity = comparison_result["similarity_scores"][field]

        status = "MATCH" if match else "MISMATCH"
        print(f"{status} {field.upper():<12}")
        print(f"  Extracted: '{extracted}'")
        print(f"  Expected:  '{expected}'")
        print(f"  Similarity: {similarity:.2f}")
        print()

    # print issues found (for debugging purposes)
    if comparison_result["issues_found"]:
        print("Issued Detected:")
        for issue in comparison_result["issues_found"]:
            print(f" {issue}")

    # overall result
    all_match = all(comparison_result["matches"].values())
    if all_match:
        print("All fields match")
    else:
        match_count = sum(comparison_result["matches"].values())
        total_count = len(comparison_result["matches"])
        print(f"{match_count}/{total_count} FIELDS MATCH")


# main block
if __name__ == "__main__":
    import sys

    if len(sys.argv) != 3:
        print("Usage: python extract_and_check.py <id_image.jpg> <master_list.csv>")
        sys.exit(1)

    image_path = sys.argv[1]
    csv_path = sys.argv[2]

    try:
        # extract MRZ data from the ID image
        extracted = extract_from_image(image_path)
        print("EXTRACTED MRZ DATA:")
        for k, v in extracted.items():
            print(f"  {k}: {v}")

        # compare with CSV using enhanced comparison
        comparison = compare_with_csv(extracted, csv_path, similarity_threshold=0.8)

        # print detailed comparison report
        print_detailed_comparison(comparison)

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(3)

from app import db
from app.models import Upload, ComparisonResult
import os
import pandas as pd

def process_upload(upload_id):
    """
    1) Charge l’objet Upload depuis la BDD
    2) Construit les chemins complets vers le CSV et le PDF
    3) Appelle extract_from_image + compare_with_csv
    4) Génére un fichier Excel résumé
    5) Crée un ComparisonResult, marque l’Upload comme processed
    6) Retourne le ComparisonResult
    """
    up = Upload.query.get_or_404(upload_id)

    # Chemins complets
    csv_path = os.path.join(os.getcwd(), 'uploads', 'csv', up.csv_filename)
    pdf_path = os.path.join(os.getcwd(), 'uploads', 'pdf', up.pdf_filename)

    # Extraction et comparaison
    extracted = extract_from_image(pdf_path)  # ou gère conversion PDF→image
    comparison = compare_with_csv(extracted, csv_path, similarity_threshold=0.8)

    # Génération du Excel
    report_dir = os.path.join(os.getcwd(), 'uploads', 'reports')
    os.makedirs(report_dir, exist_ok=True)
    excel_path = os.path.join(report_dir, f'report_{upload_id}.xlsx')

    # Supposons que comparison["expected"] et comparison["extracted"] sont des dicts
    df = pd.DataFrame([{
        **comparison["extracted"],
        **{f"expected_{k}": v for k, v in comparison["expected"].items()},
        **{f"match_{k}": comparison["matches"][k] for k in comparison["matches"]}
    }])
    df.to_excel(excel_path, index=False)

    # Sauvegarde en base
    res = ComparisonResult(
        upload_id=upload_id,
        data=comparison,
        excel_path=excel_path
    )
    up.processed = True
    db.session.add(res)

    return res
