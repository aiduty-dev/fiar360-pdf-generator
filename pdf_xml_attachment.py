#!/usr/bin/env python3
"""
PDF XML Attachment & Validation Tool
=====================================
Acest script permite:
1. Atașarea unui fișier XML la un PDF
2. Extragerea fișierelor atașate dintr-un PDF
3. Validarea XML-ului contra unei scheme XSD
4. Generarea unui raport de validare

Autor: FIAR360 Team
Versiune: 1.0
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple, List, Dict, Any
from dataclasses import dataclass, asdict
from enum import Enum

# PDF handling
from pypdf import PdfReader, PdfWriter

# XML handling
from lxml import etree


class ValidationStatus(Enum):
    VALID = "valid"
    INVALID = "invalid"
    NO_SCHEMA = "no_schema"
    ERROR = "error"


@dataclass
class ValidationResult:
    """Rezultatul validării XML"""
    status: ValidationStatus
    xml_file: str
    schema_file: Optional[str]
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    timestamp: str
    xml_root_element: Optional[str] = None
    xml_namespace: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result['status'] = self.status.value
        return result


@dataclass 
class AttachmentInfo:
    """Informații despre un atașament din PDF"""
    name: str
    size: int
    description: Optional[str]
    creation_date: Optional[str]
    modification_date: Optional[str]


class PDFXMLManager:
    """Manager pentru operații PDF-XML"""
    
    def __init__(self, pdf_path: str):
        self.pdf_path = Path(pdf_path)
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDF nu există: {pdf_path}")
        
        self.reader = PdfReader(str(self.pdf_path))
    
    def list_attachments(self) -> List[AttachmentInfo]:
        """Listează toate atașamentele din PDF"""
        attachments = []
        
        # Verifică embedded files în catalog
        if "/Names" in self.reader.trailer["/Root"]:
            names = self.reader.trailer["/Root"]["/Names"]
            if "/EmbeddedFiles" in names:
                embedded_files = names["/EmbeddedFiles"]
                if "/Names" in embedded_files:
                    names_array = embedded_files["/Names"]
                    for i in range(0, len(names_array), 2):
                        name = str(names_array[i])
                        file_spec = names_array[i + 1].get_object()
                        
                        # Extrage informații
                        size = 0
                        if "/EF" in file_spec:
                            ef = file_spec["/EF"]
                            if "/F" in ef:
                                stream = ef["/F"].get_object()
                                if "/Length" in stream:
                                    size = int(stream["/Length"])
                        
                        desc = file_spec.get("/Desc", None)
                        if desc:
                            desc = str(desc)
                        
                        attachments.append(AttachmentInfo(
                            name=name,
                            size=size,
                            description=desc,
                            creation_date=None,
                            modification_date=None
                        ))
        
        # Metodă alternativă - pypdf built-in
        if hasattr(self.reader, 'attachments') and self.reader.attachments:
            for name, data_list in self.reader.attachments.items():
                if not any(a.name == name for a in attachments):
                    for data in data_list:
                        attachments.append(AttachmentInfo(
                            name=name,
                            size=len(data) if data else 0,
                            description=None,
                            creation_date=None,
                            modification_date=None
                        ))
        
        return attachments
    
    def extract_attachment(self, attachment_name: str, output_path: str) -> bool:
        """Extrage un atașament din PDF"""
        if hasattr(self.reader, 'attachments') and self.reader.attachments:
            for name, data_list in self.reader.attachments.items():
                if name == attachment_name:
                    for data in data_list:
                        with open(output_path, 'wb') as f:
                            f.write(data)
                        return True
        return False
    
    def extract_all_attachments(self, output_dir: str) -> List[str]:
        """Extrage toate atașamentele într-un director"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        extracted = []
        if hasattr(self.reader, 'attachments') and self.reader.attachments:
            for name, data_list in self.reader.attachments.items():
                for i, data in enumerate(data_list):
                    if len(data_list) > 1:
                        file_path = output_path / f"{Path(name).stem}_{i}{Path(name).suffix}"
                    else:
                        file_path = output_path / name
                    
                    with open(file_path, 'wb') as f:
                        f.write(data)
                    extracted.append(str(file_path))
        
        return extracted
    
    def attach_xml(self, xml_path: str, output_pdf_path: str, 
                   attachment_name: Optional[str] = None,
                   description: Optional[str] = None) -> str:
        """
        Atașează un fișier XML la PDF
        
        Args:
            xml_path: Calea către fișierul XML
            output_pdf_path: Calea pentru PDF-ul rezultat
            attachment_name: Numele atașamentului (default: numele fișierului XML)
            description: Descriere opțională
            
        Returns:
            Calea către PDF-ul rezultat
        """
        xml_file = Path(xml_path)
        if not xml_file.exists():
            raise FileNotFoundError(f"XML nu există: {xml_path}")
        
        # Citește XML-ul
        with open(xml_file, 'rb') as f:
            xml_data = f.read()
        
        # Numele atașamentului
        if attachment_name is None:
            attachment_name = xml_file.name
        
        # Creează writer și copiază paginile
        writer = PdfWriter()
        for page in self.reader.pages:
            writer.add_page(page)
        
        # Copiază metadatele
        if self.reader.metadata:
            writer.add_metadata(self.reader.metadata)
        
        # Atașează XML-ul
        writer.add_attachment(attachment_name, xml_data)
        
        # Salvează
        output_path = Path(output_pdf_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'wb') as f:
            writer.write(f)
        
        return str(output_path)
    
    def attach_multiple_files(self, files: List[Tuple[str, Optional[str]]], 
                              output_pdf_path: str) -> str:
        """
        Atașează multiple fișiere la PDF
        
        Args:
            files: Lista de tuple (cale_fișier, nume_atașament_opțional)
            output_pdf_path: Calea pentru PDF-ul rezultat
            
        Returns:
            Calea către PDF-ul rezultat
        """
        writer = PdfWriter()
        
        # Copiază paginile
        for page in self.reader.pages:
            writer.add_page(page)
        
        # Copiază metadatele
        if self.reader.metadata:
            writer.add_metadata(self.reader.metadata)
        
        # Atașează fișierele
        for file_path, attachment_name in files:
            file_obj = Path(file_path)
            if not file_obj.exists():
                print(f"Atenție: Fișierul {file_path} nu există, skip.")
                continue
            
            with open(file_obj, 'rb') as f:
                data = f.read()
            
            name = attachment_name if attachment_name else file_obj.name
            writer.add_attachment(name, data)
        
        # Salvează
        output_path = Path(output_pdf_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'wb') as f:
            writer.write(f)
        
        return str(output_path)


