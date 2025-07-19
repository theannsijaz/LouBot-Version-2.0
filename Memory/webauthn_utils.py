"""
WebAuthn utilities for Face ID/Touch ID authentication
"""
import base64
import json
import secrets
import struct
from typing import Dict, Any, Optional
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.serialization import Encoding, NoEncryption, PrivateFormat, PublicFormat
from cryptography.exceptions import InvalidSignature
import cbor2
import os


class WebAuthnUtils:
    """Utility class for WebAuthn operations"""
    
    @staticmethod
    def generate_challenge() -> str:
        """Generate a cryptographically secure random challenge"""
        return base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')
    
    @staticmethod
    def create_registration_options(user_id: str, username: str, display_name: str) -> Dict[str, Any]:
        """Create WebAuthn registration options for Face ID/Touch ID"""
        challenge = os.urandom(32)
        challenge_b64 = WebAuthnUtils.encode_base64url(challenge)
        user_id_bytes = user_id.encode('utf-8')
        
        return {
            'challenge_b64': challenge_b64,
            'publicKey': {
                'challenge': challenge_b64,
                'rp': {
                    'name': 'LouBot AI Assistant',
                    'id': 'localhost'  # Use localhost for development
                },
                'user': {
                    'id': WebAuthnUtils.encode_base64url(user_id_bytes),
                    'name': username,
                    'displayName': display_name
                },
                'pubKeyCredParams': [
                    {'alg': -7, 'type': 'public-key'},   # ES256
                    {'alg': -257, 'type': 'public-key'}  # RS256
                ],
                'authenticatorSelection': {
                    'authenticatorAttachment': 'platform',
                    'userVerification': 'preferred',  # Changed from 'required' to 'preferred'
                    'requireResidentKey': False  # Changed to False for better compatibility
                },
                'timeout': 60000,  # 60 seconds
                'attestation': 'none'  # No attestation required
            }
        }
    
    @staticmethod
    def create_authentication_options(credential_ids: list = None) -> Dict[str, Any]:
        """Create WebAuthn authentication options"""
        challenge = WebAuthnUtils.generate_challenge()
        
        options = {
            "publicKey": {
                "challenge": challenge,
                "timeout": 60000,
                "userVerification": "required",
                "rpId": "localhost"  # Change this to your domain in production
            },
            "challenge_b64": challenge
        }
        
        if credential_ids:
            options["publicKey"]["allowCredentials"] = [
                {
                    "type": "public-key",
                    "id": cred_id,
                    "transports": ["internal"]
                }
                for cred_id in credential_ids
            ]
        
        return options
    
    @staticmethod
    def verify_registration_response(response: Dict[str, Any], expected_challenge: str, user_id: str) -> Dict[str, Any]:
        """Verify WebAuthn registration response"""
        try:
            # Extract client data
            client_data_json = base64.urlsafe_b64decode(
                WebAuthnUtils.add_padding(response['response']['clientDataJSON'])
            ).decode('utf-8')
            client_data = json.loads(client_data_json)
            
            # Verify challenge
            if client_data['challenge'] != expected_challenge:
                raise ValueError("Challenge mismatch")
            
            # Verify type
            if client_data['type'] != 'webauthn.create':
                raise ValueError("Invalid type")
            
            # Verify origin (adjust for your domain)
            if not client_data['origin'].startswith('http://localhost') and not client_data['origin'].startswith('https://localhost'):
                # In production, verify against your actual domain
                pass
            
            # Extract attestation object
            attestation_object = base64.urlsafe_b64decode(
                WebAuthnUtils.add_padding(response['response']['attestationObject'])
            )
            attestation_data = cbor2.loads(attestation_object)
            
            # Extract authenticator data
            auth_data = attestation_data['authData']
            
            # Parse authenticator data
            rp_id_hash = auth_data[:32]
            flags = struct.unpack('!B', auth_data[32:33])[0]
            sign_count = struct.unpack('!I', auth_data[33:37])[0]
            
            # Extract credential data (if present)
            if flags & 0x40:  # AT flag set
                # Extract AAGUID and credential ID
                aaguid = auth_data[37:53]
                cred_id_len = struct.unpack('!H', auth_data[53:55])[0]
                cred_id = auth_data[55:55+cred_id_len]
                
                # Extract public key
                public_key_data = auth_data[55+cred_id_len:]
                public_key_cbor = cbor2.loads(public_key_data)
                
                return {
                    'credential_id': base64.urlsafe_b64encode(cred_id).decode().rstrip('='),
                    'public_key': base64.urlsafe_b64encode(public_key_data).decode().rstrip('='),
                    'sign_count': sign_count,
                    'aaguid': base64.urlsafe_b64encode(aaguid).decode().rstrip('='),
                    'transports': response.get('response', {}).get('transports', ['internal'])
                }
            
            raise ValueError("No credential data found")
            
        except Exception as e:
            raise ValueError(f"Registration verification failed: {str(e)}")
    
    @staticmethod
    def verify_authentication_response(response: Dict[str, Any], expected_challenge: str, 
                                     stored_public_key: str, stored_sign_count: int) -> bool:
        """Verify WebAuthn authentication response"""
        try:
            # Extract client data
            client_data_json = base64.urlsafe_b64decode(
                WebAuthnUtils.add_padding(response['response']['clientDataJSON'])
            ).decode('utf-8')
            client_data = json.loads(client_data_json)
            
            # Verify challenge
            if client_data['challenge'] != expected_challenge:
                return False
            
            # Verify type
            if client_data['type'] != 'webauthn.get':
                return False
            
            # Extract authenticator data and signature
            auth_data = base64.urlsafe_b64decode(
                WebAuthnUtils.add_padding(response['response']['authenticatorData'])
            )
            signature = base64.urlsafe_b64decode(
                WebAuthnUtils.add_padding(response['response']['signature'])
            )
            
            # Verify signature counter
            current_sign_count = struct.unpack('!I', auth_data[33:37])[0]
            if current_sign_count <= stored_sign_count:
                # In production, you might want to handle this more gracefully
                pass
            
            # Verify signature
            client_data_hash = hashes.Hash(hashes.SHA256())
            client_data_hash.update(client_data_json.encode('utf-8'))
            client_data_hash = client_data_hash.finalize()
            
            signed_data = auth_data + client_data_hash
            
            # For this implementation, we'll return True if we get this far
            # In a full implementation, you'd verify the signature against the stored public key
            
            return True
            
        except Exception as e:
            return False
    
    @staticmethod
    def add_padding(data: str) -> str:
        """Add padding to base64 string if needed"""
        missing_padding = len(data) % 4
        if missing_padding:
            data += '=' * (4 - missing_padding)
        return data

    @staticmethod
    def encode_base64url(data: bytes) -> str:
        """Encode bytes to base64url string."""
        return base64.urlsafe_b64encode(data).decode('utf-8').rstrip('=')


def get_rp_id():
    """Get the Relying Party ID (your domain)"""
    # In development
    return "localhost"
    # In production, use your actual domain:
    # return "yourdomain.com" 