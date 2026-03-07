import os
import subprocess
import platform
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime
import num2words
from decimal import Decimal

from config.settings import Settings

class PDFService:
    def __init__(self, output_dir=None):
        if output_dir is None:
            # Use APP_DIR_NAME or just project root logic? Project root logic seems safer for now as output_dir is relative to project.
            # But the user might want outputs in the secure dir?
            # For now, keep project root logic but use Settings for company info.
            self.output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "outputs")
        else:
            self.output_dir = output_dir
            
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def generate_invoice_pdf(self, invoice_data, items):
        """
        Generates a professional full-page A4 PDF for the given invoice data.
        
        :param invoice_data: Dictionary containing invoice details (number, client, totals, etc.)
        :param items: List of dictionaries containing invoice items
        :return: Path to the generated PDF
        """
        invoice_number = invoice_data.get("invoice_number", "UNKNOWN")
        safe_filename = invoice_number.replace("/", "_").replace("\\", "_")
        pdf_path = os.path.join(self.output_dir, f"Invoice_{safe_filename}.pdf")
        
        c = canvas.Canvas(pdf_path, pagesize=A4)
        width, height = A4
        
        # Precompute tax breakdown
        subtotal = sum(float(i['total_price']) for i in items)
        vat_rate = float(invoice_data.get('vat_rate', 13) or 13)
        discount_pct = float(invoice_data.get('discount', 0) or 0)
        paid_amt = float(invoice_data.get('paid_amount', 0) or 0)
        
        # Calculate amounts
        discount_amt = subtotal * (discount_pct / 100)
        taxable = subtotal - discount_amt
        vat_amt = taxable * (vat_rate / 100)
        grand_total = taxable + vat_amt
        due = grand_total - paid_amt

        # Context for drawing
        context = {
            "invoice_data": invoice_data,
            "items": items,
            "calculations": {
                "subtotal": subtotal,
                "discount_pct": discount_pct,
                "discount_amt": discount_amt,
                "taxable": taxable,
                "vat_rate": vat_rate,
                "vat_amt": vat_amt,
                "grand_total": grand_total,
                "paid_amt": paid_amt,
                "due": due
            },
            "width": width,
            "height": height
        }

        # ── Draw One Full Copy ──
        self._draw_full_page(c, height - 50, context)

        c.save()
        return pdf_path

    def _draw_full_page(self, c, start_y, context):
        """Draw a fully structured, professional full-page A4 invoice."""
        invoice_data = context["invoice_data"]
        items = context["items"]
        calc = context["calculations"]
        width = context["width"]
        height = context["height"]

        # ── EXTREME PRECISION BALANCED COLUMN GRID ──
        LEFT = 50
        RIGHT = width - 50
        TABLE_W = RIGHT - LEFT
        
        # Recalibrated X-slots for visual balance
        X_SN = LEFT
        X_DESC = LEFT + 30
        X_HS = X_DESC + 155
        X_QTY = X_HS + 60
        X_UNIT = X_QTY + 35
        X_RATE = X_UNIT + 40
        X_TOTAL = X_RATE + 85
        
        c.setFillColorRGB(0, 0, 0)
        y = start_y

        # ═══ PREMIUM HEADER ═══
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        logo_path = os.path.join(project_root, "moonal_blackwhite.png")
        
        try:
            logo_w, logo_h = 125, 42
            c.drawImage(logo_path, LEFT, y-10, width=logo_w, height=logo_h,
                        preserveAspectRatio=True, mask='auto')
        except Exception:
            pass

        c.setFont("Helvetica-Bold", 32)
        c.setFillColorRGB(0.1, 0.1, 0.1)
        c.drawRightString(RIGHT, y, "INVOICE")
        
        y -= 52
        c.setFillColorRGB(0, 0, 0)
        c.setFont("Helvetica-Bold", 16)
        c.drawString(LEFT, y, invoice_data.get("company_name", Settings.COMPANY_NAME).upper())
        
        y -= 16
        c.setFont("Helvetica", 11)
        c.drawString(LEFT, y, invoice_data.get("company_address", Settings.COMPANY_ADDRESS))
        
        # Consolidated Info Row
        y -= 15
        c.setStrokeColorRGB(0.75, 0.75, 0.75)
        c.setLineWidth(0.8)
        c.line(LEFT, y, RIGHT, y)
        
        y -= 12
        c.setFont("Helvetica-Bold", 8.5)
        company_pan = invoice_data.get('company_pan', Settings.COMPANY_PAN)
        company_contact = invoice_data.get('company_contact', getattr(Settings, 'COMPANY_CONTACT', ''))
        company_email = invoice_data.get('company_email', getattr(Settings, 'COMPANY_EMAIL', ''))
        
        info_str = f"VAT/PAN: {company_pan}     |     PHONE: {company_contact}     |     EMAIL: {company_email}"
        c.drawCentredString(width/2, y, info_str)
        
        y -= 5
        c.line(LEFT, y, RIGHT, y)
        
        # ═══ INVOICE INFO BOX (Widened to 200pt, 60/40 Split) ═══
        box_y = start_y - 12
        box_w = 200
        box_h = 44
        box_x = RIGHT - box_w
        box_split_x = box_x + 120 # 60% of 200
        
        c.setLineWidth(1)
        c.setStrokeColorRGB(0, 0, 0)
        c.rect(box_x, box_y - box_h, box_w, box_h, fill=0)
        c.line(box_split_x, box_y, box_split_x, box_y - box_h)
        c.line(box_x, box_y - 22, box_x + box_w, box_y - 22)
        
        c.setFont("Helvetica-Bold", 8.5)
        c.drawCentredString(box_x + 60, box_y - 14, "INVOICE #")
        c.drawCentredString(box_split_x + 40, box_y - 14, "DATE")
        c.setFont("Helvetica", 10.5)
        c.drawCentredString(box_x + 60, box_y - 35, str(invoice_data.get('invoice_number', '')))
        c.drawCentredString(box_split_x + 40, box_y - 35, datetime.now().strftime('%d/%m/%Y'))

        # ═══ ADDRESS BLOCK (Structured Labels) ═══
        y -= 45
        c.saveState()
        c.setFillColorRGB(0.15, 0.15, 0.15)
        c.rect(LEFT, y - 5, 230, 18, fill=1, stroke=0)
        c.restoreState()
        
        c.setFont("Helvetica-Bold", 10)
        c.setFillColorRGB(1, 1, 1)
        c.drawString(LEFT + 5, y, "CLIENT INFORMATION (BILL TO)")
        c.setFillColorRGB(0, 0, 0)
        
        y -= 22
        c.setFont("Helvetica", 10.5)
        c.drawString(LEFT + 5, y, "Name:")
        c.setFont("Helvetica-Bold", 11)
        c.drawString(LEFT + 60, y, str(invoice_data.get('client_name', '')).upper())
        
        y -= 16
        c.setFont("Helvetica", 10.5)
        c.drawString(LEFT + 5, y, "Address:")
        c.drawString(LEFT + 60, y, str(invoice_data.get('address', '') or ''))
        
        y -= 16
        c.drawString(LEFT + 5, y, "Contact:")
        c.drawString(LEFT + 60, y, str(invoice_data.get('client_contact', '') or 'N/A'))
        
        y -= 16
        pan_val = invoice_data.get('pan_no', '')
        if pan_val:
            c.drawString(LEFT + 5, y, "VAT/PAN:")
            c.drawString(LEFT + 60, y, str(pan_val))

        # ═══ TABLE HEADER (Rigorous Balanced Widths) ═══
        y -= 35
        c.saveState()
        c.setFillColorRGB(0.12, 0.12, 0.12)
        c.rect(LEFT, y - 5, TABLE_W, 26, fill=1, stroke=0)
        c.restoreState()
        
        c.setFillColorRGB(1, 1, 1)
        c.setFont("Helvetica-Bold", 9.5)
        c.drawString(X_SN + 5, y + 2, "S.N.")
        c.drawString(X_DESC + 5, y + 2, "PARTICULARS")
        c.drawString(X_HS + 5, y + 2, "HS CODE")
        c.drawString(X_QTY + 5, y + 2, "QTY")
        c.drawString(X_UNIT + 5, y + 2, "UNIT")
        c.drawString(X_RATE + 5, y + 2, "RATE (Rs.)")
        c.drawRightString(RIGHT - 5, y + 2, "TOTAL (Rs.)")
        c.setFillColorRGB(0, 0, 0)

        y -= 5
        c.setLineWidth(1)
        c.line(LEFT, y, RIGHT, y)

        # ═══ TABLE BODY (Precision Alignment) ═══
        y_table_start = y + 26
        c.setFont("Helvetica", 10)
        row_h = 24
        for idx, item in enumerate(items, 1):
            y -= row_h
            if y < 190: 
                 break
            # Row separator
            c.setStrokeColorRGB(0.8, 0.8, 0.8)
            c.setLineWidth(0.5)
            c.line(LEFT, y-5, RIGHT, y-5)
            c.setStrokeColorRGB(0, 0, 0)
            
            c.drawString(X_SN + 5, y, f"{idx:>2}.")
            product_name = item.get('product_name', '') or ''
            c.drawString(X_DESC + 5, y, product_name[:26])
            c.drawString(X_HS + 5, y, str(item.get('hs_code', '') or ''))
            c.drawRightString(X_QTY + 30, y, str(item.get('quantity', 0)))
            c.drawString(X_UNIT + 5, y, str(item.get('unit', 'Ltr')))
            
            # Rate & Total: Right-aligned within their 85pt+ containers
            c.drawRightString(X_RATE + 80, y, f"{float(item.get('price_per_unit', 0)):,.2f}")
            c.drawRightString(RIGHT - 5, y, f"{float(item.get('total_price', 0)):,.2f}")

        # Vertical Grid Lines
        table_bottom = y - 5
        c.setLineWidth(1)
        c.line(LEFT, y_table_start, LEFT, table_bottom)
        c.line(RIGHT, y_table_start, RIGHT, table_bottom)
        
        c.setLineWidth(0.5)
        c.line(X_DESC, y_table_start, X_DESC, table_bottom)
        c.line(X_HS, y_table_start, X_HS, table_bottom)
        c.line(X_QTY, y_table_start, X_QTY, table_bottom)
        c.line(X_UNIT, y_table_start, X_UNIT, table_bottom)
        c.line(X_RATE, y_table_start, X_RATE, table_bottom)
        c.line(X_TOTAL, y_table_start, X_TOTAL, table_bottom)
        
        y = table_bottom
        c.setLineWidth(1)
        c.line(LEFT, y, RIGHT, y)

        # ═══ FORMAL TOTALS TABLE ═══
        row_y = y - 25
        total_w = 210
        total_x = RIGHT - total_w
        label_x = total_x + 10
        value_x = RIGHT - 10
        col_sep_x = total_x + 120
        
        ty = row_y + 18
        c.setLineWidth(1)
        c.rect(total_x, ty - 87, total_w, 87)
        c.line(col_sep_x, ty, col_sep_x, ty - 87)
        
        c.setFont("Helvetica-Bold", 9.5)
        c.drawString(label_x, row_y + 4, "SUBTOTAL")
        c.drawRightString(value_x, row_y + 4, f"{calc['subtotal']:,.2f}")
        c.line(total_x, row_y - 2, RIGHT, row_y - 2)
        
        row_y -= 21
        c.setFont("Helvetica", 9.5)
        c.drawString(label_x, row_y + 4, f"DISCOUNT ({calc['discount_pct']:.1f}%)")
        c.drawRightString(value_x, row_y + 4, f"{calc['discount_amt']:,.2f}")
        c.line(total_x, row_y - 2, RIGHT, row_y - 2)
        
        row_y -= 21
        c.drawString(label_x, row_y + 4, f"VAT ({calc['vat_rate']:.0f}%)")
        c.drawRightString(value_x, row_y + 4, f"{calc['vat_amt']:,.2f}")
        c.line(total_x, row_y - 2, RIGHT, row_y - 2)
        
        row_y -= 24
        c.saveState()
        c.setFillColorRGB(0.96, 0.96, 0.96)
        c.rect(total_x, ty-87, total_w, 23, fill=1, stroke=0)
        c.restoreState()
        
        c.setFont("Helvetica-Bold", 11)
        c.drawString(label_x, row_y + 6, "GRAND TOTAL")
        c.drawRightString(value_x, row_y + 6, f"Rs. {calc['grand_total']:,.2f}")

        # ═══ AMOUNT IN WORDS (Spaced Layout) ═══
        y_words = ty - 110
        c.setFont("Helvetica-Bold", 10)
        c.drawString(LEFT, y_words, "TOTAL IN WORDS:")
        c.setFont("Helvetica", 10)
        words_val = self.total_in_words(calc['grand_total'])
        c.drawString(LEFT + 120, y_words, words_val)

        # ═══ FOOTER & SIGNATURE ═══
        y_footer = 125
        c.setFont("Helvetica-Bold", 9.5)
        c.drawString(LEFT, y_footer, "TERMS & CONDITIONS")
        y_footer -= 15
        c.setFont("Helvetica", 8.5)
        terms = [
            "  • Product quality is guaranteed only if the original seal is intact.",
            "  • Any query regarding this invoice must be raised within 3 working days.",
            "  • Unopened packs can be returned within 7 days for quality inspection.",
            "  • This is a computer generated invoice and does not require a stamp."
        ]
        for t in terms:
            c.drawString(LEFT, y_footer, t)
            y_footer -= 12

        y_sig = 75
        c.setFont("Helvetica-Bold", 11)
        c.drawRightString(RIGHT, y_sig, "For MOONAL UDHYOG PVT. LTD.")
        y_sig -= 40
        c.setLineWidth(1)
        c.line(RIGHT-170, y_sig, RIGHT, y_sig)
        y_sig -= 14
        c.drawRightString(RIGHT-35, y_sig, "Authorized Signatory")

        # Watermark
        status = invoice_data.get('status', 'ACTIVE')
        if status == 'CANCELLED':
            c.saveState()
            c.setFillColorRGB(1, 0.05, 0.05, 0.1)
            c.setFont("Helvetica-Bold", 110)
            c.translate(width / 2, height / 2)
            c.rotate(45)
            c.drawCentredString(0, 0, "CANCELLED")
            c.restoreState()

        # Watermark
        status = invoice_data.get('status', 'ACTIVE')
        if status == 'CANCELLED':
            c.saveState()
            c.setFillColorRGB(1, 0.1, 0.1, 0.12)
            c.setFont("Helvetica-Bold", 110)
            c.translate(width / 2, height / 2)
            c.rotate(45)
            c.drawCentredString(0, 0, "CANCELLED")
            c.restoreState()

        # Watermark
        status = invoice_data.get('status', 'ACTIVE')
        if status == 'CANCELLED':
            c.saveState()
            c.setFillColorRGB(1, 0.2, 0.2, 0.15)
            c.setFont("Helvetica-Bold", 110)
            c.translate(width / 2, height / 2)
            c.rotate(45)
            c.drawCentredString(0, 0, "CANCELLED")
            c.restoreState()

    def total_in_words(self, total):
        try:
            total = Decimal(str(total)).quantize(Decimal('0.01'))
            rupees = int(total)
            paisa = int((total - rupees) * 100)
            text = f"{num2words.num2words(rupees, lang='en_IN').title()} Rupees"
            if paisa > 0:
                text += f" And {num2words.num2words(paisa, lang='en_IN').title()} Paisa"
            return text
        except Exception as e:
            return f"{total} (Error converting to words)"
            
    def open_pdf(self, pdf_path):
        """Opens the PDF file using the default system application."""
        if platform.system() == "Linux":
            subprocess.run(["xdg-open", pdf_path])
        elif platform.system() == "Windows":
            os.startfile(pdf_path)
        elif platform.system() == "Darwin":
            subprocess.run(["open", pdf_path])
