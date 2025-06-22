"""
Report Consistency Manager
Ensures consistent report generation for same date ranges
"""

import hashlib
from datetime import datetime
from database.queries import DatabaseQueries

class ReportConsistencyManager:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.queries = DatabaseQueries(db_manager)
        self._report_cache = {}
    
    def generate_consistent_report(self, report_type, from_date, to_date, **kwargs):
        """Generate consistent report for given parameters"""
        try:
            cache_key = self._generate_cache_key(report_type, from_date, to_date, **kwargs)
            
            if cache_key in self._report_cache:
                cached_report = self._report_cache[cache_key]
                if self._is_cache_valid(cached_report['timestamp']):
                    return cached_report['data']
            
            report_data = self._generate_report_data(report_type, from_date, to_date, **kwargs)
            
            self._report_cache[cache_key] = {
                'data': report_data,
                'timestamp': datetime.now()
            }
            
            return report_data
            
        except Exception as e:
            print(f"Error generating consistent report: {e}")
            return []
    
    def _generate_cache_key(self, report_type, from_date, to_date, **kwargs):
        """Generate unique cache key for report parameters"""
        key_string = f"{report_type}_{from_date}_{to_date}_{sorted(kwargs.items())}"
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _is_cache_valid(self, timestamp, validity_minutes=5):
        """Check if cached report is still valid"""
        time_diff = datetime.now() - timestamp
        return time_diff.total_seconds() < (validity_minutes * 60)
    
    def _generate_report_data(self, report_type, from_date, to_date, **kwargs):
        """Generate actual report data based on type"""
        try:
            if report_type == 'sales_summary':
                return self.queries.get_sales_by_date_range(from_date, to_date)
            elif report_type == 'purchase_summary':
                return self.queries.get_purchases_by_date_range(from_date, to_date)
            elif report_type == 'stock_report':
                return self.queries.get_stock_report()
            elif report_type == 'party_ledger':
                party_cd = kwargs.get('party_cd')
                return self.queries.get_party_ledger(party_cd, from_date, to_date)
            elif report_type == 'trial_balance':
                return self.queries.get_trial_balance_data(from_date, to_date)
            else:
                return []
                
        except Exception as e:
            print(f"Error generating {report_type} report: {e}")
            return []
    
    def clear_cache(self):
        """Clear report cache"""
        self._report_cache.clear()
    
    def invalidate_report_cache(self, report_type=None):
        """Invalidate specific report type cache or all cache"""
        if report_type:
            keys_to_remove = [key for key in self._report_cache.keys() if key.startswith(report_type)]
            for key in keys_to_remove:
                del self._report_cache[key]
        else:
            self.clear_cache()
