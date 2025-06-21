# Modern Business Management System

A modern desktop application for vegetable wholesale and commission agent business operations, built with Python and Tkinter.

## Features

- **Purchase Management**: Create purchase entries, manage supplier transactions, print bills
- **Sales Management**: Handle sales transactions and customer orders
- **Inventory Management**: Track stock levels, manage items with lot-wise tracking
- **Party Management**: Manage customers and suppliers with contact details
- **Accounting**: Ledger management, cash/bank books, financial reports
- **Reporting**: Generate business reports and analytics

## Technology Stack

- **Frontend**: Python Tkinter with modern UI components
- **Database**: SQLite for embedded offline storage
- **Business Logic**: Python modules for purchase, sales, accounting operations
- **Packaging**: PyInstaller for executable generation

## Installation

### From Source
```bash
git clone <repository-url>
cd business-software-modernization
pip install -r requirements.txt
python main.py
```

### Building Executable
```bash
pip install pyinstaller
pyinstaller business_app.spec
```

The executable will be created in the `dist/` directory.

## Usage

1. Launch the application
2. Use the dashboard cards to navigate to different modules
3. Create purchase entries, manage parties, and generate reports
4. All data is stored locally in SQLite database for offline operation

## Data Migration

To migrate data from the original Visual FoxPro system:

```python
from database.migration import DBFMigrator
from database.models import DatabaseManager

db_manager = DatabaseManager()
migrator = DBFMigrator(db_manager)
migrator.migrate_from_dbf_folder('/path/to/original/dbf/files')
```

## Business Context

This software is designed for:
- **UMESH BALIRAM NIPANE** - Vegetable Merchants & Commission Agent
- **Location**: Kalamna Sabji Market & Mahatma Fule Sabji Market, Nagpur
- **Operations**: Vegetable wholesale, commission agent services
- **Market Schedule**: Friday Market Closed

## License

Proprietary software for business use.
