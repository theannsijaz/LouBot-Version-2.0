/**
 * WebAuthn Face ID/Touch ID Authentication for LouBot
 * Provides secure biometric authentication for macOS devices
 */

class WebAuthnManager {
    constructor() {
        this.supported = false;
        this.platformAuthenticatorAvailable = false;
        this.ready = this.init();
    }

    async init() {
        // Check if WebAuthn is supported
        if (window.PublicKeyCredential) {
            this.supported = true;
            
            // Check if platform authenticator (Face ID/Touch ID) is available
            try {
                this.platformAuthenticatorAvailable = await PublicKeyCredential.isUserVerifyingPlatformAuthenticatorAvailable();
            } catch (error) {
                console.error('Error checking platform authenticator availability:', error);
            }
        }
        
        console.log('WebAuthn supported:', this.supported);
        console.log('Platform authenticator available:', this.platformAuthenticatorAvailable);
    }

    /**
     * Convert base64url string to ArrayBuffer
     */
    base64urlToArrayBuffer(base64url) {
        // Add padding if needed
        const padding = '='.repeat((4 - base64url.length % 4) % 4);
        const base64 = (base64url + padding).replace(/-/g, '+').replace(/_/g, '/');
        
        const binaryString = window.atob(base64);
        const bytes = new Uint8Array(binaryString.length);
        for (let i = 0; i < binaryString.length; i++) {
            bytes[i] = binaryString.charCodeAt(i);
        }
        return bytes.buffer;
    }

    /**
     * Convert ArrayBuffer to base64url string
     */
    arrayBufferToBase64url(buffer) {
        const bytes = new Uint8Array(buffer);
        let binary = '';
        for (let i = 0; i < bytes.byteLength; i++) {
            binary += String.fromCharCode(bytes[i]);
        }
        return window.btoa(binary).replace(/\+/g, '-').replace(/\//g, '_').replace(/=/g, '');
    }

    /**
     * Register a new Face ID/Touch ID credential
     */
    async registerCredential() {
        if (!this.supported || !this.platformAuthenticatorAvailable) {
            throw new Error('Face ID/Touch ID not supported on this device');
        }

        try {
            console.log('[WebAuthn] Starting credential registration...');
            
            // Request registration options from server
            const response = await fetch('/webauthn/register/begin', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                }
            });

            if (!response.ok) {
                const error = await response.json();
                console.error('[WebAuthn] Registration begin failed:', error);
                throw new Error(error.error || 'Registration failed');
            }

            const { options } = await response.json();
            console.log('[WebAuthn] Registration options received:', options);

            // Convert challenge and user ID from base64url
            options.challenge = this.base64urlToArrayBuffer(options.challenge);
            options.user.id = this.base64urlToArrayBuffer(options.user.id);

            console.log('[WebAuthn] Calling navigator.credentials.create...');
            
            // Create the credential - this will show Touch ID prompt
            const credential = await navigator.credentials.create({
                publicKey: options
            });

            console.log('[WebAuthn] Credential created successfully:', credential);

            // Convert credential response for server
            const credentialData = {
                id: credential.id,
                rawId: this.arrayBufferToBase64url(credential.rawId),
                type: credential.type,
                response: {
                    clientDataJSON: this.arrayBufferToBase64url(credential.response.clientDataJSON),
                    attestationObject: this.arrayBufferToBase64url(credential.response.attestationObject)
                }
            };

            console.log('[WebAuthn] Sending credential to server...');

            // Send credential to server
            const completeResponse = await fetch('/webauthn/register/complete', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify(credentialData)
            });

            if (!completeResponse.ok) {
                const error = await completeResponse.json();
                console.error('[WebAuthn] Registration complete failed:', error);
                throw new Error(error.error || 'Registration completion failed');
            }

