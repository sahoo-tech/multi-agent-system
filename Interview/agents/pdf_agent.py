import io
import re
from pypdf import PdfReader

class PDFAgent:
    def __init__(self, memory):
        self.memory = memory

    def process(self, pdf_bytes):
        """
        Enhanced PDF processing:
        - Extract text from PDF bytes
        - Parse line-item invoice data (simple regex-based)
        - Detect invoice total and flag if > 10,000
        - Detect policy mentions like GDPR, FDA and flag compliance risk
        - Return extracted data and flags
        """
        try:
            reader = PdfReader(io.BytesIO(pdf_bytes))
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
        except Exception as e:
            return {"error": "Failed to process PDF", "details": str(e)}

        # Parse invoice line items (dummy example: look for lines with item, qty, price)
        invoice_lines = []
        invoice_total = 0.0
        invoice_pattern = re.compile(r"(?P<item>\w+)\s+(?P<qty>\d+)\s+\$?(?P<price>[\d,.]+)")
        
        # Find all invoice line items
        for match in invoice_pattern.finditer(text):
            try:
                item = match.group('item')
                qty = int(match.group('qty'))
                price_str = match.group('price').replace(',', '')
                price = float(price_str)
                line_total = qty * price
                invoice_lines.append({
                    'item': item,
                    'quantity': qty,
                    'price': price,
                    'total': line_total
                })
                invoice_total += line_total
            except (ValueError, AttributeError) as e:
                # Skip invalid line items
                continue

        # Detect policy mentions
        policy_flags = []
        policy_keywords = ["GDPR", "FDA", "HIPAA", "CCPA"]
        for keyword in policy_keywords:
            if keyword.lower() in text.lower():
                policy_flags.append(keyword)

        flags = []
        if invoice_total > 10000:
            flags.append("High Invoice Total")
        if policy_flags:
            flags.append(f"Policy Mentions: {', '.join(policy_flags)}")

        result = {
            "extracted_text": text,
            "num_pages": len(reader.pages),
            "invoice_lines": invoice_lines,
            "invoice_total": invoice_total,
            "policy_flags": policy_flags,
            "flags": flags
        }

        # Store extracted fields in shared memory
        try:
            self.memory.add_extracted_fields("PDFAgent", result)
        except Exception as e:
            print(f"Warning: Failed to store PDF data: {e}")

        return result
