# -*- coding: utf-8 -*-
"""
D212 PDF Generator Service
Foloseste API-ul ANAF pentru generare PDF.
Schema: mfp:anaf:dgti:d212:declaratie:v11
"""

import httpx

ANAF_PDF_API = "https://www.anaf.ro/declaratii/duf/api/proxy-pdf"

ANAF_HEADERS = {
    'Content-Type': 'application/xml',
    'Accept': '*/*',
    'Origin': 'https://www.anaf.ro',
    'Referer': 'https://www.anaf.ro/declaratii/duf/rezultate-validare',
    'User-Agent': 'Mozilla/5.0 (compatible; fiar360-pdf-generator/1.0)'
}


def generate_d212_pdf(xml_content: bytes, pdf_template_path: str = None, attach_xml: bool = True) -> bytes:
    """
    Genereaza PDF D212 folosind API-ul ANAF.

    Args:
        xml_content: Continutul XML ANAF in bytes
        pdf_template_path: Ignorat (pastrat pentru compatibilitate)
        attach_xml: Ignorat (ANAF include XML-ul automat)

    Returns:
        bytes: Continutul PDF generat
    """
    # Decodifica XML
    xml_str = xml_content.decode('utf-8')

    # Adauga header XML daca lipseste
    if not xml_str.strip().startswith('<?xml'):
        xml_str = '<?xml version="1.0"?>\n' + xml_str

    # Call ANAF API
    with httpx.Client(timeout=60.0) as client:
        response = client.post(
            ANAF_PDF_API,
            content=xml_str.encode('utf-8'),
            headers=ANAF_HEADERS
        )
        response.raise_for_status()
        return response.content
