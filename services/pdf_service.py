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
        Generates a PDF for the given invoice data.
        
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
        # Ensure we work with floats/decimals
        subtotal = sum(float(i['total_price']) for i in items)
        vat_rate = float(invoice_data.get('vat_rate', 13) or 13)
        discount_pct = float(invoice_data.get('discount', 0) or 0)
        paid_amt = float(invoice_data.get('paid_amount', 0) or 0) # Handle key name difference helper
        
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

        # ── Draw two copies: top half and bottom half ──
        self._draw_copy(c, height - 55, context)
        
        # Dotted cut line in the middle
        c.setDash(3, 3)
        c.setStrokeColorRGB(0.5, 0.5, 0.5)
        c.setLineWidth(0.5)
        c.line(20, height / 2, width - 20, height / 2)
        c.setFont("Courier", 6)
        c.setFillColorRGB(0.5, 0.5, 0.5)
        c.drawCentredString(width / 2, height / 2 + 3, "--- CUT HERE ---")
        c.setDash()  # Reset dash
        
        self._draw_copy(c, height / 2 - 25, context)

        c.save()
        return pdf_path

    def _draw_copy(self, c, start_y, context):
        """Draw one invoice copy (half-page)."""
        invoice_data = context["invoice_data"]
        items = context["items"]
        calc = context["calculations"]
        width = context["width"]
        height = context["height"]

        # ── Column positions ──
        LEFT = 40
        RIGHT = width - 40
        COL_SN = LEFT + 5
        COL_DESC = LEFT + 35
        COL_HS = LEFT + 260
        COL_QTY = LEFT + 340
        COL_RATE = LEFT + 395
        COL_AMT = RIGHT - 5
        TABLE_W = RIGHT - LEFT

        c.setFillColorRGB(0, 0, 0)

        # ═══ OUTER BORDER ═══
        copy_height = (height / 2) - 30
        c.setStrokeColorRGB(0, 0, 0)
        c.setLineWidth(1)
        c.rect(LEFT, start_y - copy_height + 20, TABLE_W, copy_height)

        y = start_y

        # ═══ COMPANY HEADER ═══
        # Logo path - assume it's in the project root
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        logo_path = os.path.join(project_root, "moonal_blackwhite.png")
        
        try:
            logo_w, logo_h = 80, 22
            c.drawImage(logo_path, LEFT + 8, y - 5, width=logo_w, height=logo_h,
                        preserveAspectRatio=True, mask='auto')
            company_x = LEFT + logo_w + 15
        except Exception:
            company_x = LEFT + 8

        c.setFont("Courier-Bold", 14)
        c.drawString(company_x, y, invoice_data.get("company_name", Settings.COMPANY_NAME))
        c.setFont("Courier", 8)
        y -= 12
        c.drawString(company_x, y, invoice_data.get("company_address", Settings.COMPANY_ADDRESS))
        y -= 10
        c.drawString(company_x, y, f"PAN/VAT No: {invoice_data.get('company_pan', Settings.COMPANY_PAN)}")

        # TAX INVOICE title (right side)
        c.setFont("Courier-Bold", 14)
        is_credit_note = invoice_data.get('is_credit_note', False)
        title = "CREDIT NOTE" if is_credit_note else "TAX INVOICE"
        c.drawRightString(RIGHT - 8, start_y, title)
        c.setFont("Courier", 9)
        c.drawRightString(RIGHT - 8, start_y - 12, f"Invoice No : {invoice_data.get('invoice_number', '')}")
        
        # Use current date for print date or invoice date? Usually print date.
        c.drawRightString(RIGHT - 8, start_y - 22, f"Date       : {datetime.now().strftime('%Y-%m-%d')}")

        # Separator line
        y -= 12
        c.setLineWidth(0.5)
        c.line(LEFT, y, RIGHT, y)

        # ═══ CUSTOMER INFO ═══
        y -= 12
        c.setFont("Courier", 9)
        c.drawString(LEFT + 8, y, f"Customer : {invoice_data.get('client_name', '')}")
        c.drawRightString(RIGHT - 8, y, f"Contact: {invoice_data.get('client_contact', '') or ''}")
        y -= 12
        c.drawString(LEFT + 8, y, f"Address  : {invoice_data.get('address', '') or ''}")
        pan_val = invoice_data.get('pan_no', '') or ''
        if pan_val:
            c.drawRightString(RIGHT - 8, y, f"PAN/VAT: {pan_val}")

        # Separator
        y -= 8
        c.setLineWidth(0.5)
        c.line(LEFT, y, RIGHT, y)

        # ═══ TABLE HEADER ═══
        y -= 12
        c.setFont("Courier-Bold", 8)
        c.drawString(COL_SN, y, "S.N.")
        c.drawString(COL_DESC, y, "DESCRIPTION")
        c.drawString(COL_HS, y, "HS CODE")
        c.drawString(COL_QTY, y, "QTY")
        c.drawString(COL_RATE, y, "RATE")
        c.drawRightString(COL_AMT, y, "AMOUNT")

        y -= 5
        c.line(LEFT, y, RIGHT, y)

        # ═══ TABLE BODY ═══
        c.setFont("Courier", 9)
        for idx, item in enumerate(items, 1):
            y -= 13
            c.drawString(COL_SN, y, f"{idx:>2}.")
            # Truncate long names
            product_name = item.get('product_name', '') or ''
            name = product_name[:28]
            c.drawString(COL_DESC, y, name)
            c.drawString(COL_HS, y, str(item.get('hs_code', '') or ''))
            c.drawRightString(COL_QTY + 25, y, str(item.get('quantity', 0)))
            c.drawRightString(COL_RATE + 45, y, f"{float(item.get('price_per_unit', 0)):>10,.2f}")
            c.drawRightString(COL_AMT, y, f"{float(item.get('total_price', 0)):>10,.2f}")

        # Separator after items
        y -= 8
        c.line(LEFT, y, RIGHT, y)

        # ═══ TOTALS SECTION ═══
        total_label_x = RIGHT - 220
        total_value_x = COL_AMT

        y -= 13
        c.setFont("Courier", 9)
        c.drawString(total_label_x, y, "Sub Total     :")
        c.drawRightString(total_value_x, y, f"Rs. {calc['subtotal']:>12,.2f}")

        if calc['discount_pct'] > 0:
            y -= 12
            c.drawString(total_label_x, y, f"Discount({calc['discount_pct']:.1f}%):")
            c.drawRightString(total_value_x, y, f"Rs. {calc['discount_amt']:>12,.2f}")

        y -= 12
        c.drawString(total_label_x, y, "Taxable Amount:")
        c.drawRightString(total_value_x, y, f"Rs. {calc['taxable']:>12,.2f}")

        y -= 12
        c.drawString(total_label_x, y, f"VAT ({calc['vat_rate']:.0f}%)      :")
        c.drawRightString(total_value_x, y, f"Rs. {calc['vat_amt']:>12,.2f}")

        # Grand total with double underline
        y -= 5
        c.setLineWidth(1)
        c.line(total_label_x, y, RIGHT - 8, y)
        y -= 1
        c.line(total_label_x, y, RIGHT - 8, y)

        y -= 13
        c.setFont("Courier-Bold", 10)
        c.drawString(total_label_x, y, "GRAND TOTAL   :")
        c.drawRightString(total_value_x, y, f"Rs. {calc['grand_total']:>12,.2f}")

        if calc['paid_amt'] > 0:
            y -= 12
            c.setFont("Courier", 9)
            c.drawString(total_label_x, y, "Paid Amount   :")
            c.drawRightString(total_value_x, y, f"Rs. {calc['paid_amt']:>12,.2f}")
            y -= 12
            c.setFont("Courier-Bold", 9)
            c.drawString(total_label_x, y, "Due Amount    :")
            c.drawRightString(total_value_x, y, f"Rs. {calc['due']:>12,.2f}")

        # ═══ AMOUNT IN WORDS ═══
        y -= 16
        c.setFont("Courier", 7)
        c.drawString(LEFT + 8, y, f"In Words: {self.total_in_words(calc['grand_total'])}")

        # ═══ FOOTER ═══
        y -= 20
        c.setFont("Courier", 7)
        c.drawString(LEFT + 8, y, "Goods once sold cannot be taken back.")
        c.setFont("Courier-Bold", 8)
        c.drawRightString(RIGHT - 8, y, "Authorized Signature")
        # Signature line
        c.setLineWidth(0.3)
        c.line(RIGHT - 140, y + 10, RIGHT - 8, y + 10)

        # CANCELLED watermark
        status = invoice_data.get('status', 'ACTIVE')
        if status == 'CANCELLED':
            c.saveState()
            c.setFillColorRGB(0.85, 0.15, 0.15, 0.25)  # Semi-transparent red
            c.setFont("Courier-Bold", 40)
            c.translate((LEFT + RIGHT) / 2, start_y - copy_height / 2)
            c.rotate(35)
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
