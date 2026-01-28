# -*- coding: utf-8 -*-
"""
D394 PDF Generator Service
Converteste XML ANAF D394 in format XFA si genereaza PDF completat.
"""

import io
from xml.etree import ElementTree as ET
from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject, NumberObject


class D394ToXFAConverter:
    """Converteste XML ANAF D394 in format XFA"""

    def __init__(self, xml_content: bytes):
        self.root = ET.fromstring(xml_content)
        self.ns = {'anaf': 'mfp:anaf:dgti:d394:declaratie:v5'}

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
        tip_d394 = self.get_attr('tip_D394', 'L')
        sistem_tva = self.get_attr('sistemTVA', '0')
        op_efectuate = self.get_attr('op_efectuate', '0')
        prs_afiliat = self.get_attr('prsAfiliat', '0')

        cui = self.get_attr('cui', '')
        caen = self.get_attr('caen', '')
        den = self.get_attr('den', '')
        adresa = self.get_attr('adresa', '')
        telefon = self.get_attr('telefon', '')
        mail = self.get_attr('mail', '')
        totalPlata_A = self.get_attr('totalPlata_A', '0')

        denR = self.get_attr('denR', '')
        functie_reprez = self.get_attr('functie_reprez', '')
        adresaR = self.get_attr('adresaR', '')

        tip_intocmit = self.get_attr('tip_intocmit', '0')
        calitate_intocmit = self.get_attr('calitate_intocmit', '0')
        den_intocmit = self.get_attr('den_intocmit', '')
        cif_intocmit = self.get_attr('cif_intocmit', '')
        optiune = self.get_attr('optiune', '0')

        # Informatii
        info_elem = self.find_element('informatii')
        info = {}
        if info_elem is not None:
            for attr in info_elem.attrib:
                info[attr] = info_elem.get(attr, '0')

        # Rezumat1 si Rezumat2
        rezumat1_list = self.find_all_elements('rezumat1')
        rezumat2_elem = self.find_element('rezumat2')

        # Serie facturi
        serie_facturi = self.find_all_elements('serieFacturi')

        # Operatiuni
        op1_list = self.find_all_elements('op1')

        # Construieste XFA
        xfa = []
        xfa.append('\n<xfa:datasets xmlns:xfa="http://www.xfa.org/schema/xfa-data/1.0/"\n>')
        xfa.append('<xfa:data\n>')
        xfa.append('<form1\n>')

        xfa.append(self.xml_tag('universalCode', 'D394_A8.0.1'))

        # Body1 - Header si identificare
        xfa.append('<body1\n>')
        xfa.append('<HEADER xfa:dataNode="dataGroup"\n/>')

        xfa.append('<sub_per\n>')
        xfa.append(self.xml_tag('an_r', an))
        xfa.append(self.xml_tag('TIP_D394', tip_d394))
        xfa.append(self.xml_tag('luna_r', luna))
        xfa.append(self.xml_tag('sistem', sistem_tva))
        xfa.append(self.xml_tag('operatiuni', op_efectuate))
        xfa.append(self.xml_tag('prsAfiliat', prs_afiliat))
        xfa.append('</sub_per\n>')

        xfa.append('<sub_dateDeIdentificare\n>')
        xfa.append(self.xml_tag('cif', cui))
        xfa.append(self.xml_tag('den', den))
        xfa.append(self.xml_tag('adresa', adresa))
        xfa.append(self.xml_tag('telefon', telefon))
        xfa.append(self.xml_tag('fax', ''))
        xfa.append(self.xml_tag('mail', mail))
        xfa.append(self.xml_tag('d_rec', '0'))
        xfa.append(self.xml_tag('caen1', ''))
        xfa.append(self.xml_tag('caen', caen))
        xfa.append('</sub_dateDeIdentificare\n>')

        xfa.append('</body1\n>')

        # Body11 - Reprezentant
        xfa.append('<body11\n>')
        xfa.append('<sub_dateDeIdentificare\n>')
        xfa.append(self.xml_tag('cifR', cif_intocmit))
        xfa.append(self.xml_tag('denR', denR))
        xfa.append(self.xml_tag('adresaR', adresaR))
        xfa.append(self.xml_tag('telefonR', ''))
        xfa.append(self.xml_tag('faxR', ''))
        xfa.append(self.xml_tag('mailR', ''))
        xfa.append('</sub_dateDeIdentificare\n>')
        xfa.append('</body11\n>')

        # Body10 - Total
        xfa.append('<body10\n>')
        xfa.append(self.xml_tag('totalPlata_A', totalPlata_A))
        xfa.append('</body10\n>')

        # BodyC - Rezumat pe cote (persoane juridice)
        xfa.append('<bodyC\n>')
        xfa.append(self.xml_tag('nrCUI', info.get('nrCui1', '0')))

        # Pentru fiecare cota din rezumat1 cu tip_partener=1 (PJ)
        pj_rezumat = [r for r in rezumat1_list if r.get('tip_partener') == '1']
        if pj_rezumat:
            for rez in pj_rezumat:
                xfa.append('<Crepet\n>')
                xfa.append(self.xml_tag('cota', rez.get('cota', '')))
                xfa.append('<tabel\n>')
                xfa.append('<HeaderRow xfa:dataNode="dataGroup"\n/>')
                xfa.append('<L\n>')
                xfa.append(self.xml_tag('facturi', rez.get('facturiL', '0')))
                xfa.append(self.xml_tag('baza', rez.get('bazaL', '0')))
                xfa.append(self.xml_tag('tva', rez.get('tvaL', '0')))
                xfa.append('</L\n>')
                # Empty sections
                for sec in ['LS', 'AN', 'AI', 'ASN', 'V', 'Vcer', 'Vdes', 'Vmasa', 'Vcertif',
                           'Venerg', 'Vcertif_verzi', 'Vteren', 'Vaur', 'Vtel', 'Vmicro',
                           'Vcons', 'Vgaze', 'C', 'Ccer', 'Cdes', 'Cmasa', 'Ccertif',
                           'Cenerg', 'Ccertif_verzi', 'Cteren', 'Caur', 'Ctel', 'Cmicro',
                           'Ccons', 'Cgaze']:
                    xfa.append(f'<{sec}\n>')
                    xfa.append(self.xml_tag('facturi', ''))
                    xfa.append(self.xml_tag('baza', ''))
                    if sec not in ['LS', 'ASN', 'V', 'Vcer', 'Vdes', 'Vmasa', 'Vcertif',
                                   'Venerg', 'Vcertif_verzi', 'Vteren', 'Vaur', 'Vtel',
                                   'Vmicro', 'Vcons', 'Vgaze']:
                        xfa.append(self.xml_tag('tva', ''))
                    xfa.append(f'</{sec}\n>')
                xfa.append('</tabel\n>')
                xfa.append('</Crepet\n>')
        else:
            xfa.append('<Crepet\n>')
            xfa.append(self.xml_tag('cota', ''))
            xfa.append('<tabel\n>')
            xfa.append('<HeaderRow xfa:dataNode="dataGroup"\n/>')
            for sec in ['L', 'LS', 'AN', 'AI', 'ASN', 'V', 'Vcer', 'Vdes', 'Vmasa', 'Vcertif',
                       'Venerg', 'Vcertif_verzi', 'Vteren', 'Vaur', 'Vtel', 'Vmicro',
                       'Vcons', 'Vgaze', 'C', 'Ccer', 'Cdes', 'Cmasa', 'Ccertif',
                       'Cenerg', 'Ccertif_verzi', 'Cteren', 'Caur', 'Ctel', 'Cmicro',
                       'Ccons', 'Cgaze']:
                xfa.append(f'<{sec}\n>')
                xfa.append(self.xml_tag('facturi', ''))
                xfa.append(self.xml_tag('baza', ''))
                if sec not in ['LS', 'ASN', 'V', 'Vcer', 'Vdes', 'Vmasa', 'Vcertif',
                               'Venerg', 'Vcertif_verzi', 'Vteren', 'Vaur', 'Vtel',
                               'Vmicro', 'Vcons', 'Vgaze']:
                    xfa.append(self.xml_tag('tva', ''))
                xfa.append(f'</{sec}\n>')
            xfa.append('</tabel\n>')
            xfa.append('</Crepet\n>')

        xfa.append('</bodyC\n>')

        # BodyD - Rezumat pe cote (persoane fizice)
        xfa.append('<bodyD\n>')
        xfa.append(self.xml_tag('nrCUI', info.get('nrCui2', '0')))

        pf_rezumat = [r for r in rezumat1_list if r.get('tip_partener') == '2']
        if pf_rezumat:
            for rez in pf_rezumat:
                xfa.append('<Drepet\n>')
                xfa.append(self.xml_tag('cota', rez.get('cota', '')))
                xfa.append('<tab1\n>')
                xfa.append('<HeaderRow xfa:dataNode="dataGroup"\n/>')
                xfa.append('<L\n>')
                xfa.append(self.xml_tag('facturi', rez.get('facturiL', '0')))
                xfa.append(self.xml_tag('baza', rez.get('bazaL', '0')))
                xfa.append(self.xml_tag('tva', rez.get('tvaL', '0')))
                xfa.append('</L\n>')
                xfa.append('<LS\n>')
                xfa.append(self.xml_tag('facturi', ''))
                xfa.append(self.xml_tag('baza', ''))
                xfa.append('</LS\n>')
                xfa.append('</tab1\n>')
                xfa.append('</Drepet\n>')
        else:
            xfa.append('<Drepet\n>')
            xfa.append(self.xml_tag('cota', ''))
            xfa.append('<tab1\n>')
            xfa.append('<HeaderRow xfa:dataNode="dataGroup"\n/>')
            xfa.append('<L\n>')
            xfa.append(self.xml_tag('facturi', ''))
            xfa.append(self.xml_tag('baza', ''))
            xfa.append(self.xml_tag('tva', ''))
            xfa.append('</L\n>')
            xfa.append('<LS\n>')
            xfa.append(self.xml_tag('facturi', ''))
            xfa.append(self.xml_tag('baza', ''))
            xfa.append('</LS\n>')
            xfa.append('</tab1\n>')
            xfa.append('</Drepet\n>')

        # Tab2 empty
        xfa.append('<tab2\n>')
        xfa.append('<HeaderRow xfa:dataNode="dataGroup"\n/>')
        for cat in ['total', 'cereale', 'deseuri', 'masa', 'terenuri', 'constructii', 'alte', 'servicii']:
            xfa.append(f'<{cat}\n>')
            for f in ['facturi', 'bord', 'file', 'contracte', 'alted', 'vfacturi', 'vbord', 'vfile', 'vcontracte', 'valted']:
                xfa.append(self.xml_tag(f, ''))
            xfa.append(f'</{cat}\n>')
        xfa.append('</tab2\n>')

        xfa.append('</bodyD\n>')

        # BodyE, BodyF - empty
        for body in ['bodyE', 'bodyF']:
            xfa.append(f'<{body}\n>')
            xfa.append(self.xml_tag('nrCUI', '0'))
            letter = body[-1].upper()
            xfa.append(f'<{letter}repet\n>')
            xfa.append(self.xml_tag('cota', ''))
            xfa.append('<tab1\n>')
            xfa.append('<HeaderRow xfa:dataNode="dataGroup"\n/>')
            for sec in ['L', 'LS', 'C']:
                xfa.append(f'<{sec}\n>')
                xfa.append(self.xml_tag('facturi', ''))
                xfa.append(self.xml_tag('baza', ''))
                if sec != 'LS':
                    xfa.append(self.xml_tag('tva', ''))
                xfa.append(f'</{sec}\n>')
            xfa.append('</tab1\n>')
            xfa.append(f'</{letter}repet\n>')
            xfa.append(f'</{body}\n>')

        # BodyG - Incasari
        xfa.append('<bodyG\n>')
        xfa.append(self.xml_tag('totalbonuri', info.get('nr_BF_i1', '0')))
        xfa.append(self.xml_tag('incasari1', info.get('incasari_i1', '0')))
        xfa.append(self.xml_tag('incasari2', info.get('incasari_i2', '0')))
        xfa.append('<incas\n>')
        xfa.append('<HeaderRow xfa:dataNode="dataGroup"\n/>')
        for rate in ['i121', 'i120', 'i119', 'i111', 'i19', 'i15', 'i221', 'i220', 'i219', 'i211', 'i29', 'i25']:
            xfa.append(f'<{rate}\n>')
            xfa.append(self.xml_tag('baza', ''))
            xfa.append(self.xml_tag('tva', ''))
            xfa.append(f'</{rate}\n>')
        xfa.append('</incas\n>')
        xfa.append('</bodyG\n>')

        # BodyH - Rezumat total
        xfa.append('<bodyH\n>')
        xfa.append('<H\n>')
        xfa.append(self.xml_tag('totalPlata_A', totalPlata_A))

        # Cote TVA
        rez2 = {}
        if rezumat2_elem is not None:
            for attr in rezumat2_elem.attrib:
                rez2[attr] = rezumat2_elem.get(attr, '0')

        for cota in ['c24', 'c21', 'c20', 'c19', 'c11', 'c9', 'c5']:
            xfa.append(f'<{cota}\n>')
            xfa.append('<HeaderRow xfa:dataNode="dataGroup"\n/>')
            cota_num = cota[1:]
            for tip in ['LV', 'AC', 'AI']:
                xfa.append(f'<{tip}\n>')
                if tip == 'LV' and cota_num == rez2.get('cota', ''):
                    xfa.append(self.xml_tag('facturi', rez2.get('nrFacturiL', '0')))
                    xfa.append(self.xml_tag('baza', rez2.get('bazaL', '0')))
                    xfa.append(self.xml_tag('tva', rez2.get('tvaL', '0')))
                else:
                    xfa.append(self.xml_tag('facturi', ''))
                    xfa.append(self.xml_tag('baza', ''))
                    xfa.append(self.xml_tag('tva', ''))
                xfa.append(f'</{tip}\n>')
            xfa.append(f'</{cota}\n>')

        xfa.append('</H\n>')
        xfa.append('</bodyH\n>')

        # RezI - Serie facturi
        xfa.append('<rezI\n>')
        xfa.append('<I1\n>')
        xfa.append('<info1\n>')
        xfa.append('<HeaderRow xfa:dataNode="dataGroup"\n/>')
        for rate in ['L24', 'L21', 'L20', 'L19', 'L11', 'L9', 'L5',
                    'LI24', 'LI21', 'LI20', 'LI19', 'LI11', 'LI9', 'LI5',
                    'A24', 'A21', 'A20', 'A19', 'A11', 'A9', 'A5',
                    'AI24', 'AI21', 'AI20', 'AI19', 'AI11', 'AI9', 'AI5',
                    'AB24', 'AB20', 'AB21', 'AB19', 'AB11', 'AB9', 'AB5']:
            xfa.append(f'<{rate}\n>')
            xfa.append(self.xml_tag('baza', ''))
            xfa.append(self.xml_tag('tva', ''))
            xfa.append(f'</{rate}\n>')
        xfa.append('</info1\n>')
        xfa.append('</I1\n>')

        xfa.append('<i2\n>')
        xfa.append('<plaja1\n>')
        xfa.append(self.xml_tag('serie_i', ''))
        xfa.append(self.xml_tag('nr_f', ''))
        xfa.append(self.xml_tag('serie_f', ''))
        xfa.append(self.xml_tag('nr_i', ''))
        xfa.append('</plaja1\n>')

        # Facturi emise
        xfa.append('<facturi2\n>')
        xfa.append(self.xml_tag('fact_emise', '0'))
        xfa.append('<plaja\n>')
        xfa.append(self.xml_tag('nr_f', ''))
        xfa.append(self.xml_tag('serie_f', ''))
        xfa.append(self.xml_tag('nr_i', ''))
        xfa.append(self.xml_tag('serie_i', ''))
        xfa.append('</plaja\n>')
        xfa.append('<detaliu_fact\n>')
        xfa.append(self.xml_tag('tip_fact', ''))
        xfa.append(self.xml_tag('serie', ''))
        xfa.append(self.xml_tag('nr', ''))
        xfa.append('<autofacturare\n>')
        for f in ['baza24', 'tva24', 'tva20', 'baza20', 'tva19', 'baza19',
                 'baza11', 'baza5', 'tva5', 'baza9', 'tva9', 'tva11', 'baza21', 'tva21']:
            xfa.append(self.xml_tag(f, ''))
        xfa.append('</autofacturare\n>')
        xfa.append('</detaliu_fact\n>')
        xfa.append('</facturi2\n>')

        # Serie facturi 3 si 4
        xfa.append('<facturi3\n>')
        xfa.append(self.xml_tag('fact_emise', str(len(serie_facturi))))
        for sf in serie_facturi:
            xfa.append('<plaja\n>')
            xfa.append(self.xml_tag('nr_f', sf.get('nrI', '')))
            xfa.append(self.xml_tag('serie_f', sf.get('serieI', '')))
            xfa.append(self.xml_tag('nr_i', sf.get('nrI', '')))
            xfa.append(self.xml_tag('serie_i', sf.get('serieI', '')))
            xfa.append(self.xml_tag('den', sf.get('den', '')))
            xfa.append(self.xml_tag('cui', sf.get('cui', '')))
            xfa.append('</plaja\n>')
        if not serie_facturi:
            xfa.append('<plaja\n>')
            for f in ['nr_f', 'serie_f', 'nr_i', 'serie_i', 'den', 'cui']:
                xfa.append(self.xml_tag(f, ''))
            xfa.append('</plaja\n>')
        xfa.append('</facturi3\n>')

        xfa.append('<facturi4\n>')
        xfa.append(self.xml_tag('fact_emise', '0'))
        xfa.append('<plaja\n>')
        for f in ['nr_f', 'serie_f', 'nr_i', 'serie_i', 'cui', 'den']:
            xfa.append(self.xml_tag(f, ''))
        xfa.append('</plaja\n>')
        xfa.append('</facturi4\n>')

        xfa.append('</i2\n>')
        xfa.append('</rezI\n>')

        # Sold negativ
        xfa.append('<sold_neg\n>')
        xfa.append(self.xml_tag('solicit', '0'))
        xfa.append('<tab\n>')
        xfa.append('<tab1\n>')
        xfa.append('<Row1 xfa:dataNode="dataGroup"\n/>')
        for r in ['r2', 'r3', 'r4', 'r5', 'r6']:
            xfa.append(f'<{r}\n>')
            xfa.append(self.xml_tag('da', '0'))
            xfa.append(f'</{r}\n>')
        xfa.append('<r7 xfa:dataNode="dataGroup"\n/>')
        for r in ['r8', 'r1_1', 'r9', 'r10', 'r2_1', 'r11', 'r12']:
            xfa.append(f'<{r}\n>')
            xfa.append(self.xml_tag('da', '0'))
            xfa.append(f'</{r}\n>')
        xfa.append('<r13 xfa:dataNode="dataGroup"\n/>')
        for r in ['r14', 'r3_1', 'r15', 'r16', 'r4_1', 'r17', 'r18', 'r19', 'r20']:
            xfa.append(f'<{r}\n>')
            xfa.append(self.xml_tag('da', '0'))
            xfa.append(f'</{r}\n>')
        xfa.append('</tab1\n>')

        xfa.append('<tab2\n>')
        xfa.append('<r1\n>')
        xfa.append(self.xml_tag('da', '0'))
        xfa.append('</r1\n>')
        xfa.append('<Row2 xfa:dataNode="dataGroup"\n/>')
        for r in ['r2', 'r1_1', 'r3', 'r4', 'r2_1', 'r5', 'r6', 'r7', 'r8']:
            xfa.append(f'<{r}\n>')
            xfa.append(self.xml_tag('da', '0'))
            xfa.append(f'</{r}\n>')
        xfa.append('<r9 xfa:dataNode="dataGroup"\n/>')
        for r in ['r10', 'r3_1', 'r11', 'r12']:
            xfa.append(f'<{r}\n>')
            xfa.append(self.xml_tag('da', '0'))
            xfa.append(f'</{r}\n>')
        xfa.append('</tab2\n>')
        xfa.append('</tab\n>')
        xfa.append('</sold_neg\n>')

        # Semnatura
        xfa.append('<semnatura\n>')
        xfa.append(self.xml_tag('tip_intocmit', tip_intocmit))
        xfa.append(self.xml_tag('calitate_intocmit', calitate_intocmit))
        xfa.append(self.xml_tag('den_intocmit', den_intocmit))
        xfa.append(self.xml_tag('cif_intocmit', cif_intocmit))
        xfa.append(self.xml_tag('functie', functie_reprez))
        xfa.append(self.xml_tag('optiune', optiune))
        xfa.append('</semnatura\n>')

        xfa.append('</form1\n>')
        xfa.append('</xfa:data\n>')
        xfa.append('</xfa:datasets\n>')

        return ''.join(xfa)


def generate_d394_pdf(xml_content: bytes, pdf_template_path: str, attach_xml: bool = True) -> bytes:
    """Genereaza PDF D394 completat din continutul XML."""
    converter = D394ToXFAConverter(xml_content)
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
        attachment_name = f"D394_{an}_{luna}.xml"
        writer.add_attachment(attachment_name, xml_content)

    output_buffer = io.BytesIO()
    writer.write(output_buffer)
    output_buffer.seek(0)

    return output_buffer.getvalue()
