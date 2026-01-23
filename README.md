# PDF XML Attachment Tool

## Instalare rapidă

### Windows
```cmd
pip install pypdf lxml
```

### Mac/Linux
```bash
pip3 install pypdf lxml
```

---

## Utilizare

### Metoda 1: Script de test simplu

1. Pune toate fișierele într-un folder:
   ```
   folder/
   ├── pdf_xml_attachment.py
   ├── test_simplu.py
   └── document.pdf  (opțional)
   ```

2. Deschide terminal/cmd în folder

3. Rulează:
   ```bash
   python test_simplu.py
   ```

4. Verifică folderul `output_test/` pentru rezultate

---

### Metoda 2: Utilizare ca librărie

```python
from pdf_xml_attachment import PDFXMLManager, XMLValidator

# Atașează XML la PDF
manager = PDFXMLManager("declaratie.pdf")
manager.attach_xml("date.xml", "output.pdf")

# Listează atașamente existente
attachments = manager.list_attachments()
for att in attachments:
    print(f"{att.name}: {att.size} bytes")

# Extrage atașamente
manager.extract_all_attachments("folder_output/")

# Validare XML cu schemă XSD
validator = XMLValidator("schema.xsd")
result = validator.validate_file("date.xml")
print(f"Valid: {result.is_valid}")
print(f"Erori: {result.errors}")
```

---

## Funcționalități

| Funcție | Descriere |
|---------|-----------|
| `PDFXMLManager.attach_xml()` | Atașează un XML la PDF |
| `PDFXMLManager.attach_multiple_files()` | Atașează mai multe fișiere |
| `PDFXMLManager.list_attachments()` | Listează atașamentele |
| `PDFXMLManager.extract_attachment()` | Extrage un atașament |
| `PDFXMLManager.extract_all_attachments()` | Extrage toate atașamentele |
| `XMLValidator.validate_file()` | Validează XML (opțional cu XSD) |
| `generate_validation_report()` | Generează raport HTML/JSON/TXT |

---

## Structura fișierelor

```
pdf_xml_attachment.py   - Librăria principală
test_simplu.py          - Script de test rapid
test_d112.py            - Test complet cu D112
d112_schema.xsd         - Exemplu schemă XSD
d112_test.xml           - Exemplu XML D112
```