class XMLValidator:
    """Validator XML cu suport pentru XSD"""
    
    def __init__(self, schema_path: Optional[str] = None):
        self.schema = None
        self.schema_path = schema_path
        
        if schema_path:
            self._load_schema(schema_path)
    
    def _load_schema(self, schema_path: str):
        """Încarcă schema XSD"""
        schema_file = Path(schema_path)
        if not schema_file.exists():
            raise FileNotFoundError(f"Schema XSD nu există: {schema_path}")
        
        try:
            with open(schema_file, 'rb') as f:
                schema_doc = etree.parse(f)
            self.schema = etree.XMLSchema(schema_doc)
        except etree.XMLSchemaError as e:
            raise ValueError(f"Schema XSD invalidă: {e}")
    
    def validate_file(self, xml_path: str) -> ValidationResult:
        """
        Validează un fișier XML
        
        Args:
            xml_path: Calea către fișierul XML
            
        Returns:
            ValidationResult cu detaliile validării
        """
        errors = []
        warnings = []
        root_element = None
        namespace = None
        
        try:
            # Parsează XML-ul
            with open(xml_path, 'rb') as f:
                xml_doc = etree.parse(f)
            
            root = xml_doc.getroot()
            root_element = etree.QName(root).localname
            namespace = root.nsmap.get(None, root.nsmap.get(root.prefix))
            
            # Validare well-formed - deja trecută dacă am ajuns aici
            
            # Validare contra schemei dacă există
            if self.schema:
                is_valid = self.schema.validate(xml_doc)
                
                if not is_valid:
                    for error in self.schema.error_log:
                        errors.append(f"Linia {error.line}: {error.message}")
                
                return ValidationResult(
                    status=ValidationStatus.VALID if is_valid else ValidationStatus.INVALID,
                    xml_file=xml_path,
                    schema_file=self.schema_path,
                    is_valid=is_valid,
                    errors=errors,
                    warnings=warnings,
                    timestamp=datetime.now().isoformat(),
                    xml_root_element=root_element,
                    xml_namespace=namespace
                )
            else:
                # Fără schemă - doar verificare well-formed
                warnings.append("Nu s-a specificat o schemă XSD pentru validare completă")
                return ValidationResult(
                    status=ValidationStatus.NO_SCHEMA,
                    xml_file=xml_path,
                    schema_file=None,
                    is_valid=True,  # Well-formed
                    errors=errors,
                    warnings=warnings,
                    timestamp=datetime.now().isoformat(),
                    xml_root_element=root_element,
                    xml_namespace=namespace
                )
                
        except etree.XMLSyntaxError as e:
            errors.append(f"Eroare de sintaxă XML: {e}")
            return ValidationResult(
                status=ValidationStatus.INVALID,
                xml_file=xml_path,
                schema_file=self.schema_path,
                is_valid=False,
                errors=errors,
                warnings=warnings,
                timestamp=datetime.now().isoformat()
            )
        except Exception as e:
            errors.append(f"Eroare la validare: {str(e)}")
            return ValidationResult(
                status=ValidationStatus.ERROR,
                xml_file=xml_path,
                schema_file=self.schema_path,
                is_valid=False,
                errors=errors,
                warnings=warnings,
                timestamp=datetime.now().isoformat()
            )
    
    def validate_string(self, xml_content: bytes, source_name: str = "inline") -> ValidationResult:
        """Validează conținut XML din bytes"""
        errors = []
        warnings = []
        root_element = None
        namespace = None
        
        try:
            xml_doc = etree.fromstring(xml_content)
            root_element = etree.QName(xml_doc).localname
            namespace = xml_doc.nsmap.get(None, xml_doc.nsmap.get(xml_doc.prefix))
            
            if self.schema:
                # Pentru validare cu schemă, trebuie un ElementTree
                tree = etree.ElementTree(xml_doc)
                is_valid = self.schema.validate(tree)
                
                if not is_valid:
                    for error in self.schema.error_log:
                        errors.append(f"Linia {error.line}: {error.message}")
                
                return ValidationResult(
                    status=ValidationStatus.VALID if is_valid else ValidationStatus.INVALID,
                    xml_file=source_name,
                    schema_file=self.schema_path,
                    is_valid=is_valid,
                    errors=errors,
                    warnings=warnings,
                    timestamp=datetime.now().isoformat(),
                    xml_root_element=root_element,
                    xml_namespace=namespace
                )
            else:
                warnings.append("Nu s-a specificat o schemă XSD pentru validare completă")
                return ValidationResult(
                    status=ValidationStatus.NO_SCHEMA,
                    xml_file=source_name,
                    schema_file=None,
                    is_valid=True,
                    errors=errors,
                    warnings=warnings,
                    timestamp=datetime.now().isoformat(),
                    xml_root_element=root_element,
                    xml_namespace=namespace
                )
                
        except etree.XMLSyntaxError as e:
            errors.append(f"Eroare de sintaxă XML: {e}")
            return ValidationResult(
                status=ValidationStatus.INVALID,
                xml_file=source_name,
                schema_file=self.schema_path,
                is_valid=False,
                errors=errors,
                warnings=warnings,
                timestamp=datetime.now().isoformat()
            )


