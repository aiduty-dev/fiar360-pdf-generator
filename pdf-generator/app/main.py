# -*- coding: utf-8 -*-
"""
FastAPI PDF Generator Service
Genereaza PDF-uri ANAF (D112, D300, D301, D390, D394) din XML.
"""

import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import Response
from .services.d112_generator import generate_d112_pdf
from .services.d212_wf_generator import generate_d212_wf_pdf
from .services.d300_generator import generate_d300_pdf
from .services.d301_generator import generate_d301_pdf
from .services.d390_generator import generate_d390_pdf
from .services.d394_generator import generate_d394_pdf

app = FastAPI(
    title="ANAF PDF Generator",
    description="Serviciu pentru generarea PDF-urilor ANAF completate din XML",
    version="1.4.0"
)

# Template-uri PDF
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")
D112_TEMPLATE = os.path.join(TEMPLATES_DIR, "D112_XML_2025_0825_191125.pdf")
D212_TEMPLATE = os.path.join(TEMPLATES_DIR, "D212_WF_template.pdf")
D300_TEMPLATE = os.path.join(TEMPLATES_DIR, "D300_v11.0.7_16122025.pdf")
D301_TEMPLATE = os.path.join(TEMPLATES_DIR, "D301_XML_2017_260320.pdf")
D390_TEMPLATE = os.path.join(TEMPLATES_DIR, "D390_XML_2020_300424.pdf")
D394_TEMPLATE = os.path.join(TEMPLATES_DIR, "D394_26092025.pdf")


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "pdf-generator", "forms": ["D112", "D212", "D300", "D301", "D390", "D394"]}


# ============== D112 ==============

@app.post("/api/v1/d112/generate")
async def generate_d112(request: Request, attach_xml: bool = True):
    content_type = request.headers.get("content-type", "")
    if "xml" not in content_type.lower() and "text" not in content_type.lower():
        raise HTTPException(status_code=415, detail="Content-Type must be application/xml")
    xml_content = await request.body()
    if not xml_content:
        raise HTTPException(status_code=400, detail="XML content is required")
    if not os.path.exists(D112_TEMPLATE):
        raise HTTPException(status_code=500, detail="PDF template not found")
    try:
        pdf_bytes = generate_d112_pdf(xml_content, D112_TEMPLATE, attach_xml)
        return Response(content=pdf_bytes, media_type="application/pdf",
                        headers={"Content-Disposition": "attachment; filename=D112.pdf"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")


# ============== D212 ==============

@app.post("/api/v1/d212/generate")
async def generate_d212(request: Request):
    """Generate D212 PDF in WebForm format (D212_WF1.0) with embedded XML."""
    content_type = request.headers.get("content-type", "")
    if "xml" not in content_type.lower() and "text" not in content_type.lower():
        raise HTTPException(status_code=415, detail="Content-Type must be application/xml")
    xml_content = await request.body()
    if not xml_content:
        raise HTTPException(status_code=400, detail="XML content is required")
    if not os.path.exists(D212_TEMPLATE):
        raise HTTPException(status_code=500, detail="PDF template not found")
    try:
        pdf_bytes = generate_d212_wf_pdf(xml_content, D212_TEMPLATE)
        return Response(content=pdf_bytes, media_type="application/pdf",
                        headers={"Content-Disposition": "attachment; filename=D212.pdf"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")


# ============== D300 ==============

@app.post("/api/v1/d300/generate")
async def generate_d300(request: Request, attach_xml: bool = True):
    content_type = request.headers.get("content-type", "")
    if "xml" not in content_type.lower() and "text" not in content_type.lower():
        raise HTTPException(status_code=415, detail="Content-Type must be application/xml")
    xml_content = await request.body()
    if not xml_content:
        raise HTTPException(status_code=400, detail="XML content is required")
    if not os.path.exists(D300_TEMPLATE):
        raise HTTPException(status_code=500, detail="PDF template not found")
    try:
        pdf_bytes = generate_d300_pdf(xml_content, D300_TEMPLATE, attach_xml)
        return Response(content=pdf_bytes, media_type="application/pdf",
                        headers={"Content-Disposition": "attachment; filename=D300.pdf"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")


# ============== D301 ==============

@app.post("/api/v1/d301/generate")
async def generate_d301(request: Request, attach_xml: bool = True):
    content_type = request.headers.get("content-type", "")
    if "xml" not in content_type.lower() and "text" not in content_type.lower():
        raise HTTPException(status_code=415, detail="Content-Type must be application/xml")
    xml_content = await request.body()
    if not xml_content:
        raise HTTPException(status_code=400, detail="XML content is required")
    if not os.path.exists(D301_TEMPLATE):
        raise HTTPException(status_code=500, detail="PDF template not found")
    try:
        pdf_bytes = generate_d301_pdf(xml_content, D301_TEMPLATE, attach_xml)
        return Response(content=pdf_bytes, media_type="application/pdf",
                        headers={"Content-Disposition": "attachment; filename=D301.pdf"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")


# ============== D390 ==============

@app.post("/api/v1/d390/generate")
async def generate_d390(request: Request, attach_xml: bool = True):
    content_type = request.headers.get("content-type", "")
    if "xml" not in content_type.lower() and "text" not in content_type.lower():
        raise HTTPException(status_code=415, detail="Content-Type must be application/xml")
    xml_content = await request.body()
    if not xml_content:
        raise HTTPException(status_code=400, detail="XML content is required")
    if not os.path.exists(D390_TEMPLATE):
        raise HTTPException(status_code=500, detail="PDF template not found")
    try:
        pdf_bytes = generate_d390_pdf(xml_content, D390_TEMPLATE, attach_xml)
        return Response(content=pdf_bytes, media_type="application/pdf",
                        headers={"Content-Disposition": "attachment; filename=D390.pdf"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")


# ============== D394 ==============

@app.post("/api/v1/d394/generate")
async def generate_d394(request: Request, attach_xml: bool = True):
    content_type = request.headers.get("content-type", "")
    if "xml" not in content_type.lower() and "text" not in content_type.lower():
        raise HTTPException(status_code=415, detail="Content-Type must be application/xml")
    xml_content = await request.body()
    if not xml_content:
        raise HTTPException(status_code=400, detail="XML content is required")
    if not os.path.exists(D394_TEMPLATE):
        raise HTTPException(status_code=500, detail="PDF template not found")
    try:
        pdf_bytes = generate_d394_pdf(xml_content, D394_TEMPLATE, attach_xml)
        return Response(content=pdf_bytes, media_type="application/pdf",
                        headers={"Content-Disposition": "attachment; filename=D394.pdf"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")
