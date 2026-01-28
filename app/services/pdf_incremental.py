# -*- coding: utf-8 -*-
"""
PDF Incremental Update Utility

This module provides functionality to create incremental PDF updates that preserve
Adobe Reader Extensions (UR3) signatures. This is critical for ANAF forms that
require the "VALIDEAZA FORMULARUL" button to work.

The key insight is that Adobe Reader uses incremental updates when saving forms -
it appends changes at the end of the file without modifying the original signed bytes.
This preserves the UR3 signature that enables extended features like form validation.
"""

import io
import zlib
import re


def create_incremental_xfa_update(original_pdf_bytes: bytes, new_datasets_xml: str, datasets_obj_num: int = 5) -> bytes:
    """
    Create a PDF with incremental update that modifies only the XFA datasets stream.

    This approach preserves the original signed bytes and appends changes,
    which keeps the Adobe Reader Extensions (UR3) signature valid.

    Args:
        original_pdf_bytes: The original PDF template bytes
        new_datasets_xml: The new XFA datasets XML content
        datasets_obj_num: The object number of the datasets stream (usually 5)

    Returns:
        bytes: The complete PDF with incremental update appended
    """
    original_size = len(original_pdf_bytes)
    content_str = original_pdf_bytes.decode('latin-1')

    # Find old startxref value
    startxref_idx = content_str.rfind('startxref')
    old_xref_offset_str = content_str[startxref_idx+10:].split()[0]
    old_xref_offset = int(old_xref_offset_str)

    # Find the current Size (number of objects)
    size_match = re.search(r'/Size\s+(\d+)', content_str[-2000:])
    current_size = int(size_match.group(1)) if size_match else 52

    # Find Root and Info object references from existing trailer/xref
    root_match = re.search(r'/Root\s+(\d+)\s+(\d+)\s+R', content_str[-3000:])
    root_ref = f"{root_match.group(1)} {root_match.group(2)} R" if root_match else "32 0 R"

    info_match = re.search(r'/Info\s+(\d+)\s+(\d+)\s+R', content_str[-3000:])
    info_ref = f"{info_match.group(1)} {info_match.group(2)} R" if info_match else "30 0 R"

    # Find document ID
    id_match = re.search(r'/ID\s*\[\s*<([A-F0-9]+)>', content_str[-3000:])
    doc_id = id_match.group(1) if id_match else "A85AF2CDF24D7848A9431D81BADC45F6"

    # Compress the new datasets
    compressed_data = zlib.compress(new_datasets_xml.encode('utf-8'))

    # Build incremental update
    update = io.BytesIO()

    # Position where new datasets object starts
    obj_offset = original_size

    # Write new datasets object
    obj_header = f"{datasets_obj_num} 0 obj\n<</Filter/FlateDecode/Length {len(compressed_data)}/Subtype/XML/Type/EmbeddedFile>>\nstream\n"
    update.write(obj_header.encode('latin-1'))
    update.write(compressed_data)
    update.write(b"\nendstream\nendobj\n")

    # Position where new xref stream starts
    xref_obj_num = current_size  # Next available object number
    xref_offset = original_size + update.tell()

    # Create xref stream data
    # W array is [1, 3, 1] meaning 1 byte for type, 3 bytes for offset, 1 byte for gen
    # We need entries for: datasets object and the xref stream itself

    xref_entries = bytes([
        # Datasets object entry
        1, (obj_offset >> 16) & 0xFF, (obj_offset >> 8) & 0xFF, obj_offset & 0xFF, 0,
        # Xref stream self-reference
        1, (xref_offset >> 16) & 0xFF, (xref_offset >> 8) & 0xFF, xref_offset & 0xFF, 0,
    ])
    xref_data_compressed = zlib.compress(xref_entries)

    # Generate a new ID for the modified document (keep first part, change second)
    new_id = format(hash(new_datasets_xml) & 0xFFFFFFFFFFFFFFFF, '016X')

    # Build xref stream
    xref_stream_header = (
        f"{xref_obj_num} 0 obj\n"
        f"<</Type/XRef/Size {xref_obj_num + 1}"
        f"/Index[{datasets_obj_num} 1 {xref_obj_num} 1]"
        f"/W[1 3 1]"
        f"/Root {root_ref}"
        f"/Info {info_ref}"
        f"/Prev {old_xref_offset}"
        f"/ID[<{doc_id}><{new_id}>]"
        f"/Filter/FlateDecode"
        f"/Length {len(xref_data_compressed)}"
        f">>\nstream\n"
    )

    update.write(xref_stream_header.encode('latin-1'))
    update.write(xref_data_compressed)
    update.write(b"\nendstream\nendobj\n")

    # Write startxref
    update.write(f"startxref\n{xref_offset}\n%%EOF\n".encode('latin-1'))

    return original_pdf_bytes + update.getvalue()


def find_datasets_object_number(pdf_bytes: bytes) -> int:
    """
    Find the object number of the XFA datasets stream in a PDF.

    Args:
        pdf_bytes: The PDF file bytes

    Returns:
        int: The object number of the datasets stream
    """
    # This is a simplified approach - for ANAF forms, datasets is usually object 5
    # A more robust approach would parse the XFA array from AcroForm
    return 5
