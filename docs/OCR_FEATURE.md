# GreenMotion Cars - OCR Annonce Upload Feature

## Funktionalitet

Systemet kan nu automatisk ekstrahere biloplysninger fra annonce-billeder fra mobile.de, Blocket og andre salgssider.

### Sådan bruger du det:

1. Gå til "Tilføj Bil" siden
2. Upload et skærmbillede af annoncen (PNG, JPG, etc.)
3. Klik på "Ekstraher Data fra Annonce"
4. Systemet udfylder automatisk felterne med:
   - VIN-nummer
   - Mærke & Model
   - Årgang
   - Kilometerstand
   - Brændstoftype
   - Gearkasse type
   - Pris

### OCR Teknologi

- **Tesseract OCR** - Open source tekstgenkendelse
- **Understøtter sprog**: Engelsk, Dansk, Tysk, Svensk
- **Billedformater**: PNG, JPG, JPEG, GIF, BMP, WebP

### Installation

OCR biblioteker er installeret:
```bash
pip install Pillow pytesseract
brew install tesseract tesseract-lang
```

### Systemkrav

- macOS/Linux: Tesseract skal være installeret via Homebrew/apt
- Windows: Download Tesseract installer fra GitHub

### API Endpoint

`POST /cars/parse-ad`
- Accepterer: multipart/form-data med 'ad_image' fil
- Returnerer: JSON med ekstraherede felter
