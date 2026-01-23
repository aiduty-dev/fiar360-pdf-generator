# -*- coding: utf-8 -*-
"""
D212 PDF Generator Service
Converteste XML ANAF D212 (Declaratie Unica) in format XFA si genereaza PDF completat.
"""

import io
from xml.etree import ElementTree as ET
from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject, NumberObject, BooleanObject, DecodedStreamObject


class D212ToXFAConverter:
    """Converteste XML ANAF D212 in format XFA"""

    def __init__(self, xml_content: bytes):
        self.root = ET.fromstring(xml_content)
        self.ns = {'anaf': 'mfp:anaf:dgti:d212:declaratie:v11'}

    def get_attr(self, attr, default=''):
        return self.root.get(attr, default) or default

    def xml_tag(self, name, value):
        if value is None or value == '':
            return f'<{name}/>'
        return f'<{name}>{value}</{name}>'

    def generate_xfa_datasets(self):
        """Genereaza XML-ul XFA datasets complet"""

        # Date din root
        an_r = self.get_attr('an_r', '')
        luna_r = self.get_attr('luna_r', '')
        d_rec = self.get_attr('d_rec', '0')
        rectif1 = self.get_attr('rectif1', '0')
        rectif2 = self.get_attr('rectif2', '0')

        cif = self.get_attr('cif', '')
        nume_c = self.get_attr('nume_c', '')
        adresa_c = self.get_attr('adresa_c', '')
        telefon_c = self.get_attr('telefon_c', '')
        email_c = self.get_attr('email_c', '')
        fax_c = self.get_attr('fax_c', '')

        nerezident = self.get_attr('nerezident', '0')
        cont_bancar = self.get_attr('cont_bancar', '')

        totalPlata_A = self.get_attr('totalPlata_A', '0')

        # Bife succesor/anulare
        bifa_succesor = self.get_attr('bifa_succesor', '0')
        cif_succesor = self.get_attr('cif_succesor', '')
        anulare_litA = self.get_attr('anulare_litA', '0')
        anulare_litB = self.get_attr('anulare_litB', '0')
        bifa_conformare = self.get_attr('bifa_conformare', '0')

        # Bife capitole
        bifa111 = self.get_attr('bifa111', '0')
        bifa112 = self.get_attr('bifa112', '0')
        bifa113 = self.get_attr('bifa113', '0')
        bifa121 = self.get_attr('bifa121', '0')
        bifa122 = self.get_attr('bifa122', '0')
        bifa131 = self.get_attr('bifa131', '0')
        bifa132 = self.get_attr('bifa132', '0')
        bifa14 = self.get_attr('bifa14', '0')
        bifa15 = self.get_attr('bifa15', '0')
        bifa18 = self.get_attr('bifa18', '0')

        # Parse nume_c - poate fi in format "NUME, INITIALA, PRENUME" sau "PRENUME NUME"
        nume = ''
        init = ''
        pren = ''
        if nume_c:
            parts = [p.strip() for p in nume_c.split(',') if p.strip()]
            if len(parts) >= 3:
                nume = parts[0]
                init = parts[1]
                pren = parts[2]
            elif len(parts) == 2:
                nume = parts[0]
                pren = parts[1]
            elif len(parts) == 1:
                # Poate fi "PRENUME NUME"
                space_parts = parts[0].split()
                if len(space_parts) >= 2:
                    pren = space_parts[0]
                    nume = ' '.join(space_parts[1:])
                else:
                    nume = parts[0]

        # Construieste XFA (fara XML declaration - este stream embedded)
        xfa = []
        xfa.append('<xfa:datasets xmlns:xfa="http://www.xfa.org/schema/xfa-data/1.0/">')
        xfa.append('<xfa:data>')
        xfa.append('<form1>')

        # IdDoc - Document identification
        xfa.append('<IdDoc>')
        xfa.append(self.xml_tag('an_r', an_r))
        xfa.append(self.xml_tag('luna_r', luna_r))
        xfa.append(self.xml_tag('d_rec', d_rec))
        xfa.append(self.xml_tag('totalPlata_A', totalPlata_A))
        xfa.append(self.xml_tag('universalCode', 'D212_A1.0.6'))
        xfa.append(self.xml_tag('formValid', ''))
        xfa.append(self.xml_tag('signDgt', ''))
        xfa.append('</IdDoc>')

        # idCnt - Contributor info
        xfa.append('<idCnt>')
        xfa.append(self.xml_tag('nume', nume))
        xfa.append(self.xml_tag('init', init))
        xfa.append(self.xml_tag('pren', pren))
        xfa.append(self.xml_tag('cif', cif))
        xfa.append(self.xml_tag('adresa', adresa_c))
        xfa.append(self.xml_tag('telefon', telefon_c))
        xfa.append(self.xml_tag('fax', fax_c))
        xfa.append(self.xml_tag('email', email_c))
        xfa.append(self.xml_tag('nrzC', nerezident))
        xfa.append(self.xml_tag('iban', cont_bancar))
        xfa.append('<infN xfa:dataNode="dataGroup"/>')
        xfa.append('</idCnt>')

        # bifaI - Representative checkbox
        xfa.append('<bifaI>')
        xfa.append(self.xml_tag('rprI', '0'))
        xfa.append('</bifaI>')

        # infI - Representative info (empty)
        xfa.append('<infI>')
        xfa.append(self.xml_tag('numeI', ''))
        xfa.append(self.xml_tag('cifI', ''))
        xfa.append('<adrI xfa:dataNode="dataGroup"/>')
        xfa.append(self.xml_tag('telefon', ''))
        xfa.append(self.xml_tag('fax', ''))
        xfa.append(self.xml_tag('email', ''))
        xfa.append('</infI>')

        # bife - Checkboxes structure
        xfa.append('<bife>')

        # Cap1
        xfa.append('<Cap1>')

        # bifaR1
        xfa.append('<bifaR1>')
        xfa.append(self.xml_tag('d_rec1', rectif1))
        xfa.append(self.xml_tag('d_conformare1', bifa_conformare))
        xfa.append('</bifaR1>')

        # succesor
        xfa.append('<succesor>')
        xfa.append(self.xml_tag('art90_4', bifa_succesor))
        xfa.append(self.xml_tag('cif_succesor', cif_succesor))
        xfa.append('</succesor>')

        # anulare
        xfa.append('<anulare>')
        xfa.append(self.xml_tag('litA', anulare_litA))
        xfa.append(self.xml_tag('litB', anulare_litB))
        xfa.append('</anulare>')

        # G1 - Section I.1
        xfa.append('<G1>')
        xfa.append('<G11>')
        xfa.append(self.xml_tag('I11', bifa111))
        xfa.append('</G11>')
        xfa.append('<G12>')
        xfa.append(self.xml_tag('I12', bifa112))
        xfa.append('</G12>')
        xfa.append('<G13>')
        xfa.append(self.xml_tag('I13', bifa113))
        xfa.append('</G13>')
        xfa.append('</G1>')

        # G2 - Section I.2
        xfa.append('<G2>')
        xfa.append('<G21>')
        xfa.append(self.xml_tag('I21', bifa121))
        xfa.append('</G21>')
        xfa.append('<G22>')
        xfa.append(self.xml_tag('I22', bifa122))
        xfa.append('</G22>')
        xfa.append('</G2>')

        # G3 - Section I.3
        xfa.append('<G3>')
        xfa.append('<G31>')
        xfa.append(self.xml_tag('I31', bifa131))
        xfa.append('</G31>')
        xfa.append('<G32>')
        xfa.append(self.xml_tag('I32', bifa132))
        xfa.append('</G32>')
        xfa.append('</G3>')

        # G4 - Section I.4
        xfa.append('<G4>')
        xfa.append(self.xml_tag('I4', bifa14))
        xfa.append('</G4>')

        # G4_1 - Section I.5
        xfa.append('<G4_1>')
        xfa.append(self.xml_tag('I4_1', bifa15))
        xfa.append('</G4_1>')

        # G9 - Bonificatii
        xfa.append('<G9>')
        xfa.append(self.xml_tag('I9', bifa18))
        xfa.append('</G9>')

        xfa.append('</Cap1>')

        # Cap2
        xfa.append('<Cap2>')
        xfa.append(self.xml_tag('d_rec2', rectif2))
        xfa.append(self.xml_tag('bifaOpt', '0'))
        xfa.append('</Cap2>')

        xfa.append('</bife>')

        xfa.append('</form1>')
        xfa.append('</xfa:data>')
        xfa.append('</xfa:datasets>')

        return ''.join(xfa)