            const result = await completeResponse.json();
            console.log('[WebAuthn] Registration completed successfully:', result);
            return result;

        } catch (error) {
            console.error('[WebAuthn] Registration failed:', error);
            
            // Provide more user-friendly error messages
            if (error.name === 'NotAllowedError') {
                throw new Error('Touch ID/Face ID was cancelled. Please try again and allow when prompted.');
            } else if (error.name === 'NotSupportedError') {
                throw new Error('Touch ID/Face ID is not supported on this device.');
            } else if (error.name === 'SecurityError') {
                throw new Error('Security error. Please ensure you are using HTTPS in production.');
            } else if (error.name === 'AbortError') {
                throw new Error('Touch ID/Face ID setup was aborted. Please try again.');
            } else {
                throw error;
            }
        }
    }

    /**
     * Authenticate using Face ID/Touch ID
     */
    async authenticateWithBiometric(email) {
        if (!this.supported || !this.platformAuthenticatorAvailable) {
            throw new Error('Face ID/Touch ID not supported on this device');
        }

        try {
            // Request authentication options from server
            const response = await fetch('/webauthn/auth/begin', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({ email })
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Authentication initialization failed');
            }

            const { options } = await response.json();

            // Convert challenge and allowed credentials
            options.challenge = this.base64urlToArrayBuffer(options.challenge);
            
            if (options.allowCredentials) {
                options.allowCredentials = options.allowCredentials.map(cred => ({
                    ...cred,
                    id: this.base64urlToArrayBuffer(cred.id)
                }));
            }

            // Get the credential
            const assertion = await navigator.credentials.get({
                publicKey: options
            });

            // Convert assertion response for server
            const assertionData = {
                id: assertion.id,
                rawId: this.arrayBufferToBase64url(assertion.rawId),
                type: assertion.type,
                response: {
                    clientDataJSON: this.arrayBufferToBase64url(assertion.response.clientDataJSON),
                    authenticatorData: this.arrayBufferToBase64url(assertion.response.authenticatorData),
                    signature: this.arrayBufferToBase64url(assertion.response.signature),
                    userHandle: assertion.response.userHandle ? this.arrayBufferToBase64url(assertion.response.userHandle) : null
                },
                email: email
            };

            // Send assertion to server
            const completeResponse = await fetch('/webauthn/auth/complete', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify(assertionData)
            });

            if (!completeResponse.ok) {
                const error = await completeResponse.json();
                throw new Error(error.error || 'Authentication failed');
            }

            const result = await completeResponse.json();
            return result;

        } catch (error) {
            console.error('WebAuthn authentication failed:', error);
            throw error;
        }
    }

    /**
     * Check if user has registered credentials
     */
    async checkCredentialStatus() {
        try {
            const response = await fetch('/webauthn/check-support');
            if (response.ok) {
                return await response.json();
            }
        } catch (error) {
            console.error('Error checking credential status:', error);
        }
        return { has_credentials: false };
    }

    /**
     * Get CSRF token from cookie
     */
    getCSRFToken() {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrftoken') {
                return value;
            }
        }
        return '';
    }

    /**
     * Show user-friendly error messages
     */
    getErrorMessage(error) {
        if (error.name === 'NotSupportedError') {
            return 'Face ID/Touch ID is not supported on this device.';
        } else if (error.name === 'SecurityError') {
            return 'Security error. Please make sure you\'re using HTTPS.';
        } else if (error.name === 'NotAllowedError') {
            return 'Operation was cancelled or not allowed.';
        } else if (error.name === 'InvalidStateError') {
            return 'An authenticator is already registered for this account.';
        } else if (error.name === 'ConstraintError') {
            return 'The authenticator does not meet the requirements.';
        } else {
            return error.message || 'An unknown error occurred.';
        }
    }
}

// Initialize WebAuthn manager
const webAuthnManager = new WebAuthnManager();

// Utility functions for the login page
window.WebAuthnUtils = {
    manager: webAuthnManager,
    
    // Check if biometric authentication is available
    async isBiometricAvailable() {
        await webAuthnManager.ready;
        return webAuthnManager.supported && webAuthnManager.platformAuthenticatorAvailable;
    },
    
    // Register Face ID/Touch ID after login
    async setupBiometricAuth() {
        try {
            const result = await webAuthnManager.registerCredential();
            return { success: true, message: result.message };
        } catch (error) {
            return { success: false, message: webAuthnManager.getErrorMessage(error) };
        }
    },
    
    // Login with Face ID/Touch ID
    async loginWithBiometric(email) {
        try {
            const result = await webAuthnManager.authenticateWithBiometric(email);
            return { success: true, result };
        } catch (error) {
            return { success: false, message: webAuthnManager.getErrorMessage(error) };
        }
    },
    
    // Check if user has credentials
    async hasCredentials() {
        const status = await webAuthnManager.checkCredentialStatus();
        return status.has_credentials;
    }
}; 