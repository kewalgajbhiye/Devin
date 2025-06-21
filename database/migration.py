"""
Database migration utilities for converting DBF files to SQLite
"""

import sqlite3
from pathlib import Path
import logging
from datetime import datetime

try:
    import dbf
    DBF_AVAILABLE = True
except ImportError:
    DBF_AVAILABLE = False
    logging.warning("DBF library not available. DBF migration will not work.")

class DBFMigrator:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        
    def migrate_from_dbf_folder(self, dbf_folder_path):
        """Migrate all DBF files from the original software folder"""
        if not DBF_AVAILABLE:
            raise ImportError("DBF library is required for migration")
            
        dbf_folder = Path(dbf_folder_path)
        if not dbf_folder.exists():
            raise FileNotFoundError(f"DBF folder not found: {dbf_folder_path}")
        
        vp_folder = dbf_folder / "VP2122"
        if vp_folder.exists():
            self._migrate_vp_folder(vp_folder)
        
        self._migrate_root_files(dbf_folder)
        
        logging.info("DBF migration completed successfully")
    
    def _migrate_vp_folder(self, vp_folder):
        """Migrate files from VP2122 folder"""
        parmst_file = vp_folder / "PARMST.DBF"
        if parmst_file.exists():
            self._migrate_parties(parmst_file)
        
        fin_mst_file = vp_folder / "FIN_MST.DBF"
        if fin_mst_file.exists():
            self._migrate_items(fin_mst_file)
        
        purc_file = vp_folder / "PURC.DBF"
        if purc_file.exists():
            self._migrate_purchases(purc_file)
        
        sale_file = vp_folder / "SALE.DBF"
        if sale_file.exists():
            self._migrate_sales(sale_file)
        
        ledger_file = vp_folder / "LEDGER.DBF"
        if ledger_file.exists():
            self._migrate_ledger(ledger_file)
        
        cashbk_file = vp_folder / "CASHBK.DBF"
        if cashbk_file.exists():
            self._migrate_cashbook(cashbk_file)
        
        bankbk_file = vp_folder / "BANKBK.DBF"
        if bankbk_file.exists():
            self._migrate_bankbook(bankbk_file)
    
    def _migrate_root_files(self, dbf_folder):
        """Migrate root level DBF files"""
        company_file = dbf_folder / "COMPANY.DBF"
        if company_file.exists():
            self._migrate_company(company_file)
    
    def _migrate_parties(self, dbf_file):
        """Migrate parties from PARMST.DBF"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        try:
            with dbf.Table(str(dbf_file)) as table:
                for record in table:
                    if not record.deleted():
                        cursor.execute('''
                            INSERT OR REPLACE INTO parties 
                            (party_cd, party_nm, place, phone, bal_cd, ly_baln, ytd_dr, ytd_cr)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            record.party_cd.strip() if hasattr(record, 'party_cd') else '',
                            record.party_nm.strip() if hasattr(record, 'party_nm') else '',
                            record.place.strip() if hasattr(record, 'place') else '',
                            record.phone.strip() if hasattr(record, 'phone') else '',
                            record.bal_cd.strip() if hasattr(record, 'bal_cd') else 'D',
                            float(record.ly_baln) if hasattr(record, 'ly_baln') else 0,
                            float(record.ytd_dr) if hasattr(record, 'ytd_dr') else 0,
                            float(record.ytd_cr) if hasattr(record, 'ytd_cr') else 0
                        ))
            conn.commit()
            logging.info("Parties migrated successfully")
        except Exception as e:
            conn.rollback()
            logging.error(f"Error migrating parties: {e}")
        finally:
            conn.close()
    
    def _migrate_items(self, dbf_file):
        """Migrate items from FIN_MST.DBF"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        try:
            with dbf.Table(str(dbf_file)) as table:
                for record in table:
                    if not record.deleted():
                        cursor.execute('''
                            INSERT OR REPLACE INTO items 
                            (it_cd, it_nm, unit, rate)
                            VALUES (?, ?, ?, ?)
                        ''', (
                            record.it_cd.strip() if hasattr(record, 'it_cd') else '',
                            record.it_nm.strip() if hasattr(record, 'it_nm') else '',
                            record.unit.strip() if hasattr(record, 'unit') else 'KG',
                            float(record.rate) if hasattr(record, 'rate') else 0
                        ))
            conn.commit()
            logging.info("Items migrated successfully")
        except Exception as e:
            conn.rollback()
            logging.error(f"Error migrating items: {e}")
        finally:
            conn.close()
    
    def _migrate_purchases(self, dbf_file):
        """Migrate purchases from PURC.DBF"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        try:
            with dbf.Table(str(dbf_file)) as table:
                for record in table:
                    if not record.deleted():
                        cursor.execute('''
                            INSERT OR REPLACE INTO purchases 
                            (bill_no, bill_date, party_cd, it_cd, qty, katta, tot_smt, rate, sal_amt, 
                             order_no, order_dt, lr_no, trans_cd, agent_cd, exp1, exp2, exp3, exp4, exp5, cash, other, pkgs)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            int(record.bill_no) if hasattr(record, 'bill_no') else 0,
                            record.bill_date if hasattr(record, 'bill_date') else None,
                            record.party_cd.strip() if hasattr(record, 'party_cd') else '',
                            record.it_cd.strip() if hasattr(record, 'it_cd') else '',
                            float(record.qty) if hasattr(record, 'qty') else 0,
                            float(record.katta) if hasattr(record, 'katta') else 0,
                            float(record.tot_smt) if hasattr(record, 'tot_smt') else 0,
                            float(record.rate) if hasattr(record, 'rate') else 0,
                            float(record.sal_amt) if hasattr(record, 'sal_amt') else 0,
                            record.order_no.strip() if hasattr(record, 'order_no') else '',
                            record.order_dt if hasattr(record, 'order_dt') else None,
                            record.lr_no.strip() if hasattr(record, 'lr_no') else '',
                            record.trans_cd.strip() if hasattr(record, 'trans_cd') else '',
                            record.agent_cd.strip() if hasattr(record, 'agent_cd') else '',
                            float(record.exp1) if hasattr(record, 'exp1') else 0,
                            float(record.exp2) if hasattr(record, 'exp2') else 0,
                            float(record.exp3) if hasattr(record, 'exp3') else 0,
                            float(record.exp4) if hasattr(record, 'exp4') else 0,
                            float(record.exp5) if hasattr(record, 'exp5') else 0,
                            float(record.cash) if hasattr(record, 'cash') else 0,
                            float(record.other) if hasattr(record, 'other') else 0,
                            record.pkgs.strip() if hasattr(record, 'pkgs') else ''
                        ))
            conn.commit()
            logging.info("Purchases migrated successfully")
        except Exception as e:
            conn.rollback()
            logging.error(f"Error migrating purchases: {e}")
        finally:
            conn.close()
    
    def _migrate_sales(self, dbf_file):
        """Migrate sales from SALE.DBF"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        try:
            with dbf.Table(str(dbf_file)) as table:
                for record in table:
                    if not record.deleted():
                        cursor.execute('''
                            INSERT OR REPLACE INTO sales 
                            (bill_no, bill_date, party_cd, it_cd, qty, katta, tot_smt, rate, sal_amt, 
                             order_no, order_dt, lr_no, trans_cd, agent_cd, exp1, exp2, exp3, exp4, exp5, cash, other, pkgs)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            int(record.bill_no) if hasattr(record, 'bill_no') else 0,
                            record.bill_date if hasattr(record, 'bill_date') else None,
                            record.party_cd.strip() if hasattr(record, 'party_cd') else '',
                            record.it_cd.strip() if hasattr(record, 'it_cd') else '',
                            float(record.qty) if hasattr(record, 'qty') else 0,
                            float(record.katta) if hasattr(record, 'katta') else 0,
                            float(record.tot_smt) if hasattr(record, 'tot_smt') else 0,
                            float(record.rate) if hasattr(record, 'rate') else 0,
                            float(record.sal_amt) if hasattr(record, 'sal_amt') else 0,
                            record.order_no.strip() if hasattr(record, 'order_no') else '',
                            record.order_dt if hasattr(record, 'order_dt') else None,
                            record.lr_no.strip() if hasattr(record, 'lr_no') else '',
                            record.trans_cd.strip() if hasattr(record, 'trans_cd') else '',
                            record.agent_cd.strip() if hasattr(record, 'agent_cd') else '',
                            float(record.exp1) if hasattr(record, 'exp1') else 0,
                            float(record.exp2) if hasattr(record, 'exp2') else 0,
                            float(record.exp3) if hasattr(record, 'exp3') else 0,
                            float(record.exp4) if hasattr(record, 'exp4') else 0,
                            float(record.exp5) if hasattr(record, 'exp5') else 0,
                            float(record.cash) if hasattr(record, 'cash') else 0,
                            float(record.other) if hasattr(record, 'other') else 0,
                            record.pkgs.strip() if hasattr(record, 'pkgs') else ''
                        ))
            conn.commit()
            logging.info("Sales migrated successfully")
        except Exception as e:
            conn.rollback()
            logging.error(f"Error migrating sales: {e}")
        finally:
            conn.close()
    
    def _migrate_ledger(self, dbf_file):
        """Migrate ledger from LEDGER.DBF"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        try:
            with dbf.Table(str(dbf_file)) as table:
                for record in table:
                    if not record.deleted():
                        cursor.execute('''
                            INSERT OR REPLACE INTO ledger 
                            (vouch_date, vouch_no, party_cd, particulars, dr_amt, cr_amt, balance, vouch_type, ref_no)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            record.vouch_date if hasattr(record, 'vouch_date') else None,
                            record.vouch_no.strip() if hasattr(record, 'vouch_no') else '',
                            record.party_cd.strip() if hasattr(record, 'party_cd') else '',
                            record.particulars.strip() if hasattr(record, 'particulars') else '',
                            float(record.dr_amt) if hasattr(record, 'dr_amt') else 0,
                            float(record.cr_amt) if hasattr(record, 'cr_amt') else 0,
                            float(record.balance) if hasattr(record, 'balance') else 0,
                            record.vouch_type.strip() if hasattr(record, 'vouch_type') else '',
                            record.ref_no.strip() if hasattr(record, 'ref_no') else ''
                        ))
            conn.commit()
            logging.info("Ledger migrated successfully")
        except Exception as e:
            conn.rollback()
            logging.error(f"Error migrating ledger: {e}")
        finally:
            conn.close()
    
    def _migrate_cashbook(self, dbf_file):
        """Migrate cash book from CASHBK.DBF"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        try:
            with dbf.Table(str(dbf_file)) as table:
                for record in table:
                    if not record.deleted():
                        cursor.execute('''
                            INSERT OR REPLACE INTO cashbook 
                            (vouch_date, vouch_no, particulars, dr_amt, cr_amt, balance, party_cd)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            record.vouch_date if hasattr(record, 'vouch_date') else None,
                            record.vouch_no.strip() if hasattr(record, 'vouch_no') else '',
                            record.particulars.strip() if hasattr(record, 'particulars') else '',
                            float(record.dr_amt) if hasattr(record, 'dr_amt') else 0,
                            float(record.cr_amt) if hasattr(record, 'cr_amt') else 0,
                            float(record.balance) if hasattr(record, 'balance') else 0,
                            record.party_cd.strip() if hasattr(record, 'party_cd') else ''
                        ))
            conn.commit()
            logging.info("Cash book migrated successfully")
        except Exception as e:
            conn.rollback()
            logging.error(f"Error migrating cash book: {e}")
        finally:
            conn.close()
    
    def _migrate_bankbook(self, dbf_file):
        """Migrate bank book from BANKBK.DBF"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        try:
            with dbf.Table(str(dbf_file)) as table:
                for record in table:
                    if not record.deleted():
                        cursor.execute('''
                            INSERT OR REPLACE INTO bankbook 
                            (vouch_date, vouch_no, particulars, dr_amt, cr_amt, balance, party_cd, bank_name, cheque_no)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            record.vouch_date if hasattr(record, 'vouch_date') else None,
                            record.vouch_no.strip() if hasattr(record, 'vouch_no') else '',
                            record.particulars.strip() if hasattr(record, 'particulars') else '',
                            float(record.dr_amt) if hasattr(record, 'dr_amt') else 0,
                            float(record.cr_amt) if hasattr(record, 'cr_amt') else 0,
                            float(record.balance) if hasattr(record, 'balance') else 0,
                            record.party_cd.strip() if hasattr(record, 'party_cd') else '',
                            record.bank_name.strip() if hasattr(record, 'bank_name') else '',
                            record.cheque_no.strip() if hasattr(record, 'cheque_no') else ''
                        ))
            conn.commit()
            logging.info("Bank book migrated successfully")
        except Exception as e:
            conn.rollback()
            logging.error(f"Error migrating bank book: {e}")
        finally:
            conn.close()
    
    def _migrate_company(self, dbf_file):
        """Migrate company info from COMPANY.DBF"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        try:
            with dbf.Table(str(dbf_file)) as table:
                for record in table:
                    if not record.deleted():
                        cursor.execute('''
                            INSERT OR REPLACE INTO company 
                            (name, address1, address2, city, phone, from_date, to_date, password, directory)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            record.name.strip() if hasattr(record, 'name') else '',
                            record.address1.strip() if hasattr(record, 'address1') else '',
                            record.address2.strip() if hasattr(record, 'address2') else '',
                            record.city.strip() if hasattr(record, 'city') else '',
                            record.phone.strip() if hasattr(record, 'phone') else '',
                            record.from_date if hasattr(record, 'from_date') else None,
                            record.to_date if hasattr(record, 'to_date') else None,
                            record.password.strip() if hasattr(record, 'password') else '',
                            record.directory.strip() if hasattr(record, 'directory') else ''
                        ))
            conn.commit()
            logging.info("Company info migrated successfully")
        except Exception as e:
            conn.rollback()
            logging.error(f"Error migrating company info: {e}")
        finally:
            conn.close()