def generate_d212_pdf(xml_content: bytes, pdf_template_path: str, attach_xml: bool = True) -> bytes:
    """Genereaza PDF D212 completat din continutul XML.
    Foloseste append pentru a pastra structura XFA originala.
    """
    converter = D212ToXFAConverter(xml_content)
    xfa_datasets = converter.generate_xfa_datasets()

    # Citim template-ul original
    with open(pdf_template_path, 'rb') as f:
        pdf_bytes = f.read()

    # Folosim append pentru a pastra mai bine structura XFA
    reader = PdfReader(io.BytesIO(pdf_bytes))
    writer = PdfWriter()

    # Append pastreaza mai bine referintele interne decat clone
    writer.append(reader)

    if '/AcroForm' in writer._root_object:
        acroform = writer._root_object['/AcroForm']
        if hasattr(acroform, 'get_object'):
            acroform = acroform.get_object()

        if '/XFA' in acroform:
            xfa_array = acroform['/XFA']
            if hasattr(xfa_array, 'get_object'):
                xfa_array = xfa_array.get_object()

            for i in range(0, len(xfa_array), 2):
                name = str(xfa_array[i])
                if name == 'datasets':
                    stream_ref = xfa_array[i + 1]
                    if hasattr(stream_ref, 'get_object'):
                        stream_obj = stream_ref.get_object()
                    else:
                        stream_obj = stream_ref

                    # Decode the stream first (required for EncodedStreamObject)
                    _ = stream_obj.get_data()

                    # Now update with our XFA data
                    encoded_data = xfa_datasets.encode('utf-8')
                    stream_obj.set_data(encoded_data)
                    break

    if attach_xml:
        root = ET.fromstring(xml_content)
        luna = root.get('luna_r', '00')
        an = root.get('an_r', '0000')
        attachment_name = f"D212_{an}_{luna}.xml"
        writer.add_attachment(attachment_name, xml_content)

    output_buffer = io.BytesIO()
    writer.write(output_buffer)
    output_buffer.seek(0)

    return output_buffer.getvalue()
