#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pentru atasare XML existent la PDF
=========================================
Cauta automat fisierele XML si PDF din folder si le combina.

Rulare: python ataseaza_xml.py
"""

import os
import sys

# Verifica dependentele
try:
    from pypdf import PdfReader, PdfWriter
    from lxml import etree
except ImportError:
    print("Lipsesc dependentele. Ruleaza:")
    print("   pip install pypdf lxml")
    sys.exit(1)

from pdf_xml_attachment import PDFXMLManager, XMLValidator, generate_validation_report

def gaseste_fisiere():
    """Gaseste fisierele XML si PDF din folderul curent"""
    fisiere_xml = [f for f in os.listdir('.') if f.lower().endswith('.xml')]
    fisiere_pdf = [f for f in os.listdir('.') if f.lower().endswith('.pdf')]
    return fisiere_xml, fisiere_pdf

def main():
    print("=" * 60)
    print("ATASARE XML LA PDF")
    print("=" * 60)
    
    # Gaseste fisierele
    fisiere_xml, fisiere_pdf = gaseste_fisiere()
    
    print("\nFisiere gasite in folder:")
    print("   XML: {}".format(fisiere_xml))
    print("   PDF: {}".format(fisiere_pdf))
    
    if not fisiere_xml:
        print("\nNu am gasit niciun fisier XML!")
        return
    
    if not fisiere_pdf:
        print("\nNu am gasit niciun fisier PDF!")
        return
    
    # Selecteaza fisierele (primul din fiecare)
    xml_file = fisiere_xml[0]
    pdf_file = fisiere_pdf[0]
    
    # Daca sunt mai multe, lasa utilizatorul sa aleaga
    if len(fisiere_xml) > 1:
        print("\nSelecteaza XML (1-{}):".format(len(fisiere_xml)))
        for i, f in enumerate(fisiere_xml, 1):
            print("   {}. {}".format(i, f))
        choice = input("Alegere [1]: ").strip() or "1"
        xml_file = fisiere_xml[int(choice) - 1]
    
    if len(fisiere_pdf) > 1:
        print("\nSelecteaza PDF (1-{}):".format(len(fisiere_pdf)))
        for i, f in enumerate(fisiere_pdf, 1):
            print("   {}. {}".format(i, f))
        choice = input("Alegere [1]: ").strip() or "1"
        pdf_file = fisiere_pdf[int(choice) - 1]
    
    print("\n[OK] XML selectat: {}".format(xml_file))
    print("[OK] PDF selectat: {}".format(pdf_file))
    
    # ========================================
    # 1. Valideaza XML-ul
    # ========================================
    print("\n" + "-" * 40)
    print("VALIDARE XML")
    print("-" * 40)
    
    validator = XMLValidator()  # Fara schema XSD
    result = validator.validate_file(xml_file)
    
    status = "DA" if result.is_valid else "NU"
    print("   Well-formed: {}".format(status))
    print("   Element radacina: {}".format(result.xml_root_element))
    print("   Namespace: {}".format(result.xml_namespace or '-'))
    
    if result.errors:
        print("\n   ERORI:")
        for err in result.errors:
            print("      {}".format(err))
        print("\n   XML-ul are erori! Continuam oricum? (d/n)")
        if input().lower() != 'd':
            return
    
    # ========================================
    # 2. Analizeaza PDF-ul
    # ========================================
    print("\n" + "-" * 40)
    print("ANALIZA PDF")
    print("-" * 40)
    
    manager = PDFXMLManager(pdf_file)
    print("   Pagini: {}".format(len(manager.reader.pages)))
    
    attachments = manager.list_attachments()
    print("   Atasamente existente: {}".format(len(attachments)))
    for att in attachments:
        print("     - {} ({} bytes)".format(att.name, att.size))
    
    # ========================================
    # 3. Ataseaza XML la PDF
    # ========================================
    print("\n" + "-" * 40)
    print("ATASARE XML")
    print("-" * 40)
    
    # Numele fisierului output
    base_name = os.path.splitext(pdf_file)[0]
    output_pdf = "{}_cu_XML.pdf".format(base_name)
    
    # Numele atasamentului (acelasi ca fisierul XML)
    attachment_name = xml_file
    
    result_path = manager.attach_xml(
        xml_path=xml_file,
        output_pdf_path=output_pdf,
        attachment_name=attachment_name
    )
    
    print("   [OK] PDF generat: {}".format(result_path))
    
    # Verifica
    manager_new = PDFXMLManager(result_path)
    new_attachments = manager_new.list_attachments()
    print("\n   Atasamente in noul PDF:")
    for att in new_attachments:
        print("     - {}".format(att.name))
    
    # ========================================
    # 4. Genereaza raport
    # ========================================
    report_path = "{}_raport.html".format(base_name)
    generate_validation_report([result], report_path, format="html")
    print("\n   [OK] Raport HTML: {}".format(report_path))
    
    # ========================================
    # Sumar
    # ========================================
    print("\n" + "=" * 60)
    print("COMPLETAT!")
    print("=" * 60)
    print("\nFisier generat: {}".format(output_pdf))
    print("Raport:         {}".format(report_path))
    print("\nDeschide PDF-ul in Adobe Acrobat pentru a vedea atasamentul.")

if __name__ == "__main__":
    main()