# -*- coding: utf-8 -*-
"""
D212 WebForm PDF Generator Service
Generates D212 PDF in the new AcroForm format (D212_WF1.0) with embedded XML attachment.
This is the newer format that ANAF uses instead of the old XFA-based D212.
"""

from xml.etree import ElementTree as ET
from pypdf import PdfReader, PdfWriter
from pypdf.generic import (
    NameObject, ArrayObject, DictionaryObject,
    DecodedStreamObject, NumberObject, create_string_object
)
import io


class D212WFGenerator:
    """Generates D212 PDF in WebForm format with embedded XML"""

    def __init__(self, xml_content: bytes):
        self.xml_content = xml_content
        self.root = ET.fromstring(xml_content)
        # Detect namespace
        self.default_ns = ''
        if self.root.tag.startswith('{'):
            self.default_ns = self.root.tag[1:self.root.tag.index('}')]

    def get_attr(self, attr, default=''):
        return self.root.get(attr, default) or default

    def generate_pdf(self, template_path: str) -> bytes:
        """Generate filled PDF with embedded XML attachment"""

        # Extract values from XML for form fields
        an_r = self.get_attr('an_r', '')
        luna_r = self.get_attr('luna_r', '')
        d_rec = self.get_attr('d_rec', '0')
        cif = self.get_attr('cif', '')
        totalPlata_A = self.get_attr('totalPlata_A', '0')

        # Read template and clone entire document
        reader = PdfReader(template_path)
        writer = PdfWriter()
        writer.clone_reader_document_root(reader)

        # Fill form fields
        writer.update_page_form_field_values(
            writer.pages[0],
            {
                'luna_r': luna_r,
                'cif': cif,
                'totalPlata_A': totalPlata_A,
                'd_rec': d_rec,
                'an_r': an_r,
                'universalCode': 'D212_WF1.0'
            }
        )

        # Add XML as embedded file attachment
        self._add_xml_attachment(writer, self.xml_content, 'd212.xml')

        # Write to bytes
        output = io.BytesIO()
        writer.write(output)
        return output.getvalue()

    def _add_xml_attachment(self, writer: PdfWriter, xml_data: bytes, filename: str):
        """Add XML as embedded file attachment to PDF"""

        # Create the embedded file stream
        file_stream = DecodedStreamObject()
        file_stream.set_data(xml_data)
        file_stream[NameObject('/Type')] = NameObject('/EmbeddedFile')
        file_stream[NameObject('/Subtype')] = NameObject('/application/xml')
        file_stream[NameObject('/Params')] = DictionaryObject({
            NameObject('/Size'): NumberObject(len(xml_data))
        })
        file_stream_ref = writer._add_object(file_stream)

        # Create filespec
        filespec = DictionaryObject({
            NameObject('/Type'): NameObject('/Filespec'),
            NameObject('/F'): create_string_object(filename),
            NameObject('/Desc'): create_string_object(filename),
            NameObject('/EF'): DictionaryObject({
                NameObject('/F'): file_stream_ref
            })
        })
        filespec_ref = writer._add_object(filespec)

        # Create embedded files entry
        embedded_files = DictionaryObject({
            NameObject('/Names'): ArrayObject([
                create_string_object(filename),
                filespec_ref
            ])
        })
        embedded_files_ref = writer._add_object(embedded_files)

        # Create or update Names dictionary in catalog
        if '/Names' not in writer._root_object:
            writer._root_object[NameObject('/Names')] = DictionaryObject()

        names_dict = writer._root_object['/Names']
        if hasattr(names_dict, 'get_object'):
            names_dict = names_dict.get_object()

        names_dict[NameObject('/EmbeddedFiles')] = embedded_files_ref


def generate_d212_wf_pdf(xml_content: bytes, pdf_template_path: str) -> bytes:
    """Generate D212 WebForm PDF from XML content.

    Args:
        xml_content: The D212 XML content as bytes
        pdf_template_path: Path to the D212 WebForm PDF template

    Returns:
        The generated PDF as bytes
    """
    generator = D212WFGenerator(xml_content)
    return generator.generate_pdf(pdf_template_path)
