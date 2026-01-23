#!/usr/bin/env python3
"""
Script simplu de test - PDF XML Attachment
==========================================
Pune acest fișier în același folder cu pdf_xml_attachment.py și un PDF

Rulare: python test_simplu.py
"""

# Instalare dependențe (rulează o singură dată):
# pip install pypdf lxml

import os
import sys

# Verifică dependențele
try:
    from pypdf import PdfReader, PdfWriter
    from lxml import etree
except ImportError as e:
    print("❌ Lipsesc dependențele. Rulează:")
    print("   pip install pypdf lxml")
    sys.exit(1)

# Import din modulul principal
try:
    from pdf_xml_attachment import PDFXMLManager, XMLValidator, generate_validation_report
except ImportError:
    print("❌ Pune pdf_xml_attachment.py în același folder cu acest script!")
    sys.exit(1)

def main():
    print("=" * 60)
    print("TEST RAPID: PDF XML Attachment Tool")
    print("=" * 60)
    
    # Creează folder pentru output
    output_dir = "output_test"
    os.makedirs(output_dir, exist_ok=True)
    
    # ========================================
    # 1. Creează XML de test
    # ========================================
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<declaratie112 xmlns="mfp:anaf:dgti:d112:declaratie:v4">
    <antet>
        <lunaR>1</lunaR>
        <anR>2025</anR>
        <d_rec>0</d_rec>
    </antet>
    <platitor>
        <cif>12345678</cif>
        <denumire>SC TEST SRL</denumire>
    </platitor>
</declaratie112>"""
    
    xml_path = os.path.join(output_dir, "test_data.xml")
    with open(xml_path, 'w', encoding='utf-8') as f:
        f.write(xml_content)
    print(f"\n✓ XML creat: {xml_path}")
    
    # ========================================
    # 2. Caută un PDF în folder
    # ========================================
    pdf_files = [f for f in os.listdir('.') if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        print("\n⚠️  Nu am găsit niciun PDF în folder.")
        print("   Pune un fișier PDF în același folder și rulează din nou.")
        
        # Creează un PDF simplu de test
        print("\n   Creez un PDF simplu de test...")
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
        
        test_pdf = os.path.join(output_dir, "test_document.pdf")
        c = canvas.Canvas(test_pdf, pagesize=A4)
        c.drawString(100, 750, "Document de test pentru atasare XML")
        c.drawString(100, 730, "Generat automat")
        c.save()
        pdf_files = [test_pdf]
        print(f"   ✓ PDF creat: {test_pdf}")
    
    pdf_path = pdf_files[0]
    print(f"\n📄 PDF selectat: {pdf_path}")
    
    # ========================================
    # 3. Analizează PDF-ul
    # ========================================
    print("\n--- Analiză PDF ---")
    try:
        manager = PDFXMLManager(pdf_path)
        print(f"   Pagini: {len(manager.reader.pages)}")
        
        attachments = manager.list_attachments()
        print(f"   Atașamente existente: {len(attachments)}")
        for att in attachments:
            print(f"     • {att.name}")
    except Exception as e:
        print(f"   ❌ Eroare: {e}")
        return
    
    # ========================================
    # 4. Atașează XML la PDF
    # ========================================
    print("\n--- Atașare XML ---")
    output_pdf = os.path.join(output_dir, "document_cu_xml.pdf")
    
    try:
        result = manager.attach_xml(
            xml_path=xml_path,
            output_pdf_path=output_pdf,
            attachment_name="date_declaratie.xml"
        )
        print(f"   ✓ PDF cu XML: {result}")
        
        # Verifică
        manager_new = PDFXMLManager(result)
        new_attachments = manager_new.list_attachments()
        print(f"   Atașamente în noul PDF: {len(new_attachments)}")
        for att in new_attachments:
            print(f"     • {att.name}")
            
    except Exception as e:
        print(f"   ❌ Eroare: {e}")
    
    # ========================================
    # 5. Validare XML (fără schemă)
    # ========================================
    print("\n--- Validare XML ---")
    validator = XMLValidator()  # Fără schemă - doar well-formed check
    result = validator.validate_file(xml_path)
    
    print(f"   Status: {result.status.value}")
    print(f"   Well-formed: {'DA ✓' if result.is_valid else 'NU ✗'}")
    print(f"   Element rădăcină: {result.xml_root_element}")
    
    # ========================================
    # 6. Generează raport HTML
    # ========================================
    report_path = os.path.join(output_dir, "raport.html")
    generate_validation_report([result], report_path, format="html")
    print(f"\n✓ Raport HTML: {report_path}")
    
    # ========================================
    # Sumar
    # ========================================
    print("\n" + "=" * 60)
    print("FIȘIERE GENERATE:")
    print("=" * 60)
    for f in os.listdir(output_dir):
        fpath = os.path.join(output_dir, f)
        size = os.path.getsize(fpath)
        print(f"  {f:35} {size:>10,} bytes")
    
    print("\n✅ Test completat!")
    print(f"\nDeschide {report_path} în browser pentru raport.")


if __name__ == "__main__":
    main()
