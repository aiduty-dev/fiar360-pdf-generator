# -*- coding: utf-8 -*-
"""
D300 PDF Generator Service
Converteste XML ANAF D300 (Decont TVA) in format XFA si genereaza PDF completat.
"""

import io
from xml.etree import ElementTree as ET
from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject, NumberObject, BooleanObject, DecodedStreamObject, ArrayObject, IndirectObject


class D300ToXFAConverter:
    """Converteste XML ANAF D300 in format XFA"""

    # Mapare judete pentru dropdown XFA
    JUDETE_MAP = {
        'ALBA': '1', 'ARAD': '2', 'ARGES': '3', 'ARGEȘ': '3', 'BACAU': '4', 'BACĂU': '4',
        'BIHOR': '5', 'BISTRITA-NASAUD': '6', 'BISTRIȚA-NĂSĂUD': '6', 'BOTOSANI': '7', 'BOTOȘANI': '7',
        'BRASOV': '8', 'BRAȘOV': '8', 'BRAILA': '9', 'BRĂILA': '9', 'BUZAU': '10', 'BUZĂU': '10',
        'CARAS-SEVERIN': '11', 'CARAȘ-SEVERIN': '11', 'CALARASI': '51', 'CĂLĂRAȘI': '51',
        'CLUJ': '12', 'CONSTANTA': '13', 'CONSTANȚA': '13', 'CONSTANŢA': '13',
        'COVASNA': '14', 'DAMBOVITA': '15', 'DÂMBOVIȚA': '15', 'DOLJ': '16',
        'GALATI': '17', 'GALAȚI': '17', 'GIURGIU': '52', 'GORJ': '18',
        'HARGHITA': '19', 'HUNEDOARA': '20', 'IALOMITA': '21', 'IALOMIȚA': '21',
        'IASI': '22', 'IAȘI': '22', 'ILFOV': '53', 'MARAMURES': '24', 'MARAMUREȘ': '24',
        'MEHEDINTI': '25', 'MEHEDINȚI': '25', 'MURES': '26', 'MUREȘ': '26',
        'NEAMT': '27', 'NEAMȚ': '27', 'OLT': '28', 'PRAHOVA': '29',
        'SATU MARE': '30', 'SALAJ': '31', 'SĂLAJ': '31', 'SIBIU': '32',
        'SUCEAVA': '33', 'TELEORMAN': '34', 'TIMIS': '35', 'TIMIȘ': '35',
        'TULCEA': '36', 'VASLUI': '37', 'VALCEA': '38', 'VÂLCEA': '38',
        'VRANCEA': '39', 'BUCURESTI': '40', 'BUCUREȘTI': '40', 'SECTOR 1': '41',
        'SECTOR 2': '42', 'SECTOR 3': '43', 'SECTOR 4': '44', 'SECTOR 5': '45', 'SECTOR 6': '46'
    }

    def __init__(self, xml_content: bytes):
        self.root = ET.fromstring(xml_content)
        self.ns = {'anaf': 'mfp:anaf:dgti:d300:declaratie:v10'}

    def remove_diacritics(self, text):
        """Inlocuieste diacriticele romanesti cu echivalentele ASCII"""
        if not text:
            return text
        replacements = {
            'ă': 'a', 'Ă': 'A', 'â': 'a', 'Â': 'A',
            'î': 'i', 'Î': 'I',
            'ș': 's', 'Ș': 'S', 'ş': 's', 'Ş': 'S',
            'ț': 't', 'Ț': 'T', 'ţ': 't', 'Ţ': 'T'
        }
        for diac, ascii_char in replacements.items():
            text = text.replace(diac, ascii_char)
        return text

    def get_judet_code(self, judet_name):
        """Converteste numele judetului in codul pentru dropdown"""
        if not judet_name:
            return ''
        judet_upper = judet_name.upper().strip()
        return self.JUDETE_MAP.get(judet_upper, '')

    def get_attr(self, attr, default=''):
        return self.root.get(attr, default) or default

    def xml_tag(self, name, value):
        if value is None or value == '':
            return f'<{name}/>'
        return f'<{name}>{value}</{name}>'

    def generate_xfa_datasets(self):
        """Genereaza XML-ul XFA datasets complet"""

        # Date din root
        luna = self.get_attr('luna', '')
        an = self.get_attr('an', '')
        d_rec = self.get_attr('d_rec', '0')
        depus_repr = self.get_attr('depusReprezentant', '0')
        bifa_interne = self.get_attr('bifa_interne', '0')
        temei = self.get_attr('temei', '0')

        # Declarant
        nume_declar = self.get_attr('nume_declar', '')
        prenume_declar = self.get_attr('prenume_declar', '')
        functie_declar = self.get_attr('functie_declar', '')

        # Firma
        cui = self.get_attr('cui', '')
        den = self.get_attr('den', '')
        adresa = self.get_attr('adresa', '')
        telefon = self.get_attr('telefon', '')
        mail = self.get_attr('mail', '')
        banca = self.get_attr('banca', '')
        cont = self.get_attr('cont', '')
        caen = self.get_attr('caen', '')

        # Campuri adresa separate (daca exista in XML)
        strada = self.get_attr('str', '')
        nr_str = self.get_attr('nr', '')
        localitate = self.get_attr('loc', '')
        judet = self.get_attr('judet', '')

        # Daca nu avem campuri separate, incercam sa parsam din adresa combinata
        if not localitate or not judet:
            # Format tipic: "STRADA, nr. X, bl. Y, sc. Z, ap. W, LOCALITATE, JUDET"
            if adresa:
                parts = [p.strip() for p in adresa.split(',')]
                if len(parts) >= 2:
                    # Ultimul element e de obicei judetul
                    judet = parts[-1].strip() if not judet else judet
                    # Penultimul e de obicei localitatea
                    localitate = parts[-2].strip() if not localitate else localitate
                    # Prima parte e strada
                    if not strada:
                        strada = parts[0].strip()

        # Tip decont si alte optiuni
        tip_decont = self.get_attr('tip_decont', 'T')
        pro_rata = self.get_attr('pro_rata', '0')
        bifa_cereale = self.get_attr('bifa_cereale', 'N')
        bifa_mob = self.get_attr('bifa_mob', 'N')
        bifa_disp = self.get_attr('bifa_disp', 'N')
        bifa_cons = self.get_attr('bifa_cons', 'N')
        solicit_ramb = self.get_attr('solicit_ramb', 'N')
        nr_evid = self.get_attr('nr_evid', '')
        totalPlata_A = self.get_attr('totalPlata_A', '0')

        # Randuri (R1-R50)
        rows = {}
        for i in range(1, 61):
            rows[f'R{i}_1'] = self.get_attr(f'R{i}_1', '')
            rows[f'R{i}_2'] = self.get_attr(f'R{i}_2', '')

        # Temei legal
        temei_a = '1' if temei == '1' else '0'
        temei_b = '1' if temei == '2' else '0'

        # Tip decont
        tip_t = '1' if tip_decont == 'T' else '0'
        tip_s = '1' if tip_decont == 'S' else '0'
        tip_c = '1' if tip_decont == 'C' else '0'

        # Construieste XFA (fara XML declaration - este stream embedded)
        xfa = []
        xfa.append('<xfa:datasets xmlns:xfa="http://www.xfa.org/schema/xfa-data/1.0/">')
        xfa.append('<xfa:data>')
        xfa.append('<form1>')

        # Butoane (lasam goale)
        xfa.append('<btnDoc xfa:dataNode="dataGroup"/>')

        # Antet
        xfa.append('<Antet>')
        xfa.append('<IdDoc>')
        xfa.append(self.xml_tag('universalCode', 'D300_A11.0.7'))
        xfa.append(self.xml_tag('formValid', ''))
        xfa.append(self.xml_tag('sgn', ''))
        xfa.append(self.xml_tag('nr_evid', nr_evid))
        xfa.append('</IdDoc>')

        # metaDate - structura necesara pentru validare JavaScript
        xfa.append('<metaDate>')
        xfa.append(self.xml_tag('luna_r', luna))
        xfa.append(self.xml_tag('an_r', an))
        xfa.append(self.xml_tag('d_rez', '0'))
        xfa.append(self.xml_tag('d_rec', d_rec))
        xfa.append(self.xml_tag('tipDecont', tip_decont))
        xfa.append(self.xml_tag('totalPlata_A', totalPlata_A))
        xfa.append('</metaDate>')

        xfa.append('<opInterne>')
        xfa.append(self.xml_tag('mtdSimplificata', bifa_interne))
        xfa.append('</opInterne>')

        # Temei legal - obligatoriu pentru validare
        xfa.append('<temeiLegal>')
        xfa.append(self.xml_tag('a', temei_a))
        xfa.append(self.xml_tag('b', temei_b))
        xfa.append('</temeiLegal>')

        xfa.append(self.xml_tag('cifS', ''))
        xfa.append(self.xml_tag('d_reprezentant', depus_repr))

        xfa.append('</Antet>')

        # Identificare contribuabil
        xfa.append('<identifCntr>')

        xfa.append('<denumire>')
        xfa.append(self.xml_tag('den', self.remove_diacritics(den)))
        xfa.append(self.xml_tag('cif', cui))
        xfa.append('</denumire>')

        xfa.append('<adresa>')
        # Eliminam diacriticele din toate campurile text
        str_clean = self.remove_diacritics(strada if strada else adresa)
        loc_clean = self.remove_diacritics(localitate)
        # Pentru judet folosim codul din dropdown
        judet_code = self.get_judet_code(judet)
        xfa.append(self.xml_tag('str', str_clean))
        xfa.append(self.xml_tag('nr', nr_str))
        xfa.append(self.xml_tag('loc', loc_clean))
        xfa.append(self.xml_tag('judet', judet_code))
        xfa.append(self.xml_tag('sect', ''))
        xfa.append(self.xml_tag('bloc', ''))
        xfa.append(self.xml_tag('scara', ''))
        xfa.append(self.xml_tag('etaj', ''))
        xfa.append(self.xml_tag('apt', ''))
        xfa.append(self.xml_tag('codPst', ''))
        xfa.append('</adresa>')

        xfa.append('<contact>')
        xfa.append(self.xml_tag('telefon', telefon))
        xfa.append(self.xml_tag('fax', ''))
        xfa.append(self.xml_tag('email', mail))
        xfa.append('</contact>')

        xfa.append('<banca>')
        xfa.append(self.xml_tag('den', self.remove_diacritics(banca)))
        xfa.append(self.xml_tag('iban', cont))
        xfa.append('</banca>')

        xfa.append('<Caen>')
        xfa.append(self.xml_tag('caen', caen))
        xfa.append(self.xml_tag('caen1', ''))
        xfa.append('</Caen>')

        # proRata direct sub identifCntr pentru validare
        xfa.append(self.xml_tag('proRata', pro_rata))

        xfa.append('<Gap xfa:dataNode="dataGroup"/>')

        xfa.append('</identifCntr>')

        # Date - sectiunile cu randuri
        xfa.append('<date>')

        xfa.append('<headerColectata xfa:dataNode="dataGroup"/>')

        # Comert
        xfa.append('<comert>')
        for r in range(1, 9):
            xfa.append(f'<r{r}>')
            xfa.append(self.xml_tag('nrCrt', str(r)))
            xfa.append(self.xml_tag('c1', rows.get(f'R{r}_1', '')))
            xfa.append(self.xml_tag('c2', rows.get(f'R{r}_2', '')))
            xfa.append(self.xml_tag('c3', ''))
            xfa.append(f'</r{r}>')
        xfa.append('</comert>')

        # Livrari
        xfa.append('<livrari>')
        for r in range(9, 20):
            xfa.append(f'<r{r}>')
            xfa.append(self.xml_tag('nrCrt', str(r)))
            xfa.append(self.xml_tag('c1', rows.get(f'R{r}_1', '')))
            xfa.append(self.xml_tag('c2', rows.get(f'R{r}_2', '')))
            xfa.append(self.xml_tag('c3', ''))
            xfa.append(f'</r{r}>')
        xfa.append('</livrari>')

        xfa.append('<headerDeductibil xfa:dataNode="dataGroup"/>')

        # Achizitii RO
        xfa.append('<achizitiiRO>')
        for r in range(20, 24):
            xfa.append(f'<r{r}>')
            xfa.append(self.xml_tag('nrCrt', str(r)))
            xfa.append(self.xml_tag('c1', rows.get(f'R{r}_1', '')))
            xfa.append(self.xml_tag('c2', rows.get(f'R{r}_2', '')))
            xfa.append(self.xml_tag('c3', ''))
            xfa.append(f'</r{r}>')
        xfa.append('</achizitiiRO>')

        # Achizitii IMP
        xfa.append('<achizitiiIMP>')
        for r in range(24, 30):
            xfa.append(f'<r{r}>')
            xfa.append(self.xml_tag('nrCrt', str(r)))
            xfa.append(self.xml_tag('c1', rows.get(f'R{r}_1', '')))
            xfa.append(self.xml_tag('c2', rows.get(f'R{r}_2', '')))
            xfa.append(self.xml_tag('c3', ''))
            xfa.append(f'</r{r}>')
        xfa.append('</achizitiiIMP>')

        # R30-R36
        for r in range(30, 37):
            xfa.append(f'<r{r}>')
            xfa.append(self.xml_tag('nrCrt', str(r)))
            xfa.append(self.xml_tag('c1', rows.get(f'R{r}_1', '')))
            xfa.append(self.xml_tag('c2', rows.get(f'R{r}_2', '')))
            xfa.append(self.xml_tag('c3', ''))
            xfa.append(f'</r{r}>')

        xfa.append('<headerRegularizari xfa:dataNode="dataGroup"/>')

        # Regularizari
        xfa.append('<regularizari>')
        for r in range(37, 47):
            xfa.append(f'<r{r}>')
            xfa.append(self.xml_tag('nrCrt', str(r)))
            xfa.append(self.xml_tag('c1', rows.get(f'R{r}_1', '')))
            xfa.append(self.xml_tag('c2', rows.get(f'R{r}_2', '')))
            xfa.append(self.xml_tag('c3', ''))
            xfa.append(f'</r{r}>')
        xfa.append('</regularizari>')

        # Bife
        xfa.append('<bife>')
        xfa.append('<caption xfa:dataNode="dataGroup"/>')
        xfa.append(self.xml_tag('cereale', '1' if bifa_cereale == 'D' else '0'))
        xfa.append(self.xml_tag('mobil', '1' if bifa_mob == 'D' else '0'))
        xfa.append(self.xml_tag('dispElec', '1' if bifa_disp == 'D' else '0'))
        xfa.append(self.xml_tag('construc', '1' if bifa_cons == 'D' else '0'))
        xfa.append('</bife>')

        # Rambursare
        xfa.append('<rambursare>')
        xfa.append('<header1 xfa:dataNode="dataGroup"/>')
        xfa.append('<r47>')
        xfa.append(self.xml_tag('nrCrt', '47'))
        xfa.append(self.xml_tag('c1', '1' if solicit_ramb == 'D' else '0'))
        xfa.append(self.xml_tag('c2', rows.get('R47_2', '')))
        xfa.append('</r47>')
        xfa.append('<header2 xfa:dataNode="dataGroup"/>')
        xfa.append('<r48>')
        xfa.append(self.xml_tag('nrCrt', '48'))
        xfa.append(self.xml_tag('c1', rows.get('R48_1', '')))
        xfa.append(self.xml_tag('c2', rows.get('R48_2', '')))
        xfa.append('</r48>')
        xfa.append('<header3 xfa:dataNode="dataGroup"/>')
        xfa.append('<r49>')
        xfa.append(self.xml_tag('nrCrt', '49'))
        xfa.append(self.xml_tag('c1', rows.get('R49_1', '')))
        xfa.append(self.xml_tag('c2', rows.get('R49_2', '')))
        xfa.append('</r49>')
        xfa.append('</rambursare>')

        xfa.append('<headerDeductibil xfa:dataNode="dataGroup"/>')

        # Nedeductibil
        xfa.append('<nedeductibil>')
        xfa.append('<r50>')
        xfa.append(self.xml_tag('nrCrt', '50'))
        xfa.append(self.xml_tag('c1', rows.get('R50_1', '')))
        xfa.append(self.xml_tag('c2', rows.get('R50_2', '')))
        xfa.append('</r50>')
        xfa.append('<r60>')
        xfa.append(self.xml_tag('nrCrt', '60'))
        xfa.append(self.xml_tag('c1', rows.get('R60_1', '')))
        xfa.append(self.xml_tag('c2', rows.get('R60_2', '')))
        xfa.append('</r60>')
        xfa.append('</nedeductibil>')

        xfa.append('<alteInfo xfa:dataNode="dataGroup"/>')

        xfa.append('</date>')

        # Semnatura
        xfa.append('<semnatura>')
        xfa.append(self.xml_tag('nume', self.remove_diacritics(nume_declar)))
        xfa.append(self.xml_tag('prenume', self.remove_diacritics(prenume_declar)))
        xfa.append(self.xml_tag('smnFnc', self.remove_diacritics(functie_declar)))
        xfa.append('</semnatura>')

        xfa.append('<locOF xfa:dataNode="dataGroup"/>')

        xfa.append('</form1>')
        xfa.append('</xfa:data>')
        xfa.append('</xfa:datasets>')

        return ''.join(xfa)


def generate_d300_pdf(xml_content: bytes, pdf_template_path: str, attach_xml: bool = True) -> bytes:
    """
    Genereaza PDF D300 completat din continutul XML.
    Foloseste append pentru a pastra structura XFA originala.
    """
    converter = D300ToXFAConverter(xml_content)
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
        luna = root.get('luna', '00')
        an = root.get('an', '0000')
        attachment_name = f"D300_{an}_{luna}.xml"
        writer.add_attachment(attachment_name, xml_content)

    output_buffer = io.BytesIO()
    writer.write(output_buffer)
    output_buffer.seek(0)

    return output_buffer.getvalue()
