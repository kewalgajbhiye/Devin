"""
DBF File Parser for Visual FoxPro files
"""

import struct
from datetime import datetime

class DBFParser:
    def __init__(self, filepath):
        self.filepath = filepath
        self.fields = []
        self.records = []
        
    def parse(self):
        """Parse the DBF file and return records"""
        try:
            with open(self.filepath, 'rb') as f:
                header = f.read(32)
                
                record_count = struct.unpack('<I', header[4:8])[0]
                header_length = struct.unpack('<H', header[8:10])[0]
                record_length = struct.unpack('<H', header[10:12])[0]
                
                f.seek(32)
                self.fields = []
                while True:
                    field_desc = f.read(32)
                    if field_desc[0] == 0x0D:
                        break
                    field_name = field_desc[:11].rstrip(b'\x00').decode('ascii')
                    field_type = chr(field_desc[11])
                    field_length = field_desc[16]
                    self.fields.append((field_name, field_type, field_length))
                
                self.records = []
                for i in range(record_count):
                    record = f.read(record_length)
                    if record[0] != 0x2A:
                        record_data = {}
                        pos = 1
                        for field_name, field_type, field_length in self.fields:
                            value = record[pos:pos+field_length].rstrip(b'\x00 ').decode('ascii', errors='ignore')
                            
                            if field_type == 'N':
                                try:
                                    record_data[field_name] = float(value) if '.' in value else int(value)
                                except ValueError:
                                    record_data[field_name] = 0
                            elif field_type == 'D':
                                try:
                                    if len(value) == 8:
                                        record_data[field_name] = datetime.strptime(value, '%Y%m%d').date()
                                    else:
                                        record_data[field_name] = None
                                except ValueError:
                                    record_data[field_name] = None
                            else:
                                record_data[field_name] = value.strip()
                            
                            pos += field_length
                        
                        self.records.append(record_data)
                
                return self.records
                
        except Exception as e:
            print(f"Error parsing DBF file: {e}")
            return []
    
    def get_field_names(self):
        """Get list of field names"""
        return [field[0] for field in self.fields]
