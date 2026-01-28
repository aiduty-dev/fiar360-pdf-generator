# -*- coding: utf-8 -*-
"""
D301 PDF Generator Service
Converteste XML ANAF D301 in format XFA si genereaza PDF completat.
"""

import io
from xml.etree import ElementTree as ET
from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject, NumberObject


class D301ToXFAConverter:
    """Converteste XML ANAF D301 in format XFA"""

    def __init__(self, xml_content: bytes):
        self.root = ET.fromstring(xml_content)
        self.ns = {'anaf': 'mfp:anaf:dgti:d301:declaratie:v1'}

    def get_attr(self, element, attr, default=''):
        if element is None:
            return default
        return element.get(attr, default) or default

    def find_all_sections(self):
        """Gaseste toate sectiunile din XML"""
        results = []
        for child in self.root:
            local_name = child.tag.split('}')[-1] if '}' in child.tag else child.tag
            if local_name == 'sectiune':
                results.append(child)
        return results

    def xml_tag(self, name, value):
        if value is None or value == '':
            return f'<{name}\n/>'
        return f'<{name}\n>{value}</{name}\n>'

    def generate_xfa_datasets(self):
        """Genereaza XML-ul XFA datasets complet"""

        # Date din root
        luna = self.root.get('luna', '')
        an = self.root.get('an', '')
        d_rec = self.root.get('d_rec', '0')
        mijl_trans = self.root.get('mijl_trans', '0')
        temei = self.root.get('temei', '0')
        cif = self.root.get('cif', '')
        denumire = self.root.get('denumire', '')
        adresa = self.root.get('adresa', '')
        telefon = self.root.get('telefon', '')
        email = self.root.get('email', '')
        banca = self.root.get('banca', '')
        cont = self.root.get('cont', '')
        pers_inreg = self.root.get('pers_inreg', '1')
        nr_evid = self.root.get('nr_evid', '')

        baza1 = self.root.get('baza1', '0.00')
        tva1 = self.root.get('tva1', '0.00')
        baza2 = self.root.get('baza2', '0.00')
        tva2 = self.root.get('tva2', '0.00')
        baza3 = self.root.get('baza3', '0.00')
        tva3 = self.root.get('tva3', '0.00')
        baza4 = self.root.get('baza4', '0.00')
        tva4 = self.root.get('tva4', '0.00')
        baza5 = self.root.get('baza5', '0.00')
        tva5 = self.root.get('tva5', '0.00')
        totalPlata_A = self.root.get('totalPlata_A', '0')

        nume_declarant = self.root.get('nume_declarant', '')
        prenume_declarant = self.root.get('prenume_declarant', '')
        functia_declarant = self.root.get('functia_declarant', '')

        # Calculeaza totaluri
        try:
            Tbaza = float(baza1) + float(baza2) + float(baza3) + float(baza4) + float(baza5)
            Ttva = float(tva1) + float(tva2) + float(tva3) + float(tva4) + float(tva5)
        except:
            Tbaza = 0.00
            Ttva = 0.00

        # Temei legal
        literaa = '1' if temei == '1' else '0'
        literab = '1' if temei == '2' else '0'

        # Sectiuni pe tip operatie
        sections = self.find_all_sections()
        sections_by_type = {1: [], 2: [], 3: [], 4: [], 5: []}
        for sec in sections:
            tip = int(self.get_attr(sec, 'tip_operatie', '1'))
            if tip in sections_by_type:
                sections_by_type[tip].append(sec)

        # Construieste XFA
        xfa = []
        xfa.append('\n<xfa:datasets xmlns:xfa="http://www.xfa.org/schema/xfa-data/1.0/"\n>')
        xfa.append('<xfa:data\n>')
        xfa.append('<form1\n>')

        # Cod formular
        xfa.append('<codF1\n>')
        xfa.append(self.xml_tag('universalCode', 'D301_A2.0.4'))
        xfa.append(self.xml_tag('codF2', '301'))
        xfa.append('</codF1\n>')

        # Body0 - Header si date identificare
        xfa.append('<body0\n>')

        xfa.append('<header\n>')
        xfa.append(self.xml_tag('an_r', an))
        xfa.append(self.xml_tag('luna_r', luna))
        xfa.append(self.xml_tag('mtn', mijl_trans))
        xfa.append(self.xml_tag('d_rec', d_rec))
        xfa.append('</header\n>')

        xfa.append('<temeilegal\n>')
        xfa.append(self.xml_tag('literab', literab))
        xfa.append(self.xml_tag('literaa', literaa))
        xfa.append('</temeilegal\n>')

        xfa.append('<sub1\n>')
        xfa.append(self.xml_tag('cif', cif))
        xfa.append(self.xml_tag('text_denumire', denumire))
        xfa.append(self.xml_tag('text_adresa', adresa))
        xfa.append(self.xml_tag('text_telefon', telefon))
        xfa.append(self.xml_tag('text_fax', ''))
        xfa.append(self.xml_tag('text_email', email))
        xfa.append(self.xml_tag('TIP_PERSOANA', pers_inreg))
        xfa.append(self.xml_tag('banca', banca))
        xfa.append(self.xml_tag('cont', cont))
        xfa.append(self.xml_tag('RO', 'RO'))
        xfa.append('</sub1\n>')

        xfa.append('<sub2\n>')
        xfa.append(self.xml_tag('nume', nume_declarant))
        xfa.append(self.xml_tag('prenume', prenume_declarant))
        xfa.append(self.xml_tag('functie', functia_declarant))
        xfa.append('</sub2\n>')

        xfa.append('<rezumat\n>')
        xfa.append(self.xml_tag('baza1', baza1))
        xfa.append(self.xml_tag('tva1', tva1))
        xfa.append(self.xml_tag('baza2', baza2))
        xfa.append(self.xml_tag('tva2', tva2))
        xfa.append(self.xml_tag('baza3', baza3))
        xfa.append(self.xml_tag('tva3', tva3))
        xfa.append(self.xml_tag('baza41', baza4))
        xfa.append(self.xml_tag('tva41', tva4))
        xfa.append(self.xml_tag('baza42', baza5))
        xfa.append(self.xml_tag('tva42', tva5))
        xfa.append(self.xml_tag('Tbaza', f'{Tbaza:.2f}'))
        xfa.append(self.xml_tag('Ttva', f'{Ttva:.2f}'))
        xfa.append(self.xml_tag('totalPlata_A', totalPlata_A))
        xfa.append(self.xml_tag('NR_JUSTIFICATIV', nr_evid))
        xfa.append('</rezumat\n>')

        xfa.append('<subEnd\n>')
        xfa.append(self.xml_tag('checkIfOneRowCompleted', '1' if sections else ''))
        xfa.append('</subEnd\n>')

        xfa.append('</body0\n>')

        # Body1 - Tabele cu sectiuni
        xfa.append('<body1\n>')
        xfa.append('<main1\n>')

        # Genereaza cele 5 tabele
        for table_num in range(1, 6):
            xfa.append(f'<Table{table_num}\n>')
            xfa.append(f'<th1 xfa:dataNode="dataGroup"\n/>')
            xfa.append(f'<th1 xfa:dataNode="dataGroup"\n/>')
            xfa.append(f'<th2 xfa:dataNode="dataGroup"\n/>')

            table_sections = sections_by_type.get(table_num, [])
            table_baza_total = 0.0
            table_tva_total = 0.0

            for sec in table_sections:
                xfa.append(f'<rx{table_num}\n>')
                xfa.append(self.xml_tag('TextField7', ''))
                xfa.append(self.xml_tag('NR_DOCUMENT', self.get_attr(sec, 'nr_doc')))
                xfa.append(self.xml_tag('DATA_DOCUMENT', self.get_attr(sec, 'data_doc')))
                xfa.append(self.xml_tag('VALOARE_VALUTA', self.get_attr(sec, 'val_valuta')))
                xfa.append(self.xml_tag('TIP_VALUTA', self.get_attr(sec, 'tip_valuta')))
                xfa.append(self.xml_tag('CURS_VALUTAR', self.get_attr(sec, 'curs_valutar')))
                xfa.append(self.xml_tag('BAZA_IMPOZITARE', self.get_attr(sec, 'baza')))
                xfa.append(self.xml_tag('TVA_DATORAT', self.get_attr(sec, 'tva')))
                xfa.append(f'</rx{table_num}\n>')

                try:
                    table_baza_total += float(self.get_attr(sec, 'baza', '0'))
                    table_tva_total += float(self.get_attr(sec, 'tva', '0'))
                except:
                    pass

            # Daca nu sunt sectiuni, adauga un rand gol
            if not table_sections:
                xfa.append(f'<rx{table_num}\n>')
                xfa.append(self.xml_tag('TextField7', ''))
                xfa.append(self.xml_tag('NR_DOCUMENT', ''))
                xfa.append(self.xml_tag('DATA_DOCUMENT', ''))
                xfa.append(self.xml_tag('VALOARE_VALUTA', ''))
                xfa.append(self.xml_tag('TIP_VALUTA', ''))
                xfa.append(self.xml_tag('CURS_VALUTAR', ''))
                xfa.append(self.xml_tag('BAZA_IMPOZITARE', ''))
                xfa.append(self.xml_tag('TVA_DATORAT', ''))
                xfa.append(f'</rx{table_num}\n>')

            xfa.append('<rtotals\n>')
            xfa.append(self.xml_tag('BAZA', f'{table_baza_total:.2f}' if table_baza_total else '0.00'))
            xfa.append(self.xml_tag('TVA', f'{table_tva_total:.2f}' if table_tva_total else '0.00'))
            xfa.append('</rtotals\n>')

            xfa.append(f'</Table{table_num}\n>')

        xfa.append('</main1\n>')
        xfa.append('</body1\n>')

        xfa.append('</form1\n>')
        xfa.append('</xfa:data\n>')
        xfa.append('</xfa:datasets\n>')

        return ''.join(xfa)


def generate_d301_pdf(xml_content: bytes, pdf_template_path: str, attach_xml: bool = True) -> bytes:
    """
    Genereaza PDF D301 completat din continutul XML.
    """
    converter = D301ToXFAConverter(xml_content)
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
        attachment_name = f"D301_{an}_{luna}.xml"
        writer.add_attachment(attachment_name, xml_content)

    output_buffer = io.BytesIO()
    writer.write(output_buffer)
    output_buffer.seek(0)

    return output_buffer.getvalue()
