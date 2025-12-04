# 🧾 Faktura System - Brugervejledning

## Oversigt

GreenMotion Cars CRM har nu et komplet fakturasystem hvor du kan:
- ✅ Oprette fakturaer manuelt eller knyttet til kunder/salg
- ✅ Redigere fakturaer (kladder og sendte)
- ✅ Slette fakturaer (kun ikke-betalte)
- ✅ Printe professionelle fakturaer
- ✅ Spore status (kladde, sendt, betalt, forfald)
- ✅ Tilføje flere fakturaposter med rabatter
- ✅ Automatisk beregning af moms og totaler

---

## 📋 Sådan opretter du en faktura

### 1. Adgang til Fakturaer
- Klik på **"Fakturaer"** i venstre menu
- Eller gå direkte til: `/invoices`

### 2. Opret Ny Faktura
1. Klik på knappen **"Ny Faktura"**
2. Udfyld kundeoplysninger:
   - **Vælg eksisterende kunde** fra dropdown (auto-udfylder felter)
   - ELLER indtast kundeoplysninger manuelt
3. Angiv fakturaoplysninger:
   - **Fakturadato** (standard: i dag)
   - **Betalingsbetingelser** (standard: 14 dage)
   - **Momssats** (standard: 25%)
   - **Noter** (vises på faktura)
   - **Interne noter** (vises kun internt)

### 3. Tilføj Fakturaposter
- Start med én linje (kan tilføjes flere)
- For hver post:
  - **Beskrivelse** (f.eks. "Tesla Model 3 2022")
  - **Antal** (standard: 1)
  - **Enhedspris** (i kr.)
  - **Rabat %** (valgfrit)
- Klik **"Tilføj post"** for flere linjer
- Total beregnes automatisk

### 4. Gem Faktura
- Klik **"Gem Faktura"**
- Faktura oprettes med status: **Kladde**
- Unikt fakturanummer genereres automatisk (format: INV-2025-0001)

---

## ✏️ Rediger Faktura

### Hvornår kan du redigere?
- ✅ Kladder (draft)
- ✅ Sendte fakturaer (sent)
- ❌ Betalte fakturaer (kan IKKE redigeres)

### Sådan redigerer du:
1. Gå til faktura-oversigten
2. Klik på **blyant-ikonet** ved fakturaen
3. Foretag ændringer
4. Klik **"Gem Ændringer"**

---

## 🗑️ Slet Faktura

### Hvornår kan du slette?
- ✅ Kladder
- ✅ Sendte fakturaer
- ✅ Annullerede fakturaer
- ❌ Betalte fakturaer (kan IKKE slettes)

### Sådan sletter du:
1. Åbn fakturaen
2. I højre sidebar, klik **"Slet faktura"**
3. Bekræft sletning
4. ⚠️ **ADVARSEL**: Dette kan ikke fortrydes!

---

## 📊 Faktura Status

| Status | Beskrivelse | Handlinger |
|--------|-------------|------------|
| **Kladde** (draft) | Ny faktura under udarbejdelse | Rediger, Send, Slet |
| **Sendt** (sent) | Faktura sendt til kunde | Marker som betalt, Annuller, Slet |
| **Betalt** (paid) | Betaling modtaget | Kun visning (ingen ændringer) |
| **Forfald** (overdue) | Forfaldsdato overskredet | Marker som betalt, Send påmindelse |
| **Annulleret** (cancelled) | Faktura annulleret | Kun visning, Slet |

---

## 🔄 Opdater Status

### Marker som Sendt
1. Åbn fakturaen
2. Klik **"Marker som sendt"**
3. Status ændres til **Sendt**
4. Afsendelsesdato registreres

### Marker som Betalt
1. Åbn fakturaen
2. Klik **"Marker som betalt"**
3. Status ændres til **Betalt**
4. Betalingsdato registreres automatisk

### Annuller Faktura
1. Åbn fakturaen
2. Klik **"Annuller faktura"**
3. Bekræft annullering
4. Status ændres til **Annulleret**

---

## 🖨️ Print Faktura

### Professionel Faktura-layout
- Klik på **printer-ikonet** ved fakturaen
- ELLER åbn faktura og klik **"Print"**
- Åbner print-venlig visning i nyt vindue
- Indeholder:
  - GreenMotion Cars firmalogo og info
  - Kundeoplysninger
  - Fakturaposter med beregninger
  - Betalingsinformation
  - Noter

### Print fra browser
1. Print-vindue åbnes
2. Klik **"Print Faktura"** knappen
3. Eller brug `Ctrl/Cmd + P`
4. Vælg printer eller "Gem som PDF"

---

## 📈 Statistik Dashboard

På faktura-oversigten ser du:
- **Total**: Alle fakturaer
- **Kladder**: Uafsendte fakturaer
- **Sendt**: Fakturaer afventer betaling
- **Betalt**: Gennemførte fakturaer

