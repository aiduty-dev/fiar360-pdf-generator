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

        # Butoane - structura conform XFA validat
        xfa.append('<btnDoc>')
        xfa.append('<btnSalt/>')
        xfa.append('</btnDoc>')

        # Antet - structura conform XFA validat
        xfa.append('<Antet>')
        xfa.append('<IdDoc>')
        xfa.append(self.xml_tag('universalCode', 'D300_A11.0.7'))
        xfa.append(self.xml_tag('formValid', ''))
        xfa.append('</IdDoc>')

        xfa.append('<NumeDoc>')
        xfa.append('<Header xfa:dataNode="dataGroup"/>')
        xfa.append('</NumeDoc>')

        # nr_evid direct sub Antet, nu in IdDoc
        xfa.append(self.xml_tag('nr_evid', nr_evid))

        xfa.append('<opInterne>')
        xfa.append(self.xml_tag('mtdSimplificata', bifa_interne))
        xfa.append('</opInterne>')

        # metaDate - ordinea conform XFA validat
        xfa.append('<metaDate>')
        xfa.append(self.xml_tag('an_r', an))
        xfa.append(self.xml_tag('totalPlata_A', totalPlata_A))
        xfa.append(self.xml_tag('tipDecont', tip_decont))
        xfa.append(self.xml_tag('luna_r', luna))
        xfa.append('<perioada>')
        xfa.append('<dataInceput/>')
        xfa.append('<dataSfarsit/>')
        xfa.append('</perioada>')
        xfa.append(self.xml_tag('d_rez', '0'))
        xfa.append(self.xml_tag('d_scc', '0'))
        xfa.append(self.xml_tag('d_rec', d_rec))
        xfa.append('</metaDate>')

        # Temei legal - gol conform formularului validat
        xfa.append('<temeiLegal/>')

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
        # Strip spaces from IBAN for validation (both regular and non-breaking)
        iban_clean = cont.replace(' ', '').replace('\u00a0', '') if cont else ''
        xfa.append(self.xml_tag('iban', iban_clean))
        xfa.append('</banca>')

        # CAEN - caen1 contine codul, Caen e doar container
        xfa.append('<caen/>')
        xfa.append(self.xml_tag('caen1', caen))
        xfa.append('<Caen><Gap xfa:dataNode="dataGroup"/></Caen>')

        # proRata direct sub identifCntr - format cu zecimale
        pro_rata_formatted = f"{float(pro_rata):.2f}" if pro_rata else "0.00"
        xfa.append(self.xml_tag('proRata', pro_rata_formatted))

        xfa.append('</identifCntr>')

        # Date - sectiunile cu randuri
        xfa.append('<date>')

        # Comert - r1 la r8 (cu subrânduri r3_1, r5_1, r7_1)
        xfa.append('<comert>')
        comert_rows = [1, 2, 3, '3_1', 4, 5, '5_1', 6, 7, '7_1', 8]
        for r in comert_rows:
            xfa.append(f'<r{r}>')
            xfa.append(self.xml_tag('nrCrt', str(r).replace('_', '.')))
            xfa.append(self.xml_tag('c1', ''))  # Descrierea e in template
            xfa.append(self.xml_tag('c2', rows.get(f'R{str(r).replace("_", "")}_1', '')))
            xfa.append(self.xml_tag('c3', rows.get(f'R{str(r).replace("_", "")}_2', '')))
            xfa.append(f'</r{r}>')
        xfa.append('</comert>')

        # Livrari - r9 la r19 (cu subrânduri)
        # r17 si r18 nu au c1 conform XFA validat
        xfa.append('<livrari>')
        livrari_rows = [9, '9_1', 10, '10_1', 11, '11_1', 12, '12_1', '12_2', '12_3', '12_4', '12_5', 13, 14, 15, 16, 17, 18, 19]
        rows_without_c1 = [17, 18]
        for r in livrari_rows:
            r_key = str(r).replace('_', '')
            xfa.append(f'<r{r}>')
            xfa.append(self.xml_tag('nrCrt', str(r).replace('_', '.')))
            if r not in rows_without_c1:
                xfa.append(self.xml_tag('c1', ''))
            xfa.append(self.xml_tag('c2', rows.get(f'R{r_key}_1', '')))
            xfa.append(self.xml_tag('c3', rows.get(f'R{r_key}_2', '')))
            xfa.append(f'</r{r}>')
        xfa.append('</livrari>')

        # Achizitii RO - r20 la r23 (cu subrânduri)
        xfa.append('<achizitiiRO>')
        achizitiiRO_rows = [20, '20_1', 21, 22, '22_1', 23]
        for r in achizitiiRO_rows:
            r_key = str(r).replace('_', '')
            xfa.append(f'<r{r}>')
            xfa.append(self.xml_tag('nrCrt', str(r).replace('_', '.')))
            xfa.append(self.xml_tag('c1', ''))
            xfa.append(self.xml_tag('c2', rows.get(f'R{r_key}_1', '')))
            xfa.append(self.xml_tag('c3', rows.get(f'R{r_key}_2', '')))
            xfa.append(f'</r{r}>')
        xfa.append('</achizitiiRO>')

        # Achizitii IMP - r24 la r36 (cu subrânduri) - acestea sunt obligatorii cu 0!
        xfa.append('<achizitiiIMP>')
        achizitiiIMP_rows = [
            24, '24_1', 25, '25_1', 26,
            27, '27_1', '27_2', '27_3', '27_4', '27_5',
            28, 29, 30, '30_1', 31, 32, 33, 34, 35, 36
        ]
        # Rânduri care necesită valoare 0 implicit pentru validare
        rows_need_zero = ['24', '241', '25', '251', '26', '30', '301', '31']
        for r in achizitiiIMP_rows:
            r_key = str(r).replace('_', '')
            xfa.append(f'<r{r}>')
            xfa.append(self.xml_tag('nrCrt', str(r).replace('_', '.')))
            xfa.append(self.xml_tag('c1', ''))
            # Pentru rândurile obligatorii, punem 0 dacă nu există valoare
            c2_val = rows.get(f'R{r_key}_1', '')
            c3_val = rows.get(f'R{r_key}_2', '')
            if r_key in rows_need_zero:
                c2_val = c2_val if c2_val else '0'
                c3_val = c3_val if c3_val else '0'
            xfa.append(self.xml_tag('c2', c2_val))
            xfa.append(self.xml_tag('c3', c3_val))
            xfa.append(f'</r{r}>')
        xfa.append('</achizitiiIMP>')

        # Regularizari - r37 la r46
        xfa.append('<regularizari>')
        for r in range(37, 47):
            xfa.append(f'<r{r}>')
            xfa.append(self.xml_tag('nrCrt', str(r)))
            xfa.append(self.xml_tag('c1', ''))
            # Regularizari folosesc c3 pentru valori, nu c2
            xfa.append(self.xml_tag('c3', rows.get(f'R{r}_2', '')))
            xfa.append(f'</r{r}>')
        xfa.append('</regularizari>')

        # Bife - structura conform XFA validat
        xfa.append('<bife>')
        xfa.append('<caption>')
        xfa.append(self.xml_tag('bifa_cereale', bifa_cereale))
        xfa.append(self.xml_tag('bifa_mob', bifa_mob))
        xfa.append(self.xml_tag('bifa_disp', bifa_disp))
        xfa.append(self.xml_tag('bifa_cons', bifa_cons))
        xfa.append('</caption>')
        xfa.append('</bife>')

        # Rambursare - bifa e in rambursare, r47-r49 sunt afara
        xfa.append('<rambursare>')
        xfa.append(self.xml_tag('bifa_rambursare', solicit_ramb))
        xfa.append('</rambursare>')
        xfa.append('<r47>')
        xfa.append(self.xml_tag('c1', ''))
        xfa.append(self.xml_tag('c2', ''))
        xfa.append(self.xml_tag('c3', ''))
        xfa.append('</r47>')
        xfa.append('<r48>')
        xfa.append(self.xml_tag('c1', ''))
        xfa.append(self.xml_tag('c2', ''))
        xfa.append(self.xml_tag('c3', ''))
        xfa.append('</r48>')
        xfa.append('<r49>')
        xfa.append(self.xml_tag('c1', ''))
        xfa.append(self.xml_tag('c2', ''))
        xfa.append(self.xml_tag('c3', ''))
        xfa.append('</r49>')

        # Nedeductibil - r50, r50_1, r60, r60_1
        xfa.append('<nedeductibil>')
        xfa.append('<r50>')
        xfa.append(self.xml_tag('nrCrt', 'A'))
        xfa.append(self.xml_tag('c1', ''))
        xfa.append(self.xml_tag('c2', ''))
        xfa.append(self.xml_tag('c3', ''))
        xfa.append('</r50>')
        xfa.append('<r50_1>')
        xfa.append(self.xml_tag('nrCrt', 'A1'))
        xfa.append(self.xml_tag('c1', ''))
        xfa.append(self.xml_tag('c2', ''))
        xfa.append(self.xml_tag('c3', ''))
        xfa.append('</r50_1>')
        xfa.append('<r60>')
        xfa.append(self.xml_tag('nrCrt', 'B'))
        xfa.append(self.xml_tag('c1', ''))
        xfa.append(self.xml_tag('c2', ''))
        xfa.append(self.xml_tag('c3', ''))
        xfa.append('</r60>')
        xfa.append('<r60_1>')
        xfa.append(self.xml_tag('nrCrt', 'B1'))
        xfa.append(self.xml_tag('c1', ''))
        xfa.append(self.xml_tag('c2', ''))
        xfa.append(self.xml_tag('c3', ''))
        xfa.append('</r60_1>')
        xfa.append('</nedeductibil>')

        xfa.append('<alteInfo><r50><c1/><c2/></r50></alteInfo>')

        xfa.append('</date>')

        # Semnatura - ordinea conform XFA validat: prenume, nume, smnFnc
        xfa.append('<semnatura>')
        xfa.append(self.xml_tag('prenume', self.remove_diacritics(prenume_declar)))
        xfa.append(self.xml_tag('nume', self.remove_diacritics(nume_declar)))
        xfa.append(self.xml_tag('smnFnc', self.remove_diacritics(functie_declar)))
        xfa.append('</semnatura>')

        # locOF - structura conform XFA validat
        xfa.append('<locOF>')
        xfa.append('<TextField1/>')
        xfa.append('<TextField2/>')
        xfa.append('</locOF>')

        xfa.append('</form1>')
        xfa.append('</xfa:data>')
        xfa.append('</xfa:datasets>')

        # Formatare cu newlines ca in PDF-ul validat de Adobe
        xfa_str = ''.join(xfa)
        # Adaugam newline dupa fiecare tag inchis
        xfa_str = xfa_str.replace('><', '>\n<')
        return xfa_str


def generate_d300_pdf(xml_content: bytes, pdf_template_path: str, attach_xml: bool = True) -> bytes:
    """
    Genereaza PDF D300 completat din continutul XML.
    Foloseste incremental updates pentru a pastra semnatura Adobe Reader Extensions (UR3)
    care permite functionarea butonului 'VALIDEAZA FORMULARUL'.
    """
    from .pdf_incremental import create_incremental_xfa_update

    converter = D300ToXFAConverter(xml_content)
    xfa_datasets = converter.generate_xfa_datasets()

    # Citim template-ul original
    with open(pdf_template_path, 'rb') as f:
        pdf_bytes = f.read()

    # Folosim incremental update pentru a pastra semnatura UR3
    # Datasets stream este object 5 in template-ul D300
    result_pdf = create_incremental_xfa_update(pdf_bytes, xfa_datasets, datasets_obj_num=5)

    # Nota: attach_xml nu mai functioneaza cu incremental updates
    # deoarece ar necesita modificarea structurii PDF-ului
    # XML-ul original poate fi trimis separat daca e necesar

    return result_pdf
