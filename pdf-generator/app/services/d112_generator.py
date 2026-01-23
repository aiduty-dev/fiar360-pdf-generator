# -*- coding: utf-8 -*-
"""
D112 PDF Generator Service
Converteste XML ANAF in format XFA si genereaza PDF completat.
"""

import io
import os
from xml.etree import ElementTree as ET
from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject, NumberObject


class ANAFToXFAConverter:
    """Converteste XML ANAF in format XFA pentru PDF D112"""

    CASA_MAPPING = {
        'CT': 'CONSTANTA', '_B': 'BUCURESTI', 'B': 'BUCURESTI',
        'AB': 'ALBA', 'AR': 'ARAD', 'AG': 'ARGES', 'BC': 'BACAU',
        'BH': 'BIHOR', 'BN': 'BISTRITA-NASAUD', 'BT': 'BOTOSANI',
        'BV': 'BRASOV', 'BR': 'BRAILA', 'BZ': 'BUZAU', 'CS': 'CARAS-SEVERIN',
        'CL': 'CALARASI', 'CJ': 'CLUJ', 'CV': 'COVASNA', 'DB': 'DAMBOVITA',
        'DJ': 'DOLJ', 'GL': 'GALATI', 'GR': 'GIURGIU', 'GJ': 'GORJ',
        'HR': 'HARGHITA', 'HD': 'HUNEDOARA', 'IL': 'IALOMITA', 'IS': 'IASI',
        'IF': 'ILFOV', 'MM': 'MARAMURES', 'MH': 'MEHEDINTI', 'MS': 'MURES',
        'NT': 'NEAMT', 'OT': 'OLT', 'PH': 'PRAHOVA', 'SM': 'SATU MARE',
        'SJ': 'SALAJ', 'SB': 'SIBIU', 'SV': 'SUCEAVA', 'TR': 'TELEORMAN',
        'TM': 'TIMIS', 'TL': 'TULCEA', 'VS': 'VASLUI', 'VL': 'VALCEA', 'VN': 'VRANCEA'
    }

    def __init__(self, xml_content: bytes):
        """Initializeaza converterul cu continutul XML"""
        self.root = ET.fromstring(xml_content)
        self.ns = {'anaf': 'mfp:anaf:dgti:declaratie_unica:declaratie:v7'}

    def get_attr(self, element, attr, default=''):
        if element is None:
            return default
        return element.get(attr, default) or default

    def find_element(self, parent, tag):
        elem = parent.find(f'anaf:{tag}', self.ns)
        if elem is None:
            elem = parent.find(tag)
        if elem is None:
            for child in parent:
                local_name = child.tag.split('}')[-1] if '}' in child.tag else child.tag
                if local_name == tag:
                    return child
        return elem

    def find_all_elements(self, parent, tag):
        results = []
        for child in parent:
            local_name = child.tag.split('}')[-1] if '}' in child.tag else child.tag
            if local_name == tag:
                results.append(child)
        return results

    def xml_tag(self, name, value, close=True):
        if value is None or value == '':
            return f'<{name}\n/>'
        if close:
            return f'<{name}\n>{value}</{name}\n>'
        return f'<{name}\n>{value}'

    def generate_xfa_datasets(self):
        """Genereaza XML-ul XFA datasets complet"""
        luna_r = self.root.get('luna_r', '')
        an_r = self.root.get('an_r', '')
        d_rec = self.root.get('d_rec', '0')
        nume_declar = self.root.get('nume_declar', '')
        prenume_declar = self.root.get('prenume_declar', '')
        functie_declar = self.root.get('functie_declar', '')

        angajator = self.find_element(self.root, 'angajator')

        cif = self.get_attr(angajator, 'cif')
        den = self.get_attr(angajator, 'den')
        adrSoc = self.get_attr(angajator, 'adrSoc')
        adrFisc = self.get_attr(angajator, 'adrFisc', adrSoc)
        telSoc = self.get_attr(angajator, 'telSoc')
        telFisc = self.get_attr(angajator, 'telFisc', telSoc)
        mailSoc = self.get_attr(angajator, 'mailSoc')
        mailFisc = self.get_attr(angajator, 'mailFisc', mailSoc)
        rgCom = self.get_attr(angajator, 'rgCom')
        caen = self.get_attr(angajator, 'caen')
        casaAng = self.get_attr(angajator, 'casaAng')
        datCAM = self.get_attr(angajator, 'datCAM', '1')
        totalPlata_A = self.get_attr(angajator, 'totalPlata_A', '0')

        angajatorB = self.find_element(angajator, 'angajatorB') if angajator is not None else None
        B_cnp = self.get_attr(angajatorB, 'B_cnp', '0')
        B_sanatate = self.get_attr(angajatorB, 'B_sanatate', '0')
        B_pensie = self.get_attr(angajatorB, 'B_pensie', '0')
        B_brutSalarii = self.get_attr(angajatorB, 'B_brutSalarii', '0')
        B_sal = self.get_attr(angajatorB, 'B_sal', '0')

        angajatorC1 = self.find_element(angajator, 'angajatorC1') if angajator is not None else None
        C1_11 = self.get_attr(angajatorC1, 'C1_11', '0')
        C1_12 = self.get_attr(angajatorC1, 'C1_12', '0')
        C1_21 = self.get_attr(angajatorC1, 'C1_21', '0')
        C1_22 = self.get_attr(angajatorC1, 'C1_22', '0')
        C1_31 = self.get_attr(angajatorC1, 'C1_31', '0')
        C1_32 = self.get_attr(angajatorC1, 'C1_32', '0')
        C1_T1 = self.get_attr(angajatorC1, 'C1_T1', '0')
        C1_T2 = self.get_attr(angajatorC1, 'C1_T2', '0')
        C1_T3 = self.get_attr(angajatorC1, 'C1_T3', '0')
        C1_7 = self.get_attr(angajatorC1, 'C1_7', '0')

        angajatorC4 = self.find_element(angajator, 'angajatorC4') if angajator is not None else None
        C4_baza = self.get_attr(angajatorC4, 'C4_baza', '0')
        C4_ct = self.get_attr(angajatorC4, 'C4_ct', '0')

        angajatorF1 = self.find_element(angajator, 'angajatorF1') if angajator is not None else None
        F1_suma = self.get_attr(angajatorF1, 'F1_suma', '0')
        F1_suma_ded = self.get_attr(angajatorF1, 'F1_suma_ded', '0')
        F1_suma_scut = self.get_attr(angajatorF1, 'F1_suma_scut', '0')
        F1_deplata = self.get_attr(angajatorF1, 'F1_deplata', '0')

        angajatorA_list = self.find_all_elements(angajator, 'angajatorA') if angajator is not None else []
        asigurati = self.find_all_elements(self.root, 'asigurat')

        xfa = []
        xfa.append('\n<xfa:datasets xmlns:xfa="http://www.xfa.org/schema/xfa-data/1.0/"\n>')
        xfa.append('<xfa:data\n>')
        xfa.append('<frmMAIN\n>')
        xfa.append('<sbfrmPage1Ang\n>')

        xfa.append('<sfmIdentif\n>')
        xfa.append(self.xml_tag('d_rec', d_rec))
        xfa.append(self.xml_tag('tip_rec', ''))
        xfa.append(self.xml_tag('d_rec0', d_rec))
        xfa.append(self.xml_tag('luna_r', luna_r))
        xfa.append(self.xml_tag('an_r', an_r))
        xfa.append(self.xml_tag('den', den))
        xfa.append(self.xml_tag('adrFisc', adrFisc))
        xfa.append(self.xml_tag('telFis', telFisc))
        xfa.append(self.xml_tag('faxFisc', ''))
        xfa.append(self.xml_tag('mailFisc', mailFisc))
        xfa.append(self.xml_tag('dat', '1'))
        xfa.append(self.xml_tag('tRisc', '0.000'))
        xfa.append(self.xml_tag('caen', caen))
        xfa.append(self.xml_tag('cif', cif))
        xfa.append(self.xml_tag('telFisc', telFisc))
        xfa.append(self.xml_tag('RO', 'RO'))
        xfa.append(self.xml_tag('Bifa_FdGar', '1'))
        xfa.append(self.xml_tag('caen1', ''))
        xfa.append(self.xml_tag('datCAM', datCAM))
        xfa.append(self.xml_tag('Bifa_UM', '0'))
        xfa.append(self.xml_tag('art90', '0'))
        xfa.append(self.xml_tag('cifS', ''))
        xfa.append(self.xml_tag('data1', ''))
        xfa.append(self.xml_tag('data2', ''))
        xfa.append(self.xml_tag('d_caen', '1'))
        xfa.append('</sfmIdentif\n>')

        if angajatorA_list:
            first_a = angajatorA_list[0]
            xfa.append('<sfmSectAVal\n>')
            xfa.append(self.xml_tag('nrcrt', '1'))
            xfa.append(self.xml_tag('A_codOblig', self.get_attr(first_a, 'A_codOblig')))
            xfa.append(self.xml_tag('codbuget', self.get_attr(first_a, 'A_codBugetar')))
            xfa.append(self.xml_tag('a_datorat', self.get_attr(first_a, 'A_datorat', '0')))
            xfa.append(self.xml_tag('a_deductibil', self.get_attr(first_a, 'A_deductibil', '0')))
            xfa.append(self.xml_tag('a_scutit', self.get_attr(first_a, 'A_scutit', '0')))
            xfa.append(self.xml_tag('a_plata', self.get_attr(first_a, 'A_plata', '0')))
            xfa.append('</sfmSectAVal\n>')

        xfa.append('<sfmSectATotal\n>')
        xfa.append(self.xml_tag('totalPlata_A', totalPlata_A))
        xfa.append('</sfmSectATotal\n>')

        xfa.append('<sbfrmFooter\n>')
        xfa.append(self.xml_tag('Nr_inreg', ''))
        xfa.append(self.xml_tag('Data_inreg', ''))
        xfa.append(self.xml_tag('nume_declar', nume_declar))
        xfa.append(self.xml_tag('functie_declar', functie_declar))
        xfa.append(self.xml_tag('prenume_declar', prenume_declar))
        xfa.append('</sbfrmFooter\n>')

        xfa.append('<sfmIdentif2\n>')
        xfa.append(self.xml_tag('rgCom', rgCom))
        xfa.append(self.xml_tag('adrSoc', adrSoc))
        xfa.append(self.xml_tag('telSoc', telSoc))
        xfa.append(self.xml_tag('faxSoc', ''))
        xfa.append(self.xml_tag('mailSoc', mailSoc))
        xfa.append(self.xml_tag('casaAng', casaAng))
        xfa.append(self.xml_tag('tRisc', '0.000'))
        xfa.append(self.xml_tag('caen', caen))
        xfa.append(self.xml_tag('datCAM', datCAM))
        xfa.append('</sfmIdentif2\n>')

        xfa.append('<sfmSectB\n>')
        xfa.append(self.xml_tag('B_cnp', B_cnp))
        xfa.append(self.xml_tag('B_sanatate', B_sanatate))
        xfa.append(self.xml_tag('B_pensie', B_pensie))
        xfa.append(self.xml_tag('B1_brut_salarii', B_brutSalarii))
        xfa.append(self.xml_tag('B_sal', B_sal))
        xfa.append(self.xml_tag('T1', B_cnp))
        xfa.append(self.xml_tag('T4', B_sanatate))
        xfa.append(self.xml_tag('T2', '0'))
        xfa.append(self.xml_tag('T3', '0'))
        xfa.append(self.xml_tag('nrSal1_111', ''))
        xfa.append(self.xml_tag('nrSal2_111', ''))
        xfa.append(self.xml_tag('bazaCAS_111', ''))
        xfa.append(self.xml_tag('CAS_111', ''))
        xfa.append(self.xml_tag('nrSal3_111', ''))
        xfa.append('</sfmSectB\n>')

        xfa.append('<sbfrmSectiuneaC\n>')
        xfa.append('<sfmSectC1\n>')
        xfa.append(self.xml_tag('c1_11', C1_11))
        xfa.append(self.xml_tag('c1_21', C1_21))
        xfa.append(self.xml_tag('c1_31', C1_31))
        xfa.append(self.xml_tag('c1_t1', C1_T1))
        xfa.append(self.xml_tag('c1_12', C1_12))
        xfa.append(self.xml_tag('c1_22', C1_22))
        xfa.append(self.xml_tag('c1_32', C1_32))
        xfa.append(self.xml_tag('c1_t2', C1_T2))
        xfa.append(self.xml_tag('c1_6', '0'))
        xfa.append(self.xml_tag('c1_sp', '0'))
        xfa.append(self.xml_tag('c1_t3', C1_T3))
        xfa.append(self.xml_tag('c1_7', C1_7))
        xfa.append(self.xml_tag('c1_t', '0'))
        xfa.append(self.xml_tag('c1_T1', C1_T1))
        xfa.append(self.xml_tag('c1_T2', C1_T2))
        xfa.append(self.xml_tag('c1_T3', C1_T3))
        xfa.append(self.xml_tag('c1_T', ''))
        xfa.append(self.xml_tag('c1_5', ''))
        xfa.append(self.xml_tag('c1_33', ''))
        xfa.append(self.xml_tag('c1_23', ''))
        xfa.append(self.xml_tag('c1_13', ''))
        xfa.append('</sfmSectC1\n>')

        xfa.append('<sfmSectC2\n>')
        for field in ['c2_11', 'c2_12', 'c2_13', 'c2_24', 'c2_34', 'c2_44', 'c2_54',
                      'c2_22', 'c2_32', 'c2_42', 'c2_52', 'c2_21', 'c2_31', 'c2_41',
                      'c2_51', 'c2_15', 'c2_16', 'c2_26', 'c2_36', 'c2_46', 'c2_56',
                      'c2_T6', 'c2_7', 'c2_8', 'c2_9', 'c2_10', 'c2_110', 'c2_120',
                      'c2_130', 'c2_14', 'c2_140', 'c2_25', 'c2_23']:
            xfa.append(self.xml_tag(field, '0'))
        xfa.append('</sfmSectC2\n>')

        xfa.append('<sbfrmC345\n>')
        xfa.append(self.xml_tag('c3_Suma', '0'))
        xfa.append(self.xml_tag('c3_Total', '0'))
        for field in ['c3_44', 'c3_43', 'c3_42', 'c3_41', 'c3_34', 'c3_33', 'c3_32',
                      'c3_31', 'c3_24', 'c3_23', 'c3_22', 'c3_21', 'c3_11', 'c3_12',
                      'c3_13', 'c3_14', 'C4_scutita_so']:
            xfa.append(self.xml_tag(field, '0'))
        xfa.append(self.xml_tag('C4_baza', C4_baza))
        xfa.append(self.xml_tag('C4_ct', C4_ct))
        xfa.append(self.xml_tag('C5_baza', '0'))
        xfa.append(self.xml_tag('C5_ct', '0'))
        xfa.append(self.xml_tag('CAM_constr', ''))
        xfa.append('</sbfrmC345\n>')

        xfa.append('<sbfrmC6\n>')
        xfa.append(self.xml_tag('C6_baza', '0'))
        xfa.append(self.xml_tag('C6_ct', '0'))
        xfa.append('</sbfrmC6\n>')

        xfa.append('<sbfrmC7\n>')
        xfa.append(self.xml_tag('C7_baza', '0'))
        xfa.append(self.xml_tag('C7_ct', '0'))
        xfa.append('</sbfrmC7\n>')
        xfa.append('</sbfrmSectiuneaC\n>')

        xfa.append('<sbfrmSectiuneaD\n>')
        xfa.append(self.xml_tag('D1', '0'))
        xfa.append(self.xml_tag('D2', '0'))
        xfa.append(self.xml_tag('D3', '0.00'))
        xfa.append(self.xml_tag('D4', '0'))
        xfa.append('</sbfrmSectiuneaD\n>')

        xfa.append('<sbfrmSectiuneaE\n>')
        for field in ['E1_venit', 'E1_baza', 'E1_ct', 'E_Aj_nr', 'E_Aj_suma',
                      'E2_11', 'E2_12', 'E2_14', 'E2_16', 'E2_21', 'E2_22', 'E2_24', 'E2_26',
                      'E2_41', 'E2_42', 'E2_44', 'E2_46', 'E2_51', 'E2_52', 'E2_54', 'E2_56', 'E2_66']:
            xfa.append(self.xml_tag(field, '0'))
        xfa.append(self.xml_tag('E3_total', '0'))
        xfa.append(self.xml_tag('E3_suma', '0'))
        xfa.append(self.xml_tag('E2_140', '0'))
        xfa.append(self.xml_tag('E2_10', '0'))
        xfa.append('</sbfrmSectiuneaE\n>')

        xfa.append('<sbfrmSectiuneaF\n>')
        xfa.append('<sbfrmF1\n>')
        xfa.append(self.xml_tag('F1_suma', F1_suma))
        xfa.append(self.xml_tag('F1_suma_ded', F1_suma_ded))
        xfa.append(self.xml_tag('F1_suma_scut', F1_suma_scut))
        xfa.append(self.xml_tag('F1_deplata', F1_deplata))
        xfa.append(self.xml_tag('F12_suma', F1_suma))
        xfa.append(self.xml_tag('F12_suma_ded', F1_suma_ded))
        xfa.append(self.xml_tag('F12_suma_scut', F1_suma_scut))
        xfa.append(self.xml_tag('F12_deplata', F1_deplata))
        xfa.append('</sbfrmF1\n>')
        xfa.append('<sbfrmF2 xfa:dataNode="dataGroup"\n/>')
        xfa.append('<sbfrmF2btn\n>')
        xfa.append(self.xml_tag('tot_F2_suma', '0'))
        xfa.append(self.xml_tag('tot_F2_suma_ded', '0'))
        xfa.append(self.xml_tag('tot_F2_suma_scut', '0'))
        xfa.append(self.xml_tag('tot_F2_deplata', '0'))
        xfa.append('</sbfrmF2btn\n>')
        xfa.append('</sbfrmSectiuneaF\n>')

        xfa.append('<sbfrmSectiuneaG\n/>')
        xfa.append('<calcule1\n/>')
        xfa.append('<Salt xfa:dataNode="dataGroup"\n/>')
        xfa.append('<sfmSectAEtich xfa:dataNode="dataGroup"\n/>')
        xfa.append('<sbfrmPrezenta\n>')
        xfa.append('<Salt1 xfa:dataNode="dataGroup"\n/>')
        xfa.append('</sbfrmPrezenta\n>')
        xfa.append('<sbfrMesajFooter xfa:dataNode="dataGroup"\n/>')
        xfa.append('<sfmAnexa12 xfa:dataNode="dataGroup"\n/>')

        for idx, ang_a in enumerate(angajatorA_list[1:], start=2):
            xfa.append('<sfmSectAVal\n>')
            xfa.append(self.xml_tag('nrcrt', str(idx)))
            xfa.append(self.xml_tag('A_codOblig', self.get_attr(ang_a, 'A_codOblig')))
            xfa.append(self.xml_tag('codbuget', self.get_attr(ang_a, 'A_codBugetar')))
            xfa.append(self.xml_tag('a_datorat', self.get_attr(ang_a, 'A_datorat', '0')))
            xfa.append(self.xml_tag('a_deductibil', self.get_attr(ang_a, 'A_deductibil', '')))
            xfa.append(self.xml_tag('a_scutit', self.get_attr(ang_a, 'A_scutit', '0')))
            xfa.append(self.xml_tag('a_plata', self.get_attr(ang_a, 'A_plata', '0')))
            xfa.append('</sfmSectAVal\n>')

        xfa.append('</sbfrmPage1Ang\n>')

        for asig in asigurati:
            xfa.append(self._generate_asigurat_xfa(asig, luna_r, an_r))

        xfa.append('<Variabile\n>')
        xfa.append(self.xml_tag('tfNZL', '20'))
        xfa.append(self.xml_tag('S_plcomp', '0'))
        xfa.append(self.xml_tag('S_oug85', '0'))
        xfa.append(self.xml_tag('tfNZC', '31'))
        xfa.append('</Variabile\n>')

        xfa.append('<sbfrmAntetAng xfa:dataNode="dataGroup"\n/>')
        xfa.append('<sbfrmAntetAsig xfa:dataNode="dataGroup"\n/>')
        xfa.append(self.xml_tag('universalCode', 'D112_A7.2.4'))
        xfa.append('<sbfrmddl\n>')
        xfa.append(self.xml_tag('ddl', ''))
        xfa.append('</sbfrmddl\n>')

        xfa.append('</frmMAIN\n>')
        xfa.append('</xfa:data\n>')
        xfa.append('</xfa:datasets\n>')

        return ''.join(xfa)

    def _generate_asigurat_xfa(self, asig, luna_r, an_r):
        """Genereaza XFA pentru un asigurat"""
        xfa = []

        cnpAsig = self.get_attr(asig, 'cnpAsig')
        numeAsig = self.get_attr(asig, 'numeAsig')
        prenAsig = self.get_attr(asig, 'prenAsig')
        dataAng = self.get_attr(asig, 'dataAng')
        casaSn = self.get_attr(asig, 'casaSn')
        idAsig = self.get_attr(asig, 'idAsig', '1')
        asigCI = self.get_attr(asig, 'asigCI', '1')
        asigSO = self.get_attr(asig, 'asigSO', '1')
        asigExc = self.get_attr(asig, 'asigExc', '0')
        Timp_E3 = self.get_attr(asig, 'Timp_E3', '0')

        asiguratA = self.find_element(asig, 'asiguratA')
        A_1 = self.get_attr(asiguratA, 'A_1', '1')
        A_2 = self.get_attr(asiguratA, 'A_2', '0')
        A_3 = self.get_attr(asiguratA, 'A_3', 'N')
        A_4 = self.get_attr(asiguratA, 'A_4', '8')
        A_5 = self.get_attr(asiguratA, 'A_5', '0')
        A_6 = self.get_attr(asiguratA, 'A_6', '0')
        A_7 = self.get_attr(asiguratA, 'A_7', '0')
        A_8 = self.get_attr(asiguratA, 'A_8', '0')
        A_9 = self.get_attr(asiguratA, 'A_9', '0')
        A_11 = self.get_attr(asiguratA, 'A_11', '0')
        A_12 = self.get_attr(asiguratA, 'A_12', '0')
        A_13 = self.get_attr(asiguratA, 'A_13', '0')
        A_14 = self.get_attr(asiguratA, 'A_14', '0')
        A_sal1 = self.get_attr(asiguratA, 'A_sal1', '0')
        A_sal2 = self.get_attr(asiguratA, 'A_sal2', '0')
        A_11P = self.get_attr(asiguratA, 'A_11P', '0')
        A_12P = self.get_attr(asiguratA, 'A_12P', '0')
        A_13P = self.get_attr(asiguratA, 'A_13P', '0')
        A_14P = self.get_attr(asiguratA, 'A_14P', '0')
        A_12D = self.get_attr(asiguratA, 'A_12D', '')
        A_14D = self.get_attr(asiguratA, 'A_14D', '')
        A_13S = self.get_attr(asiguratA, 'A_13S', '0')
        A_13C = self.get_attr(asiguratA, 'A_13C', '0')

        asiguratE1 = self.find_element(asig, 'asiguratE1')
        E1_1 = self.get_attr(asiguratE1, 'E1_1', '0')
        E1_2 = self.get_attr(asiguratE1, 'E1_2', '0')
        E1_3 = self.get_attr(asiguratE1, 'E1_3', '0')
        E1_4 = self.get_attr(asiguratE1, 'E1_4', '0')
        E1_41 = self.get_attr(asiguratE1, 'E1_41', '0')
        E1_42 = self.get_attr(asiguratE1, 'E1_42', '0')
        E1_421 = self.get_attr(asiguratE1, 'E1_421', '0')
        E1_422 = self.get_attr(asiguratE1, 'E1_422', '0')
        E1_5 = self.get_attr(asiguratE1, 'E1_5', '0')
        E1_6 = self.get_attr(asiguratE1, 'E1_6', '0')
        E1_7 = self.get_attr(asiguratE1, 'E1_7', '0')

        asiguratE3 = self.find_element(asig, 'asiguratE3')
        E3_1 = self.get_attr(asiguratE3, 'E3_1', 'A')
        E3_2 = self.get_attr(asiguratE3, 'E3_2', '1')
        E3_3 = self.get_attr(asiguratE3, 'E3_3', '1')
        E3_4 = self.get_attr(asiguratE3, 'E3_4', 'P')
        E3_8 = self.get_attr(asiguratE3, 'E3_8', '0')
        E3_9 = self.get_attr(asiguratE3, 'E3_9', '0')
        E3_11 = self.get_attr(asiguratE3, 'E3_11', '0')
        E3_12 = self.get_attr(asiguratE3, 'E3_12', '0')
        E3_121 = self.get_attr(asiguratE3, 'E3_121', '0')
        E3_122 = self.get_attr(asiguratE3, 'E3_122', '0')
        E3_1221 = self.get_attr(asiguratE3, 'E3_1221', '0')
        E3_1222 = self.get_attr(asiguratE3, 'E3_1222', '0')
        E3_13 = self.get_attr(asiguratE3, 'E3_13', '0')
        E3_14 = self.get_attr(asiguratE3, 'E3_14', '0')
        E3_15 = self.get_attr(asiguratE3, 'E3_15', '0')
        E3_16 = self.get_attr(asiguratE3, 'E3_16', '0')
        E3_19 = self.get_attr(asiguratE3, 'E3_19', '0')
        E3_52 = self.get_attr(asiguratE3, 'E3_52', '0')
        E3_54 = self.get_attr(asiguratE3, 'E3_54', '0')
        E3_58 = self.get_attr(asiguratE3, 'E3_58', '0')
        E3_59 = self.get_attr(asiguratE3, 'E3_59', '0')
        E3_60 = self.get_attr(asiguratE3, 'E3_60', '0')
        E3_61 = self.get_attr(asiguratE3, 'E3_61', '0')
        E3_62 = self.get_attr(asiguratE3, 'E3_62', '0')
        E3_64 = self.get_attr(asiguratE3, 'E3_64', '0')
        E3_67 = self.get_attr(asiguratE3, 'E3_67', '0')
        E3_69 = self.get_attr(asiguratE3, 'E3_69', '0')
        E3_71 = self.get_attr(asiguratE3, 'E3_71', '0')
        E3_90 = self.get_attr(asiguratE3, 'E3_90', '0')

        VB_A = E3_8 if E3_8 != '0' else A_13C if A_13C != '0' else A_13
        tichete_A = A_13S if A_13S != '0' else '0'

        sel1_msg = f"Ati selectat asigExc = '{asigExc}-{'nu e cazul' if asigExc == '0' else 'neexceptat'}' si bifa_IE = 0"

        xfa.append('<sbfrmPage1Asig\n>')

        xfa.append('<sfmDateIdentif\n>')
        xfa.append(self.xml_tag('cnp_asig', cnpAsig))
        xfa.append(self.xml_tag('Nume_asig', numeAsig))
        xfa.append(self.xml_tag('Pren_asig', prenAsig))
        xfa.append(self.xml_tag('Data_ang', dataAng))
        xfa.append(self.xml_tag('Casa_sn', casaSn))
        xfa.append(self.xml_tag('Cnp_ant', ''))
        xfa.append(self.xml_tag('Nume_ant', ''))
        xfa.append(self.xml_tag('Pre_ant', ''))
        xfa.append(self.xml_tag('Data_sf', ''))
        xfa.append(self.xml_tag('idAsig', idAsig))
        xfa.append(self.xml_tag('Asig_ci', asigCI))
        xfa.append(self.xml_tag('Asig_so', asigSO))
        xfa.append(self.xml_tag('asigScu', '0'))
        xfa.append(self.xml_tag('asigExc', asigExc))
        xfa.append(self.xml_tag('an_r', an_r))
        xfa.append(self.xml_tag('luna_r', luna_r))
        xfa.append(self.xml_tag('asigScu_rez', ''))
        xfa.append(self.xml_tag('cis_asig', ''))
        xfa.append(self.xml_tag('motivExc', ''))
        xfa.append(self.xml_tag('bifa_plataNerezident', '0'))
        xfa.append(self.xml_tag('bifa_Ucraina', '0'))
        xfa.append(self.xml_tag('bifa_IE', '0'))
        xfa.append(self.xml_tag('Exc7', ''))
        xfa.append('</sfmDateIdentif\n>')

        xfa.append('<coAsig\n/>')

        xfa.append('<sbfrmSectiuneaA\n>')
        xfa.append(self.xml_tag('A_1', A_1))
        xfa.append(self.xml_tag('A_sal1', A_sal1))
        xfa.append(self.xml_tag('A_sal2', A_sal2))
        xfa.append(self.xml_tag('A_2', A_2))
        xfa.append(self.xml_tag('A_3', A_3))
        xfa.append(self.xml_tag('A_4', A_4))
        xfa.append(self.xml_tag('A_6', A_6))
        xfa.append(self.xml_tag('A_7', A_7))
        xfa.append(self.xml_tag('A_8', A_8))
        xfa.append(self.xml_tag('A_9', A_9))
        xfa.append(self.xml_tag('A_10', A_sal1))
        xfa.append(self.xml_tag('A_11', A_11))
        xfa.append(self.xml_tag('A_12', A_12))
        xfa.append(self.xml_tag('A_13', A_13))
        xfa.append(self.xml_tag('A_14', A_14))
        xfa.append(self.xml_tag('A_13S', A_13S))
        xfa.append(self.xml_tag('A_13C', A_13C))
        xfa.append(self.xml_tag('A_20', A_5))
        xfa.append(self.xml_tag('A_5', A_5))
        xfa.append(self.xml_tag('Asig_ci', asigCI))
        xfa.append(self.xml_tag('Asig_so', asigSO))
        xfa.append(self.xml_tag('asigScu', '0'))
        xfa.append(self.xml_tag('asigExc', asigExc))
        xfa.append(self.xml_tag('calc_aut', '0'))
        xfa.append(self.xml_tag('VB_A', VB_A))
        xfa.append(self.xml_tag('tichete_A', tichete_A))
        xfa.append(self.xml_tag('tichete1_A', tichete_A))
        xfa.append(self.xml_tag('tichete2_A', tichete_A))
        xfa.append(self.xml_tag('tichete3_A', '0'))
        xfa.append(self.xml_tag('A_8n', ''))
        xfa.append(self.xml_tag('sel1', sel1_msg))
        xfa.append(self.xml_tag('A_13P', A_13P))
        xfa.append(self.xml_tag('A_14P', A_14P))
        xfa.append(self.xml_tag('A_11P', A_11P))
        xfa.append(self.xml_tag('A_12P', A_12P))
        xfa.append(self.xml_tag('A_12D', A_12D))
        xfa.append(self.xml_tag('A_14D', A_14D))
        xfa.append(self.xml_tag('PT1', ''))
        xfa.append('</sbfrmSectiuneaA\n>')

        xfa.append('<sbfrmSectiuneaB\n>')
        xfa.append('<SbfrmSectiuneaB2\n>')
        for f in ['B2_1','B2_2','B2_3','B2_4','B2_5','B2_6','B2_7',
                  'B2_5P','B2_5S','B2_5C','B2_6P','B2_6S','B2_6C','B2_7P','B2_7S','B2_7C']:
            xfa.append(self.xml_tag(f, '0'))
        xfa.append('</SbfrmSectiuneaB2\n>')

        xfa.append('<sbfrmSectiuneaB3\n>')
        for f in ['B3_1','B3_2','B3_3','B3_4','B3_5','B3_6','B3_7','B3_8','B3_9',
                  'B3_10','B3_11','B3_12','B3_13','B3_6a']:
            xfa.append(self.xml_tag(f, '0'))
        xfa.append(self.xml_tag('B3_7S', ''))
        xfa.append(self.xml_tag('B3_7C', '0'))
        xfa.append(self.xml_tag('B3_CMS', '0'))
        xfa.append('</sbfrmSectiuneaB3\n>')

        xfa.append('<sbfrmSectiuneaB4\n>')
        for f in ['B4_1','B4_2','B4_3','B4_5','B4_6','B4_7','B4_8','B4_14']:
            xfa.append(self.xml_tag(f, '0'))
        if asigExc == '2':
            xfa.append(self.xml_tag('B4_7P', A_13P))
            xfa.append(self.xml_tag('B4_8P', A_14P))
            xfa.append(self.xml_tag('B4_5P', A_11P))
            xfa.append(self.xml_tag('B4_6P', A_12P))
            xfa.append(self.xml_tag('B4_8D', A_14P))
            xfa.append(self.xml_tag('B4_6D', A_12P))
        else:
            for f in ['B4_7P','B4_8P','B4_5P','B4_6P','B4_8D','B4_6D']:
                xfa.append(self.xml_tag(f, '0'))
        for f in ['B4_18','B4_20']:
            xfa.append(self.xml_tag(f, '0'))
        for f in ['B4_21','B4_23','B4_25','B4_27','B4_29','B4_30']:
            xfa.append(self.xml_tag(f, ''))
        xfa.append(self.xml_tag('sel1', sel1_msg))
        for f in ['B4_1n','B4_aj1','B4_aj2','B4_aj3','B4_aj4','B4_aj5','B4_22','B4_26',
                  'B4_17','B4_19','B4_24','B4_28','B4_7S']:
            xfa.append(self.xml_tag(f, '0'))
        for f in ['B4_5S','tip_8P','B4_7C','PT1']:
            xfa.append(self.xml_tag(f, ''))
        xfa.append('</sbfrmSectiuneaB4\n>')

        xfa.append(self.xml_tag('Asig_ci', asigCI))
        xfa.append(self.xml_tag('Asig_so', asigSO))
        xfa.append(self.xml_tag('asigScu', '0'))
        xfa.append(self.xml_tag('asigExc', asigExc))
        xfa.append(self.xml_tag('calc_aut', '0'))

        xfa.append('<sbfrmSectiuneaB1rep\n>')
        xfa.append('<sbfrmSectiuneaB1\n>')
        xfa.append(self.xml_tag('tfNrCrt', '1'))
        xfa.append(self.xml_tag('B1_1', '1'))
        for f in ['VB_B','tichete1_B','tichete2_B','tichete3_B','B1_sal1','B1_sal2','B1_2']:
            xfa.append(self.xml_tag(f, '0'))
        xfa.append(self.xml_tag('B1_3', 'N'))
        xfa.append(self.xml_tag('B1_4', '8'))
        xfa.append(self.xml_tag('B1_6', ''))
        xfa.append(self.xml_tag('B1_7', ''))
        for f in ['B1_8','B1_15']:
            xfa.append(self.xml_tag(f, '0'))
        xfa.append(self.xml_tag('B1_15n', ''))
        for f in ['B1_9','B1_5','B1_10']:
            xfa.append(self.xml_tag(f, '0'))
        xfa.append(self.xml_tag('B1_16', ''))
        xfa.append(self.xml_tag('B1_18', '0'))
        xfa.append(self.xml_tag('B1_17', ''))
        xfa.append('<adaug xfa:dataNode="dataGroup"\n/>')
        xfa.append('</sbfrmSectiuneaB1\n>')
        xfa.append('</sbfrmSectiuneaB1rep\n>')
        xfa.append('</sbfrmSectiuneaB\n>')

        xfa.append('<sbfrmSectiuneaC\n>')
        xfa.append(self.xml_tag('Asig_ci', '0'))
        xfa.append(self.xml_tag('Asig_so', '0'))
        xfa.append(self.xml_tag('asigScu', '0'))
        xfa.append('<SectiuneaC\n>')
        for f in ['C_1','C_2','C_3','C_4','C_5','C_6','C_7','C_8','C_9','C_10','C_11',
                  'C_17','C_18','C_19']:
            xfa.append(self.xml_tag(f, '0'))
        xfa.append(self.xml_tag('ID_C', '1'))
        for f in ['C_25','C_26','C_27','C_28','C_29']:
            xfa.append(self.xml_tag(f, '0'))
        xfa.append('</SectiuneaC\n>')
        xfa.append('</sbfrmSectiuneaC\n>')

        xfa.append('<sbfrmSectiuneaD\n>')
        xfa.append('<sfmButoane\n/>')
        xfa.append('<sbfrmSectiuneaDrep\n>')
        xfa.append(self.xml_tag('tfNrCrt', '1'))
        for f in ['Data_CMI','D_1','D_2','D_3','D_4','D_5','D_6','D_7','D_8','D_8a',
                  'D_9','D_10','D_11','D_12','D_13']:
            xfa.append(self.xml_tag(f, ''))
        for f in ['D_14','D_15','D_16','D_17','D_18']:
            xfa.append(self.xml_tag(f, '0'))
        xfa.append(self.xml_tag('D_19', ''))
        for f in ['D_20','D_21']:
            xfa.append(self.xml_tag(f, '0'))
        xfa.append(self.xml_tag('D_23', ''))
        for f in ['D_24','D_25','D_26','D_27']:
            xfa.append(self.xml_tag(f, '0'))
        xfa.append(self.xml_tag('D_28', ''))
        xfa.append('</sbfrmSectiuneaDrep\n>')
        xfa.append('</sbfrmSectiuneaD\n>')

        xfa.append('<sfmButoane\n>')
        xfa.append(self.xml_tag('rbl', '1'))
        xfa.append(self.xml_tag('tfNZL', '20'))
        xfa.append(self.xml_tag('flag', ''))
        xfa.append('<rbl2\n>')
        xfa.append(self.xml_tag('rbC', '0'))
        xfa.append(self.xml_tag('rbB', '0'))
        xfa.append(self.xml_tag('rbA', '1'))
        xfa.append('</rbl2\n>')
        xfa.append(self.xml_tag('sal1', '4050'))
        xfa.append(self.xml_tag('Sdimin', '300'))
        xfa.append(self.xml_tag('sal2', '4300'))
        xfa.append(self.xml_tag('flag1', 'visible'))
        xfa.append(self.xml_tag('sal3', '4582'))
        xfa.append('</sfmButoane\n>')

        xfa.append('<sbfrmSectiuneaE\n>')
        xfa.append(self.xml_tag('E1_1', E1_1))
        xfa.append(self.xml_tag('E1_2', E1_2))
        xfa.append(self.xml_tag('E1_3', E1_3))
        xfa.append(self.xml_tag('E1_4', E1_4))
        xfa.append(self.xml_tag('E1_41', E1_41))
        xfa.append(self.xml_tag('E1_42', E1_42))
        xfa.append(self.xml_tag('E1_421', E1_421))
        xfa.append(self.xml_tag('E1_422', E1_422))
        xfa.append(self.xml_tag('E1_5', E1_5))
        xfa.append(self.xml_tag('E1_6', E1_6))
        xfa.append(self.xml_tag('E1_7', E1_7))
        for f in ['E2_1','E2_2','E2_3','E2_4']:
            xfa.append(self.xml_tag(f, '0'))

        xfa.append('<sbfrmSectiuneaE3\n>')
        xfa.append(self.xml_tag('E3_1', E3_1))
        xfa.append(self.xml_tag('E3_2', E3_2))
        xfa.append(self.xml_tag('E3_3', E3_3))
        xfa.append(self.xml_tag('E3_4', E3_4))
        xfa.append(self.xml_tag('E3_9', E3_9))
        xfa.append(self.xml_tag('E3_52', E3_52))
        xfa.append(self.xml_tag('E3_54', E3_54))
        xfa.append(self.xml_tag('E3_59', E3_59))
        xfa.append(self.xml_tag('E3_62', E3_62))
        xfa.append(self.xml_tag('E3_64', E3_64))
        xfa.append(self.xml_tag('E3_60', E3_60))
        xfa.append(self.xml_tag('E3_61', E3_61))
        xfa.append(self.xml_tag('E3_67', E3_67))
        xfa.append(self.xml_tag('E3_71', E3_71))
        xfa.append(self.xml_tag('E3_58', E3_58))
        xfa.append(self.xml_tag('E3_69', E3_69))
        xfa.append(self.xml_tag('E3_90', E3_90))
        xfa.append(self.xml_tag('E3_8', E3_8))
        xfa.append(self.xml_tag('E3_11', E3_11))
        xfa.append(self.xml_tag('E3_12', E3_12))
        xfa.append(self.xml_tag('E3_121', E3_121))
        xfa.append(self.xml_tag('E3_122', E3_122))
        xfa.append(self.xml_tag('E3_1221', E3_1221))
        xfa.append(self.xml_tag('E3_1222', E3_1222))
        xfa.append(self.xml_tag('E3_13', E3_13))
        xfa.append(self.xml_tag('E3_14', E3_14))
        xfa.append(self.xml_tag('E3_15', E3_15))
        xfa.append(self.xml_tag('E3_16', E3_16))
        xfa.append(self.xml_tag('E3_17', '0'))
        xfa.append(self.xml_tag('E3_18', ''))
        xfa.append(self.xml_tag('E3_19', E3_19))
        xfa.append(self.xml_tag('ID_E', '1'))
        for f in ['E3_5','E3_6','E3_80','E3_81','E3_82','E3_83','E3_92','E3_93',
                  'E3_45','E3_46','E3_47','E3_48','E3_49','E3_7','E3_96','E3_53',
                  'E3_55','E3_85','E3_56','E3_10','E3_72','E3_73','E3_74','E3_75',
                  'E3_57','E3_44','E3_86','E3_87','E3_63','E3_65','E3_88','E3_66',
                  'E3_91','E3_77','E3_78','E3_68','E3_79','E3_94','E3_95','E3_20',
                  'E3_70','E3_23','E3_24','E3_27','E3_28','E3_31']:
            xfa.append(self.xml_tag(f, ''))
        xfa.append('<adaug xfa:dataNode="dataGroup"\n/>')
        for f in ['E3_40','E3_39','E3_38','E3_37']:
            xfa.append(self.xml_tag(f, ''))
        xfa.append('</sbfrmSectiuneaE3\n>')

        xfa.append('<sbfrmSectiuneaE4_c\n>')
        xfa.append(self.xml_tag('Tcota', '0.00'))
        xfa.append(self.xml_tag('Tsuma', '0'))
        xfa.append(self.xml_tag('Timp', Timp_E3))
        xfa.append('</sbfrmSectiuneaE4_c\n>')

        xfa.append('<sbfrmSectiuneaE4_ab\n>')
        xfa.append(self.xml_tag('ID_E4', '1'))
        for f in ['cnp_ctr','nr_ctr','data_ctr']:
            xfa.append(self.xml_tag(f, ''))
        xfa.append(self.xml_tag('cota_ctr', '0'))
        xfa.append(self.xml_tag('suma_ctr', '0'))
        xfa.append(self.xml_tag('den', ''))
        xfa.append(self.xml_tag('cui', ''))
        xfa.append(self.xml_tag('cota', '0'))
        xfa.append(self.xml_tag('suma', '0'))
        xfa.append('<adaug xfa:dataNode="dataGroup"\n/>')
        xfa.append('</sbfrmSectiuneaE4_ab\n>')
        xfa.append('</sbfrmSectiuneaE\n>')

        xfa.append('<det1\n>')
        xfa.append('<det2\n>')
        for f in ['stat_detasat','cif_detasat']:
            xfa.append(self.xml_tag(f, ''))
        for f in ['bifa_UE','bifa_altstat','acord_NU','acord_DA']:
            xfa.append(self.xml_tag(f, '0'))
        for f in ['dataD2','dataD1']:
            xfa.append(self.xml_tag(f, ''))
        xfa.append(self.xml_tag('tfNrCrt', '1'))
        xfa.append(self.xml_tag('detasat', ''))
        for f in ['plata3','plata4']:
            xfa.append(self.xml_tag(f, '0'))
        xfa.append('</det2\n>')
        for f in ['plata_CAS','plata_CASS','plata_CAM']:
            xfa.append(self.xml_tag(f, '0'))
        xfa.append('</det1\n>')

        xfa.append('<coAsig\n>')
        for f in ['cnpParinte2','prenSot','numeSot','cnpSot','prenParinte2',
                  'numeParinte2','prenParinte1','numeParinte1','cnpParinte1']:
            xfa.append(self.xml_tag(f, ''))
        xfa.append('</coAsig\n>')

        xfa.append('<secDE xfa:dataNode="dataGroup"\n/>')
        xfa.append('<vezi_D xfa:dataNode="dataGroup"\n/>')
        xfa.append('<sbfrmAllPlus xfa:dataNode="dataGroup"\n/>')
        xfa.append('</sbfrmPage1Asig\n>')

        return ''.join(xfa)


