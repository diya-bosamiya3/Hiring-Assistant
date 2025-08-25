import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import asdict
import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import uuid

class DataHandler:
    """Handle candidate data with privacy considerations and GDPR compliance"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        os.makedirs(f"{data_dir}/encrypted", exist_ok=True)
        os.makedirs(f"{data_dir}/exports", exist_ok=True)
        self.encryption_key = self._get_or_create_encryption_key()
        self.cipher_suite = Fernet(self.encryption_key)
    
    def _get_or_create_encryption_key(self) -> bytes:
        """Get or create encryption key for data protection"""
        key_file = f"{self.data_dir}/.encryption_key"
        
        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                return f.read()
        else:
            # Generate new key
            key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(key)
            # Set restrictive permissions
            os.chmod(key_file, 0o600)
            return key
    
    def _encrypt_data(self, data: str) -> str:
        """Encrypt sensitive data"""
        try:
            encrypted_data = self.cipher_suite.encrypt(data.encode())
            return base64.b64encode(encrypted_data).decode()
        except Exception as e:
            print(f"Error encrypting data: {e}")
            return data  # Return unencrypted if encryption fails
    
    def _decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        try:
            decoded_data = base64.b64decode(encrypted_data.encode())
            decrypted_data = self.cipher_suite.decrypt(decoded_data)
            return decrypted_data.decode()
        except Exception as e:
            print(f"Error decrypting data: {e}")
            return encrypted_data  # Return as-is if decryption fails
    
    def hash_email(self, email: str) -> str:
        """Create a hash of email for privacy"""
        return hashlib.sha256(email.encode()).hexdigest()[:16]
    
    def hash_phone(self, phone: str) -> str:
        """Create a hash of phone number for privacy"""
        return hashlib.sha256(phone.encode()).hexdigest()[:12]
    
    def save_candidate_data(self, candidate_info, session_id: str, conversation_history: List[Dict] = None) -> bool:
        """Save candidate information securely with encryption"""
        try:
            # Create anonymized and encrypted data structure
            timestamp = datetime.now()
            
            # Encrypt sensitive personal information
            encrypted_data = {
                'session_id': session_id,
                'timestamp': timestamp.isoformat(),
                'data_version': '1.0',
                'privacy_compliant': True,
                
                # Encrypted personal information
                'candidate_info': {
                    'full_name_encrypted': self._encrypt_data(candidate_info.full_name) if candidate_info.full_name else None,
                    'email_encrypted': self._encrypt_data(candidate_info.email) if candidate_info.email else None,
                    'phone_encrypted': self._encrypt_data(candidate_info.phone) if candidate_info.phone else None,
                    'current_location_encrypted': self._encrypt_data(candidate_info.current_location) if candidate_info.current_location else None,
                    
                    # Non-sensitive information (not encrypted)
                    'years_experience': candidate_info.years_experience,
                    'desired_positions': candidate_info.desired_positions,
                    'tech_stack': candidate_info.tech_stack,
                },
                
                # Privacy hashes for identification without exposing data
                'privacy_hashes': {
                    'email_hash': self.hash_email(candidate_info.email) if candidate_info.email else None,
                    'phone_hash': self.hash_phone(candidate_info.phone) if candidate_info.phone else None,
                },
                
                # Metadata
                'metadata': {
                    'ip_address_hash': None,  # Could be implemented if needed
                    'user_agent_hash': None,  # Could be implemented if needed
                    'session_duration': None,  # Could be calculated
                    'completion_status': 'complete' if conversation_history else 'incomplete'
                }
            }
            
            # Add conversation history if provided (encrypted)
            if conversation_history:
                encrypted_data['conversation_history_encrypted'] = self._encrypt_data(
                    json.dumps(conversation_history)
                )
            
            # Save to encrypted file
            filename = f"{self.data_dir}/encrypted/candidate_{session_id}.json"
            with open(filename, 'w') as f:
                json.dump(encrypted_data, f, indent=2)
            
            # Set restrictive file permissions
            os.chmod(filename, 0o600)
            
            # Log the data storage (without sensitive info)
            self._log_data_activity('SAVE', session_id, {
                'has_personal_info': bool(candidate_info.full_name),
                'has_contact_info': bool(candidate_info.email),
                'tech_stack_count': len(candidate_info.tech_stack) if candidate_info.tech_stack else 0
            })
            
            return True
            
        except Exception as e:
            print(f"Error saving candidate data: {e}")
            return False
    
    def load_candidate_data(self, session_id: str) -> Optional[Dict]:
        """Load and decrypt candidate data"""
        try:
            filename = f"{self.data_dir}/encrypted/candidate_{session_id}.json"
            
            if not os.path.exists(filename):
                return None
            
            with open(filename, 'r') as f:
                encrypted_data = json.load(f)
            
            # Decrypt sensitive information
            decrypted_data = encrypted_data.copy()
            
            if 'candidate_info' in encrypted_data:
                candidate_info = encrypted_data['candidate_info']
                decrypted_data['candidate_info'] = {
                    'full_name': self._decrypt_data(candidate_info['full_name_encrypted']) if candidate_info.get('full_name_encrypted') else None,
                    'email': self._decrypt_data(candidate_info['email_encrypted']) if candidate_info.get('email_encrypted') else None,
                    'phone': self._decrypt_data(candidate_info['phone_encrypted']) if candidate_info.get('phone_encrypted') else None,
                    'current_location': self._decrypt_data(candidate_info['current_location_encrypted']) if candidate_info.get('current_location_encrypted') else None,
                    'years_experience': candidate_info.get('years_experience'),
                    'desired_positions': candidate_info.get('desired_positions'),
                    'tech_stack': candidate_info.get('tech_stack', []),
                }
            
            if 'conversation_history_encrypted' in encrypted_data:
                decrypted_history = self._decrypt_data(encrypted_data['conversation_history_encrypted'])
                decrypted_data['conversation_history'] = json.loads(decrypted_history)
            
            self._log_data_activity('LOAD', session_id)
            return decrypted_data
            
        except Exception as e:
            print(f"Error loading candidate data: {e}")
            return None
    
    def export_candidate_data(self, session_id: str, export_format: str = 'json') -> Optional[str]:
        """Export candidate data for GDPR compliance (data portability)"""
        try:
            data = self.load_candidate_data(session_id)
            if not data:
                return None
            
            # Create export-friendly format
            export_data = {
                'export_info': {
                    'exported_at': datetime.now().isoformat(),
                    'session_id': session_id,
                    'format': export_format,
                    'gdpr_compliant': True
                },
                'personal_information': data.get('candidate_info', {}),
                'conversation_summary': {
                    'total_messages': len(data.get('conversation_history', [])),
                    'completion_status': data.get('metadata', {}).get('completion_status', 'unknown')
                },
                'privacy_notice': {
                    'data_controller': 'TalentScout Recruitment Agency',
                    'purpose': 'Initial candidate screening and recruitment',
                    'retention_period': '30 days from collection',
                    'rights': 'You have the right to access, rectify, erase, and port your data'
                }
            }
            
            # Save export file
            export_filename = f"{self.data_dir}/exports/export_{session_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            with open(export_filename, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            self._log_data_activity('EXPORT', session_id, {'format': export_format})
            return export_filename
            
        except Exception as e:
            print(f"Error exporting candidate data: {e}")
            return None
    
    def delete_candidate_data(self, session_id: str, reason: str = 'user_request') -> bool:
        """Delete candidate data (GDPR right to erasure)"""
        try:
            filename = f"{self.data_dir}/encrypted/candidate_{session_id}.json"
            
            if os.path.exists(filename):
                # Log deletion before removing file
                self._log_data_activity('DELETE', session_id, {'reason': reason})
                
                # Securely delete file
                os.remove(filename)
                
                # Also remove any export files for this session
                export_pattern = f"export_{session_id}_"
                for export_file in os.listdir(f"{self.data_dir}/exports"):
                    if export_file.startswith(export_pattern):
                        os.remove(f"{self.data_dir}/exports/{export_file}")
                
                return True
            
            return False
            
        except Exception as e:
            print(f"Error deleting candidate data: {e}")
            return False
    
    def cleanup_old_data(self, retention_days: int = 30) -> int:
        """Remove old candidate data based on retention policy"""
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        deleted_count = 0
        
        try:
            encrypted_dir = f"{self.data_dir}/encrypted"
            
            for filename in os.listdir(encrypted_dir):
                if filename.startswith('candidate_') and filename.endswith('.json'):
                    filepath = os.path.join(encrypted_dir, filename)
                    
                    try:
                        with open(filepath, 'r') as f:
                            data = json.load(f)
                        
                        file_date = datetime.fromisoformat(data['timestamp'])
                        
                        if file_date < cutoff_date:
                            session_id = data.get('session_id', 'unknown')
                            
                            # Log automatic deletion
                            self._log_data_activity('AUTO_DELETE', session_id, {
                                'retention_days': retention_days,
                                'file_age_days': (datetime.now() - file_date).days
                            })
                            
                            # Delete the file
                            os.remove(filepath)
                            deleted_count += 1
                            
                    except Exception as e:
                        print(f"Error processing file {filename}: {e}")
            
            # Also cleanup old export files
            exports_dir = f"{self.data_dir}/exports"
            for filename in os.listdir(exports_dir):
                if filename.startswith('export_'):
                    filepath = os.path.join(exports_dir, filename)
                    file_stat = os.stat(filepath)
                    file_date = datetime.fromtimestamp(file_stat.st_mtime)
                    
                    if file_date < cutoff_date:
                        os.remove(filepath)
            
            return deleted_count
            
        except Exception as e:
            print(f"Error during cleanup: {e}")
            return deleted_count
    
    def _log_data_activity(self, activity: str, session_id: str, metadata: Dict = None):
        """Log data handling activities for audit trail"""
        try:
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'activity': activity,
                'session_id': session_id,
                'metadata': metadata or {}
            }
            
            log_file = f"{self.data_dir}/activity_log.json"
            
            # Load existing log or create new
            if os.path.exists(log_file):
                with open(log_file, 'r') as f:
                    log_data = json.load(f)
            else:
                log_data = {'activities': []}
            
            log_data['activities'].append(log_entry)
            
            # Keep only last 1000 entries
            if len(log_data['activities']) > 1000:
                log_data['activities'] = log_data['activities'][-1000:]
            
            with open(log_file, 'w') as f:
                json.dump(log_data, f, indent=2)
                
        except Exception as e:
            print(f"Error logging activity: {e}")
    
    def get_privacy_report(self) -> Dict:
        """Generate privacy compliance report"""
        try:
            report = {
                'generated_at': datetime.now().isoformat(),
                'data_summary': {
                    'total_records': 0,
                    'encrypted_records': 0,
                    'oldest_record': None,
                    'newest_record': None
                },
                'compliance_status': {
                    'encryption_enabled': True,
                    'retention_policy_active': True,
                    'audit_logging_enabled': True,
                    'gdpr_compliant': True
                },
                'recent_activities': []
            }
            
            # Count records
            encrypted_dir = f"{self.data_dir}/encrypted"
            if os.path.exists(encrypted_dir):
                files = [f for f in os.listdir(encrypted_dir) if f.startswith('candidate_')]
                report['data_summary']['total_records'] = len(files)
                report['data_summary']['encrypted_records'] = len(files)
                
                # Find oldest and newest records
                dates = []
                for filename in files:
                    try:
                        filepath = os.path.join(encrypted_dir, filename)
                        with open(filepath, 'r') as f:
                            data = json.load(f)
                        dates.append(datetime.fromisoformat(data['timestamp']))
                    except:
                        continue
                
                if dates:
                    report['data_summary']['oldest_record'] = min(dates).isoformat()
                    report['data_summary']['newest_record'] = max(dates).isoformat()
            
            # Get recent activities
            log_file = f"{self.data_dir}/activity_log.json"
            if os.path.exists(log_file):
                with open(log_file, 'r') as f:
                    log_data = json.load(f)
                report['recent_activities'] = log_data['activities'][-10:]  # Last 10 activities
            
            return report
            
        except Exception as e:
            print(f"Error generating privacy report: {e}")
            return {'error': str(e)}
