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
        # Detect namespace from root element
        self.default_ns = ''
        if self.root.tag.startswith('{'):
            self.default_ns = self.root.tag[1:self.root.tag.index('}')]
        self.ns = {'anaf': self.default_ns} if self.default_ns else {}

    def get_attr(self, attr, default=''):
        return self.root.get(attr, default) or default

    def get_child_attr(self, child_name, attr, default=''):
        """Get attribute from a child element"""
        child = None
        # Try with detected namespace
        if self.default_ns:
            child = self.root.find(f'{{{self.default_ns}}}{child_name}')
        if child is None:
            # Try without namespace
            child = self.root.find(child_name)
        if child is not None:
            return child.get(attr, default) or default
        return default

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

        # Date din oblig_estimat
        cas_total_ven_estim = self.get_child_attr('oblig_estimat', 'cas_total_ven_estim', '')
        cas_ven_ales = self.get_child_attr('oblig_estimat', 'cas_ven_ales', '')
        oblcas_datorat = self.get_child_attr('oblig_estimat', 'oblcas_datorat', '')
        cas_bifa_plafon = self.get_child_attr('oblig_estimat', 'cas_bifa_plafon', '0')
        cass_total_ven_estim = self.get_child_attr('oblig_estimat', 'cass_total_ven_estim', '')
        bifa_venit_peste_plafon = self.get_child_attr('oblig_estimat', 'bifa_venit_peste_plafon', '0')
        oblcass_venit_datorat = self.get_child_attr('oblig_estimat', 'oblcass_venit_datorat', '')
        bifa_venit_sub_plafon = self.get_child_attr('oblig_estimat', 'bifa_venit_sub_plafon', '0')
        bifa_fara_venit = self.get_child_attr('oblig_estimat', 'bifa_fara_venit', '0')
        oblimpoz_est_total = self.get_child_attr('oblig_estimat', 'oblimpoz_est_total', '')
        oblimpoz_est_deplata = self.get_child_attr('oblig_estimat', 'oblimpoz_est_deplata', '')
        oblcas_est_deplata = self.get_child_attr('oblig_estimat', 'oblcas_est_deplata', '')
        oblcass_est_total = self.get_child_attr('oblig_estimat', 'oblcass_est_total', '')
        oblcass_est_deplata = self.get_child_attr('oblig_estimat', 'oblcass_est_deplata', '')

        # Date din cap22 (venituri din norme)
        estn_categ_venit = self.get_child_attr('cap22', 'estn_categ_venit', '')
        estn_forma_org = self.get_child_attr('cap22', 'estn_forma_org', '')
        estn_caen = self.get_child_attr('cap22', 'estn_caen', '')
        estn_descriere_sediu_bun = self.get_child_attr('cap22', 'estn_descriere_sediu_bun', '')
        estn_nr_doc_autoriz = self.get_child_attr('cap22', 'estn_nr_doc_autoriz', '')
        estn_data_doc_autoriz = self.get_child_attr('cap22', 'estn_data_doc_autoriz', '')
        estn_norma_venit = self.get_child_attr('cap22', 'estn_norma_venit', '')
        estn_ajustare = self.get_child_attr('cap22', 'estn_ajustare', '')
        estn_venit_net_anual = self.get_child_attr('cap22', 'estn_venit_net_anual', '')
        estn_venit_impozit = self.get_child_attr('cap22', 'estn_venit_impozit', '')
        estn_impozit = self.get_child_attr('cap22', 'estn_impozit', '')

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
                space_parts = parts[0].split()
                if len(space_parts) >= 2:
                    pren = space_parts[0]
                    nume = ' '.join(space_parts[1:])
                else:
                    nume = parts[0]

        # Determine which checkboxes to set based on data
        has_cap22 = bool(estn_categ_venit)
        has_cas = bool(oblcas_datorat)
        has_cass = bool(oblcass_venit_datorat)

        # Construieste XFA
        xfa = []
        xfa.append('<xfa:datasets xmlns:xfa="http://www.xfa.org/schema/xfa-data/1.0/">')
        xfa.append('<xfa:data>')
        xfa.append('<form1>')

        # btnDoc
        xfa.append('<btnDoc>')
        xfa.append('<btnSalt/>')
        xfa.append('<btnWebService/>')
        xfa.append('<info><help xfa:dataNode="dataGroup"/></info>')
        xfa.append('</btnDoc>')

        xfa.append('<Title xfa:dataNode="dataGroup"/>')

        # IdDoc
        xfa.append('<IdDoc>')
        xfa.append(self.xml_tag('totalPlata_A', totalPlata_A))
        xfa.append(self.xml_tag('formValid', ''))
        xfa.append(self.xml_tag('universalCode', 'D212_A1.0.6'))
        xfa.append(self.xml_tag('an_r', an_r))
        xfa.append(self.xml_tag('luna_r', luna_r))
        xfa.append(self.xml_tag('d_rec', d_rec))
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
        xfa.append(self.xml_tag('iban', cont_bancar))
        xfa.append(self.xml_tag('nrzC', nerezident))
        xfa.append('<infN><statN/><cifN/></infN>')
        xfa.append('</idCnt>')

        # bife - Checkboxes
        xfa.append('<bife>')

        # Cap1 - for realized income (not used in this example)
        xfa.append('<Cap1>')
        xfa.append('<bifaR1>')
        xfa.append(self.xml_tag('d_rec1', rectif1))
        xfa.append('</bifaR1>')
        xfa.append(self.xml_tag('I11', '0'))
        xfa.append(self.xml_tag('I12', '0'))
        xfa.append(self.xml_tag('I13', '0'))
        xfa.append(self.xml_tag('I2', '0'))
        xfa.append(self.xml_tag('I31', '0'))
        xfa.append(self.xml_tag('I32', '0'))
        xfa.append(self.xml_tag('I4', '0'))
        xfa.append('<S1 xfa:dataNode="dataGroup"/>')
        xfa.append(self.xml_tag('I5', '0'))
        xfa.append('</Cap1>')

        # Cap2 - for estimated income
        xfa.append('<Cap2>')
        xfa.append('<bifaR2>')
        xfa.append(self.xml_tag('d_rec2', rectif2))
        xfa.append('</bifaR2>')
        # Ii11 = impozit, Ii12 = norme de venit, Ii13 = alte venituri
        xfa.append(self.xml_tag('Ii11', '0'))
        xfa.append(self.xml_tag('Ii12', '1' if has_cap22 else '0'))  # Norme de venit
        xfa.append(self.xml_tag('Ii13', '0'))
        # Ii31 = CAS, Ii32 = CASS
        xfa.append(self.xml_tag('Ii31', '1' if has_cas else '0'))
        xfa.append(self.xml_tag('Ii32', '1' if has_cass else '0'))
        xfa.append('</Cap2>')

        xfa.append('</bife>')

        # bifaI - Representative
        xfa.append('<bifaI>')
        xfa.append(self.xml_tag('rprI', '0'))
        xfa.append('</bifaI>')

        # s111_alias - empty structure for realized income
        xfa.append('<s111_alias>')
        xfa.append('<date>')
        xfa.append('<nrCrt><nV/></nrCrt>')
        xfa.append('<Scutiri><Gap xfa:dataNode="dataGroup"/><sctRgl><vScutit>0</vScutit><oRegularizare>0</oRegularizare></sctRgl></Scutiri>')
        xfa.append('<Cat><Gap xfa:dataNode="dataGroup"/><cat><slct/></cat></Cat>')
        xfa.append('<catChild>')
        xfa.append('<Det><Gap xfa:dataNode="dataGroup"/><det><slct/></det></Det>')
        xfa.append('<Org><Gap xfa:dataNode="dataGroup"/><org><slct/><mod>0</mod><info><help xfa:dataNode="dataGroup"/></info></org></Org>')
        xfa.append('<Caen><Gap xfa:dataNode="dataGroup"/><caen/><denCaen/></Caen>')
        xfa.append('<SedIdentif><Gap xfa:dataNode="dataGroup"/><loc/></SedIdentif>')
        xfa.append('<Doc><Gap xfa:dataNode="dataGroup"/><nrData><nrD/><dataD/></nrData></Doc>')
        xfa.append('<Actv><Gap xfa:dataNode="dataGroup"/><infoA><incA/><sfA/><nrZile/></infoA></Actv>')
        xfa.append('<VntImp><Gap><alteVenituri><slct/></alteVenituri></Gap><tabelVenit><venitB/><chltD/><venitN/><cstgN/><pierdF/><pierdFP/><venitImp/><venitImpRed/><impDat/></tabelVenit></VntImp>')
        xfa.append('</catChild>')
        xfa.append('</date>')
        xfa.append('</s111_alias>')

        xfa.append('<Gap xfa:dataNode="dataGroup"/>')

        # c11Alias - empty
        xfa.append('<c11Alias>')
        xfa.append('<imp18plt/><imp18bnf/><cas18plt/><cas18bnf/><cass18plt/><cass18bnf/>')
        xfa.append('</c11Alias>')

        # s212 - Estimated income from norms (cap22 data)
        if has_cap22:
            xfa.append('<s212>')
            xfa.append('<date>')
            xfa.append('<nrCrt><nV>1</nV></nrCrt>')
            xfa.append('<Cat><Gap xfa:dataNode="dataGroup"/><cat>')
            xfa.append(self.xml_tag('slct', '1'))  # Category 1 = norme de venit
            xfa.append('<nrCam/>')
            xfa.append('</cat></Cat>')
            xfa.append('<catChild>')
            xfa.append('<Org><Gap xfa:dataNode="dataGroup"/><org>')
            xfa.append(self.xml_tag('slct', estn_forma_org))
            xfa.append('</org></Org>')
            xfa.append('<Caen><Gap xfa:dataNode="dataGroup"/>')
            xfa.append(self.xml_tag('caen', estn_caen))
            xfa.append('<denCaen/>')
            xfa.append('</Caen>')
            xfa.append('<SedIdentif><Gap xfa:dataNode="dataGroup"/>')
            xfa.append(self.xml_tag('loc', estn_descriere_sediu_bun))
            xfa.append('</SedIdentif>')
            xfa.append('<Doc><Gap xfa:dataNode="dataGroup"/><nrData>')
            xfa.append(self.xml_tag('nrD', estn_nr_doc_autoriz))
            xfa.append(self.xml_tag('dataD', estn_data_doc_autoriz))
            xfa.append('</nrData></Doc>')
            xfa.append('<Actv><Gap xfa:dataNode="dataGroup"/><infoA><incA/><sfA/><spA/><nrZile/></infoA></Actv>')
            xfa.append('<VntImp><Gap xfa:dataNode="dataGroup"/><tabelVenit>')
            xfa.append(self.xml_tag('venitB', estn_norma_venit))
            xfa.append(self.xml_tag('chltD', estn_ajustare))
            xfa.append(self.xml_tag('venitN', estn_venit_net_anual))
            xfa.append(self.xml_tag('cstgN', estn_venit_impozit))
            xfa.append(self.xml_tag('impDat', estn_impozit))
            xfa.append('</tabelVenit></VntImp>')
            xfa.append('</catChild>')
            xfa.append('</date>')
            xfa.append('</s212>')

        # sumar2 - Summary for chapter 2
        xfa.append('<sumar2>')
        xfa.append('<c12>')
        xfa.append('<imp18><Gap xfa:dataNode="dataGroup"/><tabel>')
        xfa.append(self.xml_tag('dtr', oblimpoz_est_total))
        xfa.append('<bnf1/>')
        xfa.append('</tabel></imp18>')
        xfa.append('<cas18><Gap xfa:dataNode="dataGroup"/><tabel>')
        xfa.append(self.xml_tag('dtr', oblcas_datorat))
        xfa.append('<bnf1/>')
        xfa.append('</tabel></cas18>')
        xfa.append('<cass18><Gap xfa:dataNode="dataGroup"/><tabel>')
        xfa.append(self.xml_tag('dtr', oblcass_venit_datorat))
        xfa.append('<bnf1/>')
        xfa.append('</tabel></cass18>')
        xfa.append('</c12>')
        xfa.append('</sumar2>')

        # c21 - Payment summary
        xfa.append('<c21>')
        xfa.append('<imp18><Gap xfa:dataNode="dataGroup"/><tabel>')
        xfa.append(self.xml_tag('dtr', oblimpoz_est_total))
        xfa.append('<bnf/>')
        xfa.append(self.xml_tag('plt', oblimpoz_est_deplata))
        xfa.append('</tabel></imp18>')
        xfa.append('<cas18><Gap xfa:dataNode="dataGroup"/><tabel>')
        xfa.append(self.xml_tag('dtr', oblcas_datorat))
        xfa.append('<bnf/>')
        xfa.append(self.xml_tag('plt', oblcas_est_deplata))
        xfa.append('</tabel></cas18>')
        xfa.append('<cass18><Gap xfa:dataNode="dataGroup"/><tabel>')
        xfa.append(self.xml_tag('dtr', oblcass_venit_datorat))
        xfa.append('<bnf/>')
        xfa.append(self.xml_tag('plt', oblcass_est_deplata))
        xfa.append('</tabel></cass18>')
        xfa.append('</c21>')

        # s221 - CAS section
        if has_cas:
            xfa.append('<s221>')
            xfa.append('<Cas><Gap xfa:dataNode="dataGroup"/><tabel>')
            xfa.append(self.xml_tag('venitA', cas_total_ven_estim))
            xfa.append(self.xml_tag('alegV', cas_bifa_plafon))
            xfa.append(self.xml_tag('bazaC', cas_ven_ales))
            xfa.append(self.xml_tag('casDat', oblcas_datorat))
            xfa.append('</tabel></Cas>')
            xfa.append('</s221>')

        # s222 - CASS section
        if has_cass:
            xfa.append('<s222>')
            xfa.append('<Cas><Gap xfa:dataNode="dataGroup"/><tabel>')
            xfa.append(self.xml_tag('venitA', cass_total_ven_estim))
            xfa.append(self.xml_tag('aVntGtMin', bifa_venit_peste_plafon))
            xfa.append(self.xml_tag('casA', oblcass_venit_datorat))
            xfa.append(self.xml_tag('bVntSmMin', bifa_venit_sub_plafon))
            xfa.append('<casB/>')
            xfa.append(self.xml_tag('cNoVnt', bifa_fara_venit))
            xfa.append('<casC/>')
            xfa.append('</tabel></Cas>')
            xfa.append('</s222>')

        xfa.append('</form1>')
        xfa.append('</xfa:data>')
        xfa.append('</xfa:datasets>')

        return ''.join(xfa)


def generate_d212_pdf(xml_content: bytes, pdf_template_path: str, attach_xml: bool = True) -> bytes:
    """Genereaza PDF D212 completat din continutul XML.
    Foloseste incremental updates pentru a pastra semnatura Adobe Reader Extensions (UR3)
    care permite functionarea butonului 'VALIDEAZA FORMULARUL'.
    """
    from .pdf_incremental import create_incremental_xfa_update

    converter = D212ToXFAConverter(xml_content)
    xfa_datasets = converter.generate_xfa_datasets()

    # Citim template-ul original
    with open(pdf_template_path, 'rb') as f:
        pdf_bytes = f.read()

    # Folosim incremental update pentru a pastra semnatura UR3
    # Datasets stream este object 5 in template-ul D212
    result_pdf = create_incremental_xfa_update(pdf_bytes, xfa_datasets, datasets_obj_num=5)

    return result_pdf