def generate_d112_pdf(xml_content: bytes, pdf_template_path: str, attach_xml: bool = True) -> bytes:
    """
    Genereaza PDF D112 completat din continutul XML.

    Args:
        xml_content: Continutul XML ANAF in bytes
        pdf_template_path: Calea catre template-ul PDF
        attach_xml: Daca se ataseaza XML-ul original la PDF

    Returns:
        bytes: Continutul PDF generat
    """
    # Converteste XML -> XFA
    converter = ANAFToXFAConverter(xml_content)
    xfa_datasets = converter.generate_xfa_datasets()

    # Citeste template-ul PDF
    reader = PdfReader(pdf_template_path)
    writer = PdfWriter()
    writer.clone_document_from_reader(reader)

    # Injecteaza XFA datasets
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

    # Ataseaza XML original
    if attach_xml:
        # Extrage luna si anul din XML pentru numele fisierului
        root = ET.fromstring(xml_content)
        luna = root.get('luna_r', '00')
        an = root.get('an_r', '0000')
        attachment_name = f"D112_{an}_{luna}.xml"
        writer.add_attachment(attachment_name, xml_content)

    # Scrie in memory buffer
    output_buffer = io.BytesIO()
    writer.write(output_buffer)
    output_buffer.seek(0)

    return output_buffer.getvalue()
