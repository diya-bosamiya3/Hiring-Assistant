#!/usr/bin/env python3
"""
Privacy maintenance script for TalentScout Hiring Assistant
Run this script periodically to maintain data privacy compliance
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.data_handler import DataHandler
from config import Config
import json
from datetime import datetime

def main():
    """Main privacy maintenance routine"""
    print("🔒 TalentScout Privacy Maintenance")
    print("=" * 40)
    
    config = Config()
    data_handler = DataHandler()
    
    # Generate privacy report
    print("📊 Generating privacy compliance report...")
    report = data_handler.get_privacy_report()
    
    print(f"✅ Total records: {report['data_summary']['total_records']}")
    print(f"🔐 Encrypted records: {report['data_summary']['encrypted_records']}")
    
    if report['data_summary']['oldest_record']:
        print(f"📅 Oldest record: {report['data_summary']['oldest_record']}")
    
    # Cleanup old data
    print(f"\n🧹 Cleaning up data older than {config.DATA_RETENTION_DAYS} days...")
    deleted_count = data_handler.cleanup_old_data(config.DATA_RETENTION_DAYS)
    print(f"🗑️ Deleted {deleted_count} old records")
    
    # Save maintenance report
    maintenance_report = {
        'maintenance_date': datetime.now().isoformat(),
        'deleted_records': deleted_count,
        'privacy_report': report
    }
    
    with open('data/maintenance_report.json', 'w') as f:
        json.dump(maintenance_report, f, indent=2)
    
    print("\n✅ Privacy maintenance completed successfully!")
    print("📁 Report saved to: data/maintenance_report.json")

if __name__ == "__main__":
    main()