---

## 🔍 Søgning og Filtrering

### Søg fakturaer
- Søg efter **fakturanummer** (f.eks. "INV-2025-0001")
- Søg efter **kundenavn**

### Filtrer efter status
- Alle status
- Kladde
- Sendt
- Betalt
- Forfald
- Annulleret

---

## 💡 Tips og Tricks

### Auto-udfyld kundeoplysninger
Når du vælger en eksisterende kunde fra dropdown:
- Navn, adresse, email, telefon udfyldes automatisk
- CVR-nummer kopieres hvis forhandler
- Betalingsbetingelser hentes fra kunde

### Automatisk beregning
- **Subtotal** beregnes fra alle fakturaposter
- **Moms** beregnes baseret på momssats
- **Total** opdateres automatisk ved ændringer
- **Rabat** trækkes fra før moms beregnes

### Forfaldsdato
- Beregnes automatisk fra fakturadato + betalingsbetingelser
- Eksempel: Fakturadato 01-12-2025 + 14 dage = Forfald 15-12-2025

### Fakturanummer
- Genereres automatisk i format: **INV-ÅR-NUMMER**
- Eksempel: INV-2025-0001, INV-2025-0002, etc.
- Fortløbende nummerering per år

---

## ⚠️ Vigtige Begrænsninger

### Kan IKKE redigeres:
- Betalte fakturaer (status: paid)
- Begrundelse: Sikrer revisorspor

### Kan IKKE slettes:
- Betalte fakturaer (status: paid)
- Begrundelse: Økonomisk dokumentation

### Annullerede fakturaer:
- Kan slettes hvis nødvendigt
- Vises stadig i oversigten
- Kan ikke ændres til andre statuser

---

## 🔐 Sikkerhed

- ✅ Login påkrævet for alle faktura-funktioner
- ✅ Alle handlinger logges
- ✅ Betalte fakturaer er beskyttet mod ændringer
- ✅ Sletning kræver bekræftelse

---

## 📞 Firmaoplysninger på Faktura

Standard oplysninger (kan tilpasses i print.html):
```
GreenMotion Cars
Nørresundby, Danmark
CVR: 12345678
Email: info@greenmotioncars.dk
Telefon: +45 98 12 34 56
```

**Bankoplysninger:**
```
Bank: Danske Bank
Reg. nr.: 1234 | Konto nr.: 567890
IBAN: DK1234567890 | SWIFT: DABADKKK
```

---

## 🎯 Workflows

### Workflow 1: Simpel Faktura
1. Opret faktura → Indtast kunde → Tilføj poster → Gem
2. Marker som sendt
3. Når betaling modtages → Marker som betalt

### Workflow 2: Faktura Knyttet til Salg
1. Gå til salg → Opret faktura fra salg (fremtidig funktion)
2. Kundeoplysninger auto-udfyldt
3. Marker som sendt
4. Spor betaling

### Workflow 3: Forhandler Faktura
1. Vælg forhandler fra dropdown
2. Betalingsbetingelser sættes automatisk (f.eks. 30 dage)
3. CVR-nummer inkluderet
4. Send faktura
5. Spor forfald

---

## 📱 Navigation

**Menu placering**: Venstre sidebar → **Fakturaer** (mellem Pipeline og Logistik)

**URLs**:
- Liste: `/invoices`
- Opret: `/invoices/create`
- Detaljer: `/invoices/<id>`
- Rediger: `/invoices/<id>/edit`
- Print: `/invoices/<id>/print`

---

## ✅ Funktioner Implementeret

- ✅ Opret faktura (manuel eller kunde-knyttet)
- ✅ Rediger faktura (beskytter betalte)
- ✅ Slet faktura (beskytter betalte)
- ✅ Vis faktura-detaljer
- ✅ Print professionel faktura
- ✅ Status management (kladde → sendt → betalt)
- ✅ Automatisk beregninger (subtotal, moms, total)
- ✅ Flere fakturaposter med rabat
- ✅ Forfaldsdato beregning
- ✅ Automatisk fakturanummer-generering
- ✅ Søgning og filtrering
- ✅ Statistik dashboard
- ✅ Database migration
- ✅ Menu integration

---

## 🚀 Næste Trin (Fremtidige Forbedringer)

1. **Email integration**
   - Send faktura direkte fra systemet
   - Automatiske betalingspåmindelser

2. **PDF generering**
   - Download faktura som PDF
   - Gem PDF'er i dokumenter

3. **Salgs-integration**
   - Opret faktura direkte fra salg
   - Link flere fakturaer til samme salg

4. **Betaling tracking**
   - Delbetalinger
   - Betalingshistorik

5. **Rapporter**
   - Omsætningsrapporter
   - Momsrapporter
   - Forfaldne fakturaer

---

**Oprettet**: 4. december 2025  
**Version**: 1.0  
**Status**: ✅ Fuldt funktionelt
