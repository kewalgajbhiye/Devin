"""
Visual FoxPro Data Import Utility
"""

import os
import sqlite3
from pathlib import Path
from datetime import datetime
import struct
from typing import Dict, List, Any

class FoxProImporter:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        
    def read_dbf_file(self, file_path: str) -> List[Dict]:
        """Read DBF file and return records"""
        records = []
        
        try:
            with open(file_path, 'rb') as f:
                header = f.read(32)
                if len(header) < 32:
                    return records
                
                record_count = struct.unpack('<I', header[4:8])[0]
                header_length = struct.unpack('<H', header[8:10])[0]
                record_length = struct.unpack('<H', header[10:12])[0]
                
                f.seek(32)
                field_info = []
                
                while f.tell() < header_length - 1:
                    field_data = f.read(32)
                    if len(field_data) < 32:
                        break
                        
                    field_name = field_data[:11].rstrip(b'\x00').decode('ascii', errors='ignore')
                    field_type = chr(field_data[11])
                    field_length = field_data[16]
                    field_decimal = field_data[17]
                    
                    field_info.append({
                        'name': field_name,
                        'type': field_type,
                        'length': field_length,
                        'decimal': field_decimal
                    })
                
                f.seek(header_length)
                
                for i in range(record_count):
                    record_data = f.read(record_length)
                    if len(record_data) < record_length:
                        break
                        
                    if record_data[0:1] == b'*':
                        continue
                        
                    record = {}
                    offset = 1
                    
                    for field in field_info:
                        field_data = record_data[offset:offset + field['length']]
                        offset += field['length']
                        
                        try:
                            if field['type'] == 'C':
                                value = field_data.rstrip(b'\x00 ').decode('ascii', errors='ignore')
                            elif field['type'] == 'N':
                                value_str = field_data.rstrip(b'\x00 ').decode('ascii', errors='ignore')
                                value = float(value_str) if value_str else 0
                            elif field['type'] == 'D':
                                date_str = field_data.rstrip(b'\x00 ').decode('ascii', errors='ignore')
                                if len(date_str) == 8:
                                    value = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
                                else:
                                    value = None
                            elif field['type'] == 'L':
                                value = field_data[0:1] in [b'T', b't', b'Y', b'y']
                            else:
                                value = field_data.rstrip(b'\x00 ').decode('ascii', errors='ignore')
                                
                            record[field['name'].lower()] = value
                        except:
                            record[field['name'].lower()] = None
                    
                    records.append(record)
                    
        except Exception as e:
            print(f"Error reading DBF file {file_path}: {e}")
            
        return records
    
    def import_parties(self, foxpro_path: str) -> int:
        """Import parties from PARMST.DBF"""
        try:
            parmst_file = os.path.join(foxpro_path, 'VP2122', 'PARMST.DBF')
            if not os.path.exists(parmst_file):
                print(f"PARMST.DBF not found at {parmst_file}")
                return 0
                
            records = self.read_dbf_file(parmst_file)
            
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            imported_count = 0
            
            for record in records:
                try:
                    cursor.execute('''
                        INSERT OR REPLACE INTO parties 
                        (party_cd, party_nm, place, phone, bal_cd, ly_baln, ytd_dr, ytd_cr)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        record.get('party_cd', ''),
                        record.get('party_nm', ''),
                        record.get('place', ''),
                        record.get('phone', ''),
                        record.get('bal_cd', 'D'),
                        record.get('ly_baln', 0),
                        record.get('ytd_dr', 0),
                        record.get('ytd_cr', 0)
                    ))
                    imported_count += 1
                except Exception as e:
                    print(f"Error importing party record: {e}")
                    continue
            
            conn.commit()
            conn.close()
            
            print(f"Imported {imported_count} parties")
            return imported_count
            
        except Exception as e:
            print(f"Error importing parties: {e}")
            return 0
    
    def import_items(self, foxpro_path: str) -> int:
        """Import items from IT.DBF"""
        try:
            it_file = os.path.join(foxpro_path, 'VP2122', 'IT.DBF')
            if not os.path.exists(it_file):
                print(f"IT.DBF not found at {it_file}")
                return 0
                
            records = self.read_dbf_file(it_file)
            
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            imported_count = 0
            
            for record in records:
                try:
                    cursor.execute('''
                        INSERT OR REPLACE INTO items 
                        (it_cd, it_nm, unit, rate, category)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (
                        record.get('it_cd', ''),
                        record.get('it_nm', ''),
                        record.get('unit', 'KG'),
                        record.get('rate', 0),
                        record.get('category', '')
                    ))
                    imported_count += 1
                except Exception as e:
                    print(f"Error importing item record: {e}")
                    continue
            
            conn.commit()
            conn.close()
            
            print(f"Imported {imported_count} items")
            return imported_count
            
        except Exception as e:
            print(f"Error importing items: {e}")
            return 0
    
    def import_purchases(self, foxpro_path: str) -> int:
        """Import purchases from PURC.DBF"""
        try:
            purc_file = os.path.join(foxpro_path, 'VP2122', 'PURC.DBF')
            if not os.path.exists(purc_file):
                print(f"PURC.DBF not found at {purc_file}")
                return 0
                
            records = self.read_dbf_file(purc_file)
            
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            imported_count = 0
            
            for record in records:
                try:
                    cursor.execute('''
                        INSERT OR REPLACE INTO purchases 
                        (bill_no, bill_date, party_cd, it_cd, qty, rate, sal_amt, 
                         exp1, exp2, exp3, exp4, exp5, cash, order_no, lr_no)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        record.get('bill_no', 0),
                        record.get('bill_date'),
                        record.get('party_cd', ''),
                        record.get('it_cd', ''),
                        record.get('qty', 0),
                        record.get('rate', 0),
                        record.get('sal_amt', 0),
                        record.get('exp1', 0),
                        record.get('exp2', 0),
                        record.get('exp3', 0),
                        record.get('exp4', 0),
                        record.get('exp5', 0),
                        record.get('cash', 0),
                        record.get('order_no', ''),
                        record.get('lr_no', '')
                    ))
                    imported_count += 1
                except Exception as e:
                    print(f"Error importing purchase record: {e}")
                    continue
            
            conn.commit()
            conn.close()
            
            print(f"Imported {imported_count} purchases")
            return imported_count
            
        except Exception as e:
            print(f"Error importing purchases: {e}")
            return 0
    
    def import_sales(self, foxpro_path: str) -> int:
        """Import sales from SALE.DBF"""
        try:
            sale_file = os.path.join(foxpro_path, 'VP2122', 'SALE.DBF')
            if not os.path.exists(sale_file):
                print(f"SALE.DBF not found at {sale_file}")
                return 0
                
            records = self.read_dbf_file(sale_file)
            
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            imported_count = 0
            
            for record in records:
                try:
                    cursor.execute('''
                        INSERT OR REPLACE INTO sales 
                        (bill_no, bill_date, party_cd, it_cd, qty, rate, sal_amt,
                         exp1, exp2, exp3, exp4, exp5, cash, order_no, lr_no)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        record.get('bill_no', 0),
                        record.get('bill_date'),
                        record.get('party_cd', ''),
                        record.get('it_cd', ''),
                        record.get('qty', 0),
                        record.get('rate', 0),
                        record.get('sal_amt', 0),
                        record.get('exp1', 0),
                        record.get('exp2', 0),
                        record.get('exp3', 0),
                        record.get('exp4', 0),
                        record.get('exp5', 0),
                        record.get('cash', 0),
                        record.get('order_no', ''),
                        record.get('lr_no', '')
                    ))
                    imported_count += 1
                except Exception as e:
                    print(f"Error importing sales record: {e}")
                    continue
            
            conn.commit()
            conn.close()
            
            print(f"Imported {imported_count} sales")
            return imported_count
            
        except Exception as e:
            print(f"Error importing sales: {e}")
            return 0
    
    def import_all_data(self, foxpro_path: str) -> Dict[str, int]:
        """Import all data from Visual FoxPro files"""
        results = {}
        
        print("Starting Visual FoxPro data import...")
        
        results['parties'] = self.import_parties(foxpro_path)
        results['items'] = self.import_items(foxpro_path)
        results['purchases'] = self.import_purchases(foxpro_path)
        results['sales'] = self.import_sales(foxpro_path)
        
        print("Import completed!")
        return results

def main():
    """Test the import functionality"""
    from config.database import DatabaseManager
    
    db_manager = DatabaseManager()
    importer = FoxProImporter(db_manager)
    
    foxpro_path = input("Enter path to Visual FoxPro data directory: ")
    if not os.path.exists(foxpro_path):
        print(f"Path {foxpro_path} does not exist")
        return
    
    results = importer.import_all_data(foxpro_path)
    
    print("\nImport Results:")
    for table, count in results.items():
        print(f"{table}: {count} records imported")

if __name__ == "__main__":
    main()
