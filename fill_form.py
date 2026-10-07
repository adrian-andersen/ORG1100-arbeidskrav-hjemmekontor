#!/usr/bin/env python3
"""
fill_form.py - Fyller ut KI_deklarasjonsskjema.pdf digitalt og lagrer som KI_deklarasjonsskjema_utfylt.pdf.
Støtter både interaktive AcroForm-skjemaer og flat PDF via PyMuPDF.
"""

import os
import sys
import pymupdf

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

INPUT_PDF = "KI_deklarasjonsskjema.pdf"
OUTPUT_PDF = "KI_deklarasjonsskjema_utfylt.pdf"
FONT_PATH = "C:/Windows/Fonts/calibri.ttf"
FONT_NAME = "calibri"


def draw_cross(page, rect, pad=1.8, width=1.2, color=(0, 0, 0)):
    """Tegner et rent vektor-kryss [X] i en avkrysningsboks."""
    shape = page.new_shape()
    shape.draw_line(
        pymupdf.Point(rect.x0 + pad, rect.y0 + pad),
        pymupdf.Point(rect.x1 - pad, rect.y1 - pad),
    )
    shape.draw_line(
        pymupdf.Point(rect.x0 + pad, rect.y1 - pad),
        pymupdf.Point(rect.x1 - pad, rect.y0 + pad),
    )
    shape.finish(color=color, width=width)
    shape.commit()


def wrap_text(font, text, fontsize, max_width):
    """Bryter tekst til linjer basert på faktisk skriftbredde."""
    words = text.split()
    lines = []
    current_line = ""
    for word in words:
        test_line = (current_line + " " + word).strip()
        if font.text_length(test_line, fontsize=fontsize) <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    return lines


def fill_form():
    if not os.path.exists(INPUT_PDF):
        raise FileNotFoundError(f"Fant ikke kildefilen: {INPUT_PDF}")

    doc = pymupdf.open(INPUT_PDF)
    print(f"Åpnet {INPUT_PDF} ({len(doc)} sider).")

    # 1. Sjekk for interaktive skjemafelt (AcroForm)
    total_widgets = sum(len(list(p.widgets())) for p in doc)
    print(f"Fant {total_widgets} interaktive skjemafelt i dokumentet.")

    if total_widgets > 0:
        print("Fyller ut interaktive skjemafelt...")
    else:
        print("Ingen AcroForm-felter funnet. Tegner direkte på sidene via PyMuPDF...")

    has_custom_font = os.path.exists(FONT_PATH)
    font_obj = pymupdf.Font(fontfile=FONT_PATH) if has_custom_font else None

    # Hjelpefunksjon for å sette inn tekst
    def insert_text(page, point, text, fontsize=9.3, color=(0, 0, 0)):
        if has_custom_font:
            page.insert_text(
                point,
                text,
                fontsize=fontsize,
                fontname=FONT_NAME,
                fontfile=FONT_PATH,
                color=color,
            )
        else:
            page.insert_text(
                point,
                text,
                fontsize=fontsize,
                fontname="helv",
                color=color,
            )

    # =========================================================================
    # SIDE 1
    # =========================================================================
    p1 = doc[0]

    # --- Navn på studentene i to kolonner ---
    names_col1 = [
        "Adrian Andersen",
        "Anders Taraldsen",
        "Ellen Rebekka Strøm",
    ]
    names_col2 = [
        "Marte Wenneck Rasmussen",
        "August Evjen Sæther",
        "Andreas Dullum",
    ]

    y_start_names = 104.0
    line_spacing_names = 15.0

    for i, name in enumerate(names_col1):
        insert_text(p1, pymupdf.Point(246.0, y_start_names + i * line_spacing_names), name, fontsize=9.3)

    for i, name in enumerate(names_col2):
        insert_text(p1, pymupdf.Point(380.0, y_start_names + i * line_spacing_names), name, fontsize=9.3)

    # --- Emnekode og -navn ---
    # Dekker over opprinnelig tekst "Org1100" med en hvit boks for et rent resultat
    p1.draw_rect(pymupdf.Rect(241.0, 153.5, 519.0, 167.5), fill=(1, 1, 1), color=None)
    insert_text(p1, pymupdf.Point(245.2, 164.0), "ORG1100 – Organisasjon og ledelse", fontsize=9.3)

    # --- Semester og årstall ---
    p1.draw_rect(pymupdf.Rect(241.0, 168.0, 519.0, 182.5), fill=(1, 1, 1), color=None)
    insert_text(p1, pymupdf.Point(245.2, 178.8), "Høst 2026", fontsize=9.3)

    # --- Sjekkboks: Har det blitt anvendt KI-baserte hjelpemidler? -> [X] Ja ---
    rect_ja = pymupdf.Rect(106.9, 215.6, 116.3, 225.0)
    draw_cross(p1, rect_ja)

    # --- Sjekkbokser DEL I - Tekst ---
    # [X] Stavekontroll
    rect_stavekontroll = pymupdf.Rect(106.9, 264.1, 116.3, 273.5)
    draw_cross(p1, rect_stavekontroll)

    # [X] Skriveassistanse
    rect_skriveassistanse = pymupdf.Rect(106.9, 287.8, 116.3, 297.1)
    draw_cross(p1, rect_skriveassistanse)

    # [X] Tekstgenerering
    rect_tekstgenerering = pymupdf.Rect(106.9, 311.4, 116.3, 320.7)
    draw_cross(p1, rect_tekstgenerering)

    # --- Fritekstfelt under Tekst ---
    fritekst = (
        "KI (Gemini/ChatGPT) er benyttet som sparringspartner for strukturering av disposisjon, "
        "drøfting av pensumteorier, korrekturlesing og teknisk oppsett i LaTeX. Verktøyet ble også brukt til å "
        "foreslå språklig oppstramming/innkorting av gruppens egne utkast (Del 2) og utkast til formuleringer i "
        "avslutningskapittelet. Alt råmateriale, faglige vurderinger og pensumforankring er gjennomført, bearbeidet og "
        "kvalitetssikret av studentene."
    )

    box_w = 517.4 - 106.7 - 8.0  # 402.7 pt
    fontsize_fritekst = 6.0
    text_lines = wrap_text(font_obj, fritekst, fontsize_fritekst, box_w) if font_obj else [fritekst]
    print(f"Fritekst delt inn i {len(text_lines)} linjer (fontstørrelse {fontsize_fritekst} pt).")

    # Plassering i boksen (y fra 350.2 til 373.2)
    y_baselines = [356.6, 363.3, 370.0]
    for i, line in enumerate(text_lines):
        baseline = y_baselines[i] if i < len(y_baselines) else (356.6 + i * 6.7)
        insert_text(p1, pymupdf.Point(109.5, baseline), line, fontsize=fontsize_fritekst)

    # =========================================================================
    # SIDE 2
    # =========================================================================
    if len(doc) > 1:
        p2 = doc[1]
        # [X] NTNUs regelverk (erklæring)
        rect_regelverk = pymupdf.Rect(93.6, 61.4, 102.9, 70.8)
        draw_cross(p2, rect_regelverk)

    # Lagre den utfylte filen
    doc.save(OUTPUT_PDF)
    doc.close()
    print(f"Fullført! Lagret utfylt skjema som {OUTPUT_PDF}.")


if __name__ == "__main__":
    fill_form()
