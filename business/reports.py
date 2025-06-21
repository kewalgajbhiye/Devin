"""
Report generation and bill printing logic
"""

from datetime import datetime
from typing import List, Dict
from database.queries import DatabaseQueries

class ReportGenerator:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.queries = DatabaseQueries(db_manager)
    
    def generate_purchase_bill(self, bill_no: int) -> Dict:
        """Generate purchase bill with all details"""
        bill_data = self.queries.get_purchase_by_bill_no(bill_no)
        
        if not bill_data:
            return {'error': f'Bill No. {bill_no} not found'}
        
        bill_header = bill_data[0]
        total_amount = sum(float(item['sal_amt']) for item in bill_data)
        total_qty = sum(float(item['qty']) for item in bill_data)
        total_weight = sum(float(item.get('tot_smt', 0)) for item in bill_data)
        
        expenses = {
            'tapaal': float(bill_header.get('exp1', 0)),
            'bhada': float(bill_header.get('exp2', 0)),
            'rail_freight': float(bill_header.get('exp3', 0)),
            'hamali': float(bill_header.get('exp4', 0)),
            'others': float(bill_header.get('exp5', 0)),
            'advance': float(bill_header.get('cash', 0)),
            'other_expenses': float(bill_header.get('other', 0))
        }
        
        total_expenses = sum(expenses.values())
        net_amount = total_amount - total_expenses
        
        return {
            'bill_no': bill_no,
            'bill_date': bill_header['bill_date'],
            'party_name': bill_header['party_nm'],
            'place': bill_header['place'],
            'phone': bill_header['phone'],
            'order_no': bill_header.get('order_no', ''),
            'lr_no': bill_header.get('lr_no', ''),
            'items': bill_data,
            'totals': {
                'total_qty': total_qty,
                'total_weight': total_weight,
                'total_amount': total_amount,
                'total_expenses': total_expenses,
                'net_amount': net_amount
            },
            'expenses': expenses,
            'amount_in_words': self.number_to_words(net_amount)
        }
    
    def number_to_words(self, amount: float) -> str:
        """Convert number to words in Indian format"""
        if amount == 0:
            return "ZERO ONLY"
        
        units = ['', 'ONE', 'TWO', 'THREE', 'FOUR', 'FIVE', 'SIX', 'SEVEN', 'EIGHT', 'NINE',
                'TEN', 'ELEVEN', 'TWELVE', 'THIRTEEN', 'FOURTEEN', 'FIFTEEN', 'SIXTEEN',
                'SEVENTEEN', 'EIGHTEEN', 'NINETEEN', 'TWENTY']
        
        tens = ['', '', 'TWENTY', 'THIRTY', 'FORTY', 'FIFTY', 'SIXTY', 'SEVENTY', 'EIGHTY', 'NINETY']
        
        def convert_hundreds(num):
            result = ""
            if num >= 100:
                result += units[num // 100] + " HUNDRED "
                num %= 100
            
            if num >= 20:
                result += tens[num // 10] + " "
                num %= 10
            
            if num > 0:
                result += units[num] + " "
            
            return result.strip()
        
        amount_str = f"{amount:.2f}"
        rupees, paise = amount_str.split('.')
        rupees = int(rupees)
        paise = int(paise)
        
        words = ""
        
        if rupees >= 10000000:
            crores = rupees // 10000000
            words += convert_hundreds(crores) + " CRORE "
            rupees %= 10000000
        
        if rupees >= 100000:
            lakhs = rupees // 100000
            words += convert_hundreds(lakhs) + " LAKH "
            rupees %= 100000
        
        if rupees >= 1000:
            thousands = rupees // 1000
            words += convert_hundreds(thousands) + " THOUSAND "
            rupees %= 1000
        
        if rupees > 0:
            words += convert_hundreds(rupees)
        
        if paise > 0:
            words += " AND " + convert_hundreds(paise) + " PAISE"
        
        return words.strip() + " ONLY"
    
    def format_bill_for_print(self, bill_data: Dict) -> str:
        """Format bill data for printing"""
        lines = []
        lines.append("=" * 80)
        lines.append("UMESH BALIRAM NIPANE")
        lines.append("Vegetable Merchants & Commission Agent")
        lines.append("Shop No. 15, Gala No.5, Kalamna Sabji Market, Nagpur")
        lines.append("Subject To Nagpur Jurisdiction")
        lines.append("Umesh: 70202 70292, Harish: 88882 12800")
        lines.append("Friday Market Closed")
        lines.append("=" * 80)
        lines.append("")
        
        lines.append(f"To: {bill_data['party_name']}")
        lines.append(f"    {bill_data['place']}")
        lines.append(f"    PH.NO {bill_data['phone']}")
        lines.append("")
        lines.append(f"DATE       : {bill_data['bill_date']}")
        lines.append(f"Total Crate: {bill_data['order_no']}")
        lines.append(f"Lorry.No.  : {bill_data['lr_no']}")
        lines.append(f"Bill  No.  : {bill_data['bill_no']}")
        lines.append("")
        lines.append("-" * 80)
        lines.append("SR. | ITEM NAME             | Bags| CRT/| Weight  | Rate   | Amount")
        lines.append("    |                       |     | BOX |         |        |")
        lines.append("-" * 80)
        
        sr = 1
        for item in bill_data['items']:
            item_name = item['it_nm'][:20]
            lines.append(f"{sr:2d}  | {item_name:<21} | {item['qty']:4.0f}| {item.get('katta', 0):4.0f}| {item.get('tot_smt', 0):8.2f}| {item['rate']:7.2f}| {item['sal_amt']:9.2f}")
            sr += 1
        
        lines.append("-" * 80)
        lines.append(f"Total Qty: {bill_data['totals']['total_qty']:4.0f}     Total Sale: {bill_data['totals']['total_amount']:9.2f}")
        lines.append("-" * 80)
        
        expenses = bill_data['expenses']
        if expenses['others'] > 0:
            lines.append(f"Others.............. {expenses['others']:8.2f}")
        if expenses['tapaal'] > 0:
            lines.append(f"Tapaal.............. {expenses['tapaal']:8.2f}")
        if expenses['bhada'] > 0:
            lines.append(f"Bhada............... {expenses['bhada']:8.2f}")
        if expenses['rail_freight'] > 0:
            lines.append(f"Rail Freight........ {expenses['rail_freight']:8.2f}")
        if expenses['hamali'] > 0:
            lines.append(f"Hamali.............. {expenses['hamali']:8.2f}")
        if expenses['advance'] > 0:
            lines.append(f"Advance............. {expenses['advance']:8.2f}")
        if expenses['other_expenses'] > 0:
            lines.append(f"Expenses............ {expenses['other_expenses']:8.2f}")
        
        lines.append(f"Total Exp........... {bill_data['totals']['total_expenses']:9.2f}")
        lines.append(f"Net Sale............ {bill_data['totals']['net_amount']:9.2f}")
        lines.append("-" * 80)
        lines.append(f"In Words: {bill_data['amount_in_words']}")
        lines.append("=" * 80)
        
        return "\n".join(lines)
