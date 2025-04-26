"""
PDF Generator for TariffDoc AI

This module handles the generation of PDF documents containing tariff information.
"""

import os
import io
from datetime import datetime
from typing import Dict, List, Any, Optional, BinaryIO
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image

class PDFGenerator:
    """Generator for tariff information PDF documents."""
    
    def __init__(self, logo_path: Optional[str] = None):
        """
        Initialize the PDF generator.
        
        Args:
            logo_path: Path to the logo image file
        """
        self.styles = getSampleStyleSheet()
        self.logo_path = logo_path
        
        # Create custom styles with unique names
        self.styles.add(ParagraphStyle(
            name='TariffHeading1',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=12
        ))
        
        self.styles.add(ParagraphStyle(
            name='TariffHeading2',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=10
        ))
        
        self.styles.add(ParagraphStyle(
            name='TariffNormal',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=8
        ))
        
        self.styles.add(ParagraphStyle(
            name='TariffItalic',
            parent=self.styles['Italic'],
            fontSize=10,
            spaceAfter=8
        ))
        
        self.styles.add(ParagraphStyle(
            name='TariffBold',
            parent=self.styles['Normal'],
            fontSize=10,
            fontName='Helvetica-Bold',
            spaceAfter=8
        ))
        
        self.styles.add(ParagraphStyle(
            name='TariffSmallText',
            parent=self.styles['Normal'],
            fontSize=8,
            spaceAfter=6
        ))
    
    def generate_tariff_document(self, 
                                tariff_data: Dict[str, Any], 
                                output_path: Optional[str] = None) -> BinaryIO:
        """
        Generate a PDF document with tariff information.
        
        Args:
            tariff_data: Dictionary containing tariff information
            output_path: Path to save the PDF file (if None, returns a file-like object)
            
        Returns:
            File-like object containing the PDF data if output_path is None,
            otherwise returns None and saves the PDF to the specified path
        """
        # Create a file-like object to receive PDF data
        buffer = io.BytesIO()
        
        # Create the PDF document
        doc = SimpleDocTemplate(
            buffer if output_path is None else output_path,
            pagesize=letter,
            rightMargin=0.5*inch,
            leftMargin=0.5*inch,
            topMargin=0.5*inch,
            bottomMargin=0.5*inch
        )
        
        # Build the document content
        story = []
        
        # Add header with logo
        self._add_header(story)
        
        # Add product information section
        self._add_product_info(story, tariff_data)
        
        # Add classification analysis if available
        if "classification_analysis" in tariff_data:
            self._add_classification_analysis(story, tariff_data)
        
        # Add tariff details section
        self._add_tariff_details(story, tariff_data)
        
        # Add trade agreement section
        self._add_trade_agreements(story, tariff_data)
        
        # Add explanation section if available
        if "explanation" in tariff_data:
            self._add_explanation(story, tariff_data["explanation"])
        
        # Add source information and footer
        self._add_source_info(story, tariff_data)
        self._add_footer(story)
        
        # Build the PDF
        doc.build(story)
        
        # If output_path is None, return the buffer
        if output_path is None:
            buffer.seek(0)
            return buffer
        
        return None
    
    def _add_classification_analysis(self, story: List[Any], tariff_data: Dict[str, Any]) -> None:
        """Add the classification analysis section."""
        story.append(Paragraph("Classification Analysis", self.styles["TariffHeading2"]))
        
        analysis = tariff_data.get("classification_analysis", {})
        
        # Create a table for the analysis
        analysis_data = []
        
        # Add materials
        materials = analysis.get("materials", [])
        if materials:
            if isinstance(materials, list):
                materials_str = ", ".join(materials)
            else:
                materials_str = str(materials)
            analysis_data.append(["Materials:", materials_str])
        
        # Add function
        function = analysis.get("function", "")
        if function:
            analysis_data.append(["Function:", function])
        
        # Add industry terms
        industry_terms = analysis.get("industry_terms", [])
        if industry_terms:
            if isinstance(industry_terms, list):
                terms_str = ", ".join(industry_terms)
            else:
                terms_str = str(industry_terms)
            analysis_data.append(["Industry Terms:", terms_str])
        
        # Add confidence reasoning
        confidence_reason = analysis.get("confidence_reason", "")
        if confidence_reason:
            analysis_data.append(["Classification Reasoning:", confidence_reason])
        
        # Create the table if we have data
        if analysis_data:
            analysis_table = Table(analysis_data, colWidths=[1.5*inch, 5.5*inch])
            analysis_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
            ]))
            
            story.append(analysis_table)
            story.append(Spacer(1, 0.2*inch))
    
    def _add_header(self, story: List[Any]) -> None:
        """Add the document header with logo."""
        # Create a table for the header with logo and title
        header_data = []
        
        # Add logo if available
        if self.logo_path and os.path.exists(self.logo_path):
            img = Image(self.logo_path, width=1.5*inch, height=0.5*inch)
            header_data.append([img, Paragraph("TariffDoc AI", self.styles["TariffHeading1"])])
        else:
            header_data.append([Paragraph("TariffDoc AI", self.styles["TariffHeading1"])])
        
        # Create the header table
        if len(header_data[0]) == 1:
            # No logo, use full width for title
            header_table = Table(header_data, colWidths=[7*inch])
        else:
            # With logo, split width
            header_table = Table(header_data, colWidths=[1.5*inch, 5.5*inch])
        
        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (1, 0), (1, 0), 'LEFT'),
        ]))
        
        story.append(header_table)
        story.append(Paragraph("Tariff Classification Summary", self.styles["TariffHeading2"]))
        story.append(Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y at %H:%M:%S')}", self.styles["TariffItalic"]))
        story.append(Spacer(1, 0.2*inch))
    
    def _add_product_info(self, story: List[Any], tariff_data: Dict[str, Any]) -> None:
        """Add the product information section."""
        story.append(Paragraph("Product Information", self.styles["TariffHeading2"]))
        
        # Extract product information
        product_desc = tariff_data.get("product_description", "N/A")
        hts_code = tariff_data.get("hts_code", "N/A")
        hts_desc = tariff_data.get("hts_description", "N/A")
        
        # Create a table for product information
        product_data = [
            ["Product Description:", product_desc],
            ["HTS Code:", hts_code],
            ["HTS Description:", hts_desc]
        ]
        
        product_table = Table(product_data, colWidths=[1.5*inch, 5.5*inch])
        product_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
        ]))
        
        story.append(product_table)
        story.append(Spacer(1, 0.2*inch))
    
    def _add_tariff_details(self, story: List[Any], tariff_data: Dict[str, Any]) -> None:
        """Add the tariff details section."""
        story.append(Paragraph("Tariff Details", self.styles["TariffHeading2"]))
        
        # Extract tariff rates
        rates = tariff_data.get("rates", {})
        general_rate = rates.get("general", "N/A")
        column2_rate = rates.get("column2", "N/A")
        special_rates = rates.get("special", {})
        
        # Format special rates for display
        special_rates_text = ""
        if special_rates:
            for country, rate in special_rates.items():
                special_rates_text += f"{country}: {rate}, "
            special_rates_text = special_rates_text.rstrip(", ")
        else:
            special_rates_text = "None"
        
        # Create a table for tariff details
        tariff_details = [
            ["General Rate of Duty:", general_rate],
            ["Special Rates:", special_rates_text],
            ["Column 2 Rate:", column2_rate]
        ]
        
        # Add unit of quantity if available
        unit = tariff_data.get("unit_of_quantity", "")
        if unit:
            tariff_details.append(["Unit of Quantity:", unit])
        
        tariff_table = Table(tariff_details, colWidths=[1.5*inch, 5.5*inch])
        tariff_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
        ]))
        
        story.append(tariff_table)
        story.append(Spacer(1, 0.2*inch))
    
    def _add_trade_agreements(self, story: List[Any], tariff_data: Dict[str, Any]) -> None:
        """Add the trade agreement section."""
        trade_info = tariff_data.get("trade_agreements", {})
        
        if not trade_info or not trade_info.get("eligible_agreements"):
            story.append(Paragraph("Trade Agreement Eligibility", self.styles["TariffHeading2"]))
            story.append(Paragraph("No eligible trade agreements identified for this product and country combination.", self.styles["TariffNormal"]))
            story.append(Spacer(1, 0.2*inch))
            return
        
        story.append(Paragraph("Trade Agreement Eligibility", self.styles["TariffHeading2"]))
        
        # Extract eligible agreements
        eligible_agreements = trade_info.get("eligible_agreements", [])
        
        # Create table headers
        agreement_data = [["Agreement", "Rate", "Requirements"]]
        
        # Add each agreement to the table
        for agreement in eligible_agreements:
            agreement_data.append([
                agreement.get("agreement", "N/A"),
                agreement.get("rate", "N/A"),
                agreement.get("requirements", "N/A")
            ])
        
        # Create the table
        agreement_table = Table(agreement_data, colWidths=[2*inch, 1*inch, 4*inch])
        agreement_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
        ]))
        
        story.append(agreement_table)
        story.append(Spacer(1, 0.2*inch))
    
    def _add_explanation(self, story: List[Any], explanation: str) -> None:
        """Add the explanation section."""
        story.append(Paragraph("Expert Analysis", self.styles["TariffHeading2"]))
        story.append(Paragraph(explanation, self.styles["TariffNormal"]))
        story.append(Spacer(1, 0.2*inch))
    
    def _add_source_info(self, story: List[Any], tariff_data: Dict[str, Any]) -> None:
        """Add the source information section."""
        story.append(Paragraph("Source Information", self.styles["TariffHeading2"]))
        
        # Create a table for source information
        source_data = [
            ["Data Source:", "USITC Harmonized Tariff Schedule"],
            ["Last Updated:", datetime.now().strftime("%B %d, %Y")],
            ["Document ID:", f"TDA-{datetime.now().strftime('%Y%m%d%H%M%S')}"]
        ]
        
        source_table = Table(source_data, colWidths=[1.5*inch, 5.5*inch])
        source_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
        ]))
        
        story.append(source_table)
        story.append(Spacer(1, 0.2*inch))
    
    def _add_footer(self, story: List[Any]) -> None:
        """Add the document footer."""
        disclaimer = (
            "DISCLAIMER: This document is provided for informational purposes only and does not constitute "
            "legal advice. The information contained herein is believed to be accurate as of the date of "
            "generation, but tariff classifications and duty rates are subject to change. Users should "
            "consult with a licensed customs broker or trade attorney for specific guidance. "
            "Generated by TariffDoc AI, powered by Multifactor AI."
        )
        
        story.append(Paragraph(disclaimer, self.styles["TariffSmallText"]))
