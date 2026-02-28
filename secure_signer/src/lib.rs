//! Coldstar Secure Signer - A memory-safe signing core for Solana and EVM transactions
//!
//! This library provides secure signing with:
//! - Ed25519 signing for Solana
//! - secp256k1 ECDSA signing for EVM (Base, Ethereum)
//! - Memory-locked key storage (mlock/VirtualLock)
//! - Automatic zeroization of sensitive data
//! - Panic-safe cleanup
//! - No plaintext key exposure outside signing function
//!
//! # Security Model
//!
//! The private key is:
//! 1. Received as an encrypted container (AES-256-GCM)
//! 2. Decrypted directly into a locked memory buffer
//! 3. Used for signing within the secure context
//! 4. Immediately zeroized after use (even on error/panic)
//!
//! The plaintext key NEVER:
//! - Leaves the locked memory buffer
//! - Gets logged or written to disk
//! - Gets swapped to disk (memory is locked)
//! - Survives beyond the signing function scope

pub mod crypto;
pub mod error;
pub mod secure_buffer;

#[cfg(feature = "ffi")]
pub mod ffi;

// Solana (Ed25519)
pub use crypto::{
    create_encrypted_key_container, decrypt_and_sign, sign_transaction, EncryptedKeyContainer,
    SigningResult,
};

// EVM (secp256k1)
pub use crypto::{
    decrypt_and_sign_evm, sign_evm_transaction, EVMSigningResult,
};

pub use error::SignerError;
pub use secure_buffer::{LockingMode, SecureBuffer};

/// Library version
pub const VERSION: &str = env!("CARGO_PKG_VERSION");

/// Re-export for convenience
pub mod prelude {
    pub use crate::crypto::{
        create_encrypted_key_container, decrypt_and_sign, decrypt_and_sign_evm,
        EncryptedKeyContainer, EVMSigningResult,
    };
    pub use crate::error::SignerError;
    pub use crate::secure_buffer::SecureBuffer;
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_version() {
        assert!(!VERSION.is_empty());
    }
}
