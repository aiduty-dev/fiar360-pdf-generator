# -*- coding: utf-8 -*-
"""
D390 PDF Generator Service
Converteste XML ANAF D390 in format XFA si genereaza PDF completat.
"""

import io
from xml.etree import ElementTree as ET
from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject, NumberObject


class D390ToXFAConverter:
    """Converteste XML ANAF D390 in format XFA"""

    def __init__(self, xml_content: bytes):
        self.root = ET.fromstring(xml_content)
        self.ns = {'anaf': 'mfp:anaf:dgti:d390:declaratie:v3'}

    def get_attr(self, attr, default=''):
        return self.root.get(attr, default) or default

    def find_element(self, tag):
        for child in self.root:
            local_name = child.tag.split('}')[-1] if '}' in child.tag else child.tag
            if local_name == tag:
                return child
        return None

    def find_all_elements(self, tag):
        results = []
        for child in self.root:
            local_name = child.tag.split('}')[-1] if '}' in child.tag else child.tag
            if local_name == tag:
                results.append(child)
        return results

    def xml_tag(self, name, value):
        if value is None or value == '':
            return f'<{name}\n/>'
        return f'<{name}\n>{value}</{name}\n>'

    def generate_xfa_datasets(self):
        """Genereaza XML-ul XFA datasets complet"""

        # Date din root
        luna = self.get_attr('luna', '')
        an = self.get_attr('an', '')
        d_rec = self.get_attr('d_rec', '0')
        nume_declar = self.get_attr('nume_declar', '')
        prenume_declar = self.get_attr('prenume_declar', '')
        functie_declar = self.get_attr('functie_declar', '')
        cui = self.get_attr('cui', '')
        den = self.get_attr('den', '')
        adresa = self.get_attr('adresa', '')
        telefon = self.get_attr('telefon', '')
        mail = self.get_attr('mail', '')
        totalPlata_A = self.get_attr('totalPlata_A', '0')

        # Rezumat
        rezumat = self.find_element('rezumat')
        nr_pag = '1'
        nrOPI = '0'
        bazaL = '0'
        bazaT = '0'
        bazaA = '0'
        bazaP = '0'
        bazaS = '0'
        bazaR = '0'
        total_baza = '0'

        if rezumat is not None:
            nr_pag = rezumat.get('nr_pag', '1')
            nrOPI = rezumat.get('nrOPI', '0')
            bazaL = rezumat.get('bazaL', '0')
            bazaT = rezumat.get('bazaT', '0')
            bazaA = rezumat.get('bazaA', '0')
            bazaP = rezumat.get('bazaP', '0')
            bazaS = rezumat.get('bazaS', '0')
            bazaR = rezumat.get('bazaR', '0')
            total_baza = rezumat.get('total_baza', '0')

        # Operatii
        operatii = self.find_all_elements('operatie')

        # Construieste XFA
        xfa = []
        xfa.append('\n<xfa:datasets xmlns:xfa="http://www.xfa.org/schema/xfa-data/1.0/"\n>')
        xfa.append('<xfa:data\n>')
        xfa.append('<form1\n>')

        # Cod formular
        xfa.append('<codF1\n>')
        xfa.append(self.xml_tag('universalCode', 'D390_A1.0.11'))
        xfa.append('</codF1\n>')

        # Body1 - Date identificare
        xfa.append('<body1\n>')
        xfa.append('<HEADER xfa:dataNode="dataGroup"\n/>')

        xfa.append('<dd1\n>')
        xfa.append(self.xml_tag('d_rec', d_rec))
        xfa.append('</dd1\n>')

        xfa.append('<dd2\n>')
        xfa.append(self.xml_tag('luna_r', luna))
        xfa.append(self.xml_tag('an_r', an))
        xfa.append('</dd2\n>')

        xfa.append('<dd3\n>')
        xfa.append(self.xml_tag('cif', cui))
        xfa.append(self.xml_tag('denumire', den))
        xfa.append(self.xml_tag('adresa', adresa))
        xfa.append(self.xml_tag('telefon', telefon))
        xfa.append(self.xml_tag('fax', ''))
        xfa.append(self.xml_tag('eMail', mail))
        xfa.append('</dd3\n>')

        xfa.append('<dd4\n>')
        xfa.append(self.xml_tag('totalPlata_A', totalPlata_A))
        xfa.append(self.xml_tag('TOTAL_PAGINI', nr_pag))
        xfa.append(self.xml_tag('TOTAL_OPERATORI', nrOPI))
        xfa.append(self.xml_tag('SUMA_L', bazaL))
        xfa.append(self.xml_tag('SUMA_T', bazaT))
        xfa.append(self.xml_tag('SUMA_A', bazaA))
        xfa.append(self.xml_tag('SUMA_P', bazaP))
        xfa.append(self.xml_tag('SUMA_S', bazaS))
        xfa.append(self.xml_tag('SUMA_R', bazaR))
        xfa.append('</dd4\n>')

        xfa.append('<dd5\n>')
        xfa.append(self.xml_tag('numeP', nume_declar))
        xfa.append(self.xml_tag('prenP', prenume_declar))
        xfa.append(self.xml_tag('functiaP', functie_declar))
        xfa.append('</dd5\n>')

        xfa.append('<dd6\n>')
        xfa.append(self.xml_tag('numeFisier', ''))
        xfa.append('</dd6\n>')

        xfa.append('</body1\n>')

        # Body3 - Prima operatie (pentru validare)
        xfa.append('<body3\n>')
        xfa.append('<dd1 xfa:dataNode="dataGroup"\n/>')
        xfa.append('<dd2\n>')
        xfa.append(self.xml_tag('seq', '1.00000000'))
        if operatii:
            xfa.append(self.xml_tag('TARA1', operatii[0].get('tara', '')))
            xfa.append(self.xml_tag('COD_OP1', operatii[0].get('codO', '')))
        else:
            xfa.append(self.xml_tag('TARA1', ''))
            xfa.append(self.xml_tag('COD_OP1', ''))
        xfa.append('</dd2\n>')
        xfa.append('<dd4 xfa:dataNode="dataGroup"\n/>')
        xfa.append('</body3\n>')

        # Body4 - empty
        xfa.append('<body4\n>')
        xfa.append('<dd1 xfa:dataNode="dataGroup"\n/>')
        xfa.append('<dd2\n>')
        xfa.append(self.xml_tag('seq', ''))
        xfa.append(self.xml_tag('TARA1', ''))
        xfa.append(self.xml_tag('COD_OP1', ''))
        xfa.append(self.xml_tag('TARA2', ''))
        xfa.append(self.xml_tag('COD_OP2', ''))
        xfa.append(self.xml_tag('motiv', ''))
        xfa.append('</dd2\n>')
        xfa.append('</body4\n>')

        # Body2 - Lista operatii
        xfa.append('<body2\n>')
        xfa.append('<dd1\n>')
        xfa.append('<OP1\n>')

        for idx, op in enumerate(operatii, start=1):
            xfa.append('<OP2\n>')
            xfa.append(self.xml_tag('seq', str(idx)))
            xfa.append(self.xml_tag('TIP_OP', op.get('tip', '')))
            xfa.append(self.xml_tag('TARA', op.get('tara', '')))
            xfa.append(self.xml_tag('COD_OP', op.get('codO', '')))
            xfa.append(self.xml_tag('DEN_OP', op.get('denO', '')))
            xfa.append(self.xml_tag('BAZA', op.get('baza', '0')))
            xfa.append('</OP2\n>')

        # Daca nu sunt operatii, adauga una goala
        if not operatii:
            xfa.append('<OP2\n>')
            xfa.append(self.xml_tag('seq', '1'))
            xfa.append(self.xml_tag('TIP_OP', ''))
            xfa.append(self.xml_tag('TARA', ''))
            xfa.append(self.xml_tag('COD_OP', ''))
            xfa.append(self.xml_tag('DEN_OP', ''))
            xfa.append(self.xml_tag('BAZA', ''))
            xfa.append('</OP2\n>')

        xfa.append('</OP1\n>')

        xfa.append('<TG\n>')
        xfa.append(self.xml_tag('TOTAL_BAZA', total_baza))
        xfa.append('</TG\n>')

        xfa.append('<BUTOANE\n>')
        xfa.append(self.xml_tag('unicitate', ''))
        xfa.append('</BUTOANE\n>')

        xfa.append('</dd1\n>')
        xfa.append('</body2\n>')

        xfa.append('</form1\n>')
        xfa.append('</xfa:data\n>')
        xfa.append('</xfa:datasets\n>')

        return ''.join(xfa)


def generate_d390_pdf(xml_content: bytes, pdf_template_path: str, attach_xml: bool = True) -> bytes:
    """Genereaza PDF D390 completat din continutul XML."""
    converter = D390ToXFAConverter(xml_content)
    xfa_datasets = converter.generate_xfa_datasets()

    reader = PdfReader(pdf_template_path)
    writer = PdfWriter()
    writer.clone_document_from_reader(reader)

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

                    encoded_data = xfa_datasets.encode('utf-8')
                    stream_obj._data = encoded_data

                    if '/Filter' in stream_obj:
                        del stream_obj[NameObject('/Filter')]
                    if '/DecodeParms' in stream_obj:
                        del stream_obj[NameObject('/DecodeParms')]

                    stream_obj[NameObject('/Length')] = NumberObject(len(encoded_data))
                    break

    if attach_xml:
        root = ET.fromstring(xml_content)
        luna = root.get('luna', '00')
        an = root.get('an', '0000')
        attachment_name = f"D390_{an}_{luna}.xml"
        writer.add_attachment(attachment_name, xml_content)

    output_buffer = io.BytesIO()
    writer.write(output_buffer)
    output_buffer.seek(0)

    return output_buffer.getvalue()