def generate_validation_report(results: List[ValidationResult], 
                               output_path: str,
                               format: str = "html") -> str:
    """
    Generează un raport de validare
    
    Args:
        results: Lista de rezultate ale validării
        output_path: Calea pentru raport
        format: Formatul raportului (html, json, txt)
        
    Returns:
        Calea către raportul generat
    """
    if format == "json":
        report_data = {
            "generated_at": datetime.now().isoformat(),
            "total_files": len(results),
            "valid_count": sum(1 for r in results if r.is_valid),
            "invalid_count": sum(1 for r in results if not r.is_valid),
            "results": [r.to_dict() for r in results]
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
    
    elif format == "html":
        html_content = _generate_html_report(results)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    elif format == "txt":
        txt_content = _generate_txt_report(results)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(txt_content)
    
    return output_path


def _generate_html_report(results: List[ValidationResult]) -> str:
    """Generează raport HTML"""
    valid_count = sum(1 for r in results if r.is_valid)
    invalid_count = len(results) - valid_count
    
    rows = ""
    for r in results:
        status_class = "valid" if r.is_valid else "invalid"
        status_icon = "✓" if r.is_valid else "✗"
        errors_html = "<br>".join(r.errors) if r.errors else "-"
        warnings_html = "<br>".join(r.warnings) if r.warnings else "-"
        
        rows += f"""
        <tr class="{status_class}">
            <td>{r.xml_file}</td>
            <td>{status_icon} {r.status.value}</td>
            <td>{r.xml_root_element or '-'}</td>
            <td>{r.schema_file or 'Fără schemă'}</td>
            <td class="errors">{errors_html}</td>
            <td class="warnings">{warnings_html}</td>
        </tr>
        """
    
    return f"""<!DOCTYPE html>
<html lang="ro">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Raport Validare XML</title>
    <style>
        * {{ box-sizing: border-box; }}
        body {{ 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            margin: 0; padding: 20px; 
            background: #f5f5f5;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        h1 {{ color: #333; border-bottom: 2px solid #007bff; padding-bottom: 10px; }}
        .summary {{ 
            display: flex; gap: 20px; margin-bottom: 20px; 
        }}
        .summary-card {{ 
            padding: 20px; border-radius: 8px; color: white; flex: 1;
            text-align: center;
        }}
        .summary-card.total {{ background: #6c757d; }}
        .summary-card.valid {{ background: #28a745; }}
        .summary-card.invalid {{ background: #dc3545; }}
        .summary-card h2 {{ margin: 0; font-size: 2.5em; }}
        .summary-card p {{ margin: 5px 0 0 0; opacity: 0.9; }}
        table {{ 
            width: 100%; border-collapse: collapse; 
            background: white; border-radius: 8px; overflow: hidden;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #007bff; color: white; }}
        tr:hover {{ background: #f8f9fa; }}
        tr.valid td:nth-child(2) {{ color: #28a745; font-weight: bold; }}
        tr.invalid td:nth-child(2) {{ color: #dc3545; font-weight: bold; }}
        .errors {{ color: #dc3545; font-size: 0.9em; }}
        .warnings {{ color: #ffc107; font-size: 0.9em; }}
        .timestamp {{ text-align: right; color: #666; margin-top: 20px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📋 Raport Validare XML</h1>
        
        <div class="summary">
            <div class="summary-card total">
                <h2>{len(results)}</h2>
                <p>Total fișiere</p>
            </div>
            <div class="summary-card valid">
                <h2>{valid_count}</h2>
                <p>Valide</p>
            </div>
            <div class="summary-card invalid">
                <h2>{invalid_count}</h2>
                <p>Invalide</p>
            </div>
        </div>
        
        <table>
            <thead>
                <tr>
                    <th>Fișier XML</th>
                    <th>Status</th>
                    <th>Element Rădăcină</th>
                    <th>Schemă XSD</th>
                    <th>Erori</th>
                    <th>Avertismente</th>
                </tr>
            </thead>
            <tbody>
                {rows}
            </tbody>
        </table>
        
        <p class="timestamp">Generat la: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
</body>
</html>"""


def _generate_txt_report(results: List[ValidationResult]) -> str:
    """Generează raport text"""
    lines = [
        "=" * 70,
        "RAPORT VALIDARE XML",
        "=" * 70,
        f"Generat: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Total fișiere: {len(results)}",
        f"Valide: {sum(1 for r in results if r.is_valid)}",
        f"Invalide: {sum(1 for r in results if not r.is_valid)}",
        "=" * 70,
        ""
    ]
    
    for r in results:
        status = "✓ VALID" if r.is_valid else "✗ INVALID"
        lines.extend([
            f"Fișier: {r.xml_file}",
            f"Status: {status}",
            f"Element rădăcină: {r.xml_root_element or '-'}",
            f"Namespace: {r.xml_namespace or '-'}",
            f"Schemă: {r.schema_file or 'Fără schemă'}"
        ])
        
        if r.errors:
            lines.append("Erori:")
            for e in r.errors:
                lines.append(f"  - {e}")
        
        if r.warnings:
            lines.append("Avertismente:")
            for w in r.warnings:
                lines.append(f"  - {w}")
        
        lines.extend(["-" * 70, ""])
    
    return "\n".join(lines)


# =====================================
# Funcții de conveniență pentru CLI
# =====================================

def demo():
    """Demonstrație rapidă a funcționalităților"""
    print("=" * 60)
    print("PDF-XML Attachment & Validation Tool - Demo")
    print("=" * 60)
    
    # Creează fișiere de test
    test_dir = Path("/home/claude/pdf_xml_tools/test_files")
    test_dir.mkdir(parents=True, exist_ok=True)
    
    # XML valid de test
    valid_xml = """<?xml version="1.0" encoding="UTF-8"?>
<declaratie xmlns="urn:anaf:dgfp:d112:v1">
    <antet>
        <an>2025</an>
        <luna>1</luna>
    </antet>
    <contribuabil>
        <cui>12345678</cui>
        <denumire>Test SRL</denumire>
    </contribuabil>
    <date>
        <suma>1000.00</suma>
    </date>
</declaratie>"""
    
    # XML invalid de test (tag-uri neînchise)
    invalid_xml = """<?xml version="1.0" encoding="UTF-8"?>
<declaratie>
    <antet>
        <an>2025
    </antet>
</declaratie>"""
    
    # Schema XSD simplă
    xsd_schema = """<?xml version="1.0" encoding="UTF-8"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema"
           xmlns="urn:anaf:dgfp:d112:v1"
           targetNamespace="urn:anaf:dgfp:d112:v1"
           elementFormDefault="qualified">
    
    <xs:element name="declaratie">
        <xs:complexType>
            <xs:sequence>
                <xs:element name="antet">
                    <xs:complexType>
                        <xs:sequence>
                            <xs:element name="an" type="xs:int"/>
                            <xs:element name="luna" type="xs:int"/>
                        </xs:sequence>
                    </xs:complexType>
                </xs:element>
                <xs:element name="contribuabil">
                    <xs:complexType>
                        <xs:sequence>
                            <xs:element name="cui" type="xs:string"/>
                            <xs:element name="denumire" type="xs:string"/>
                        </xs:sequence>
                    </xs:complexType>
                </xs:element>
                <xs:element name="date">
                    <xs:complexType>
                        <xs:sequence>
                            <xs:element name="suma" type="xs:decimal"/>
                        </xs:sequence>
                    </xs:complexType>
                </xs:element>
            </xs:sequence>
        </xs:complexType>
    </xs:element>
</xs:schema>"""
    
    # Salvează fișierele de test
    (test_dir / "valid.xml").write_text(valid_xml, encoding='utf-8')
    (test_dir / "invalid.xml").write_text(invalid_xml, encoding='utf-8')
    (test_dir / "schema.xsd").write_text(xsd_schema, encoding='utf-8')
    
    print(f"\n✓ Fișiere de test create în: {test_dir}")
    
    # Test validare
    print("\n--- Test Validare XML ---")
    validator = XMLValidator(str(test_dir / "schema.xsd"))
    
    result1 = validator.validate_file(str(test_dir / "valid.xml"))
    print(f"\nvalid.xml: {result1.status.value}")
    print(f"  Element rădăcină: {result1.xml_root_element}")
    
    result2 = validator.validate_file(str(test_dir / "invalid.xml"))
    print(f"\ninvalid.xml: {result2.status.value}")
    for err in result2.errors:
        print(f"  Eroare: {err}")
    
    # Generează raport
    report_path = str(test_dir / "raport_validare.html")
    generate_validation_report([result1, result2], report_path, format="html")
    print(f"\n✓ Raport generat: {report_path}")
    
    print("\n" + "=" * 60)
    print("Demo completat!")
    print("=" * 60)


if __name__ == "__main__":
    demo()
