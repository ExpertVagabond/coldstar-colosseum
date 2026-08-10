//! FFI (Foreign Function Interface) for Python integration.
//!
//! Exposes the ZK proof engine to Python via C-compatible functions.
//! Uses JSON-based parameter passing for simplicity and flexibility.
//!
//! # Convention
//! - Input: JSON string (C string, null-terminated)
//! - Output: JSON string (heap-allocated, caller must free)
//! - Errors: Returned as JSON with "error" field
//!
//! # Memory Management
//! All returned strings are heap-allocated with Box::into_raw.
//! The caller must free them with `coldstar_zk_free_string`.
//!
//! # Shared safety contract
//!
//! Every `coldstar_zk_*` entry point in this module that takes an
//! `input_json: *const c_char` shares the same contract. It is repeated in
//! abbreviated form on each function; the authoritative statement is here.
//!
//! ## The input pointer
//! * **Null is allowed.** Every entry point null-checks `input_json` before
//!   dereferencing it and returns an error response instead. Passing null is
//!   defined behaviour, not UB.
//! * **If non-null, it must be a live pointer to a NUL-terminated byte
//!   sequence.** There is no length parameter. `CStr::from_ptr` scans forward
//!   until it finds a `0` byte, so every byte from `input_json` up to and
//!   including the terminator must lie inside a single live allocation the
//!   caller owns. An unterminated buffer, a dangling pointer, or a pointer
//!   one-past-the-end of an allocation is undefined behaviour and will read
//!   out of bounds. No maximum length is enforced.
//! * **Alignment is trivially satisfied** — `c_char` has an alignment of 1 —
//!   but the pointer must still be non-dangling and properly derived from a
//!   real allocation.
//! * **The bytes need not be valid UTF-8.** Invalid UTF-8 is detected and
//!   returned as an error response; it is not undefined behaviour.
//! * **No concurrent mutation.** The buffer is read as a shared borrow for the
//!   duration of the call. The caller must not mutate or free it from another
//!   thread while the call is in flight. Doing so is a data race.
//! * **The callee never takes ownership of the input.** It is only read; the
//!   caller remains responsible for freeing it.
//!
//! ## The returned pointer
//! * **Never null.** The response is always serialisable and can never contain
//!   an interior NUL byte (`serde_json` escapes control characters), and the
//!   serialiser has an infallible fallback, so `CString::new` cannot fail here.
//!   Callers do not need to null-check the result.
//! * **Ownership transfers to the caller.** The buffer is allocated by Rust's
//!   global allocator via `CString::into_raw`.
//! * **It must be freed with `coldstar_zk_free_string`, exactly once.** Freeing
//!   it with libc `free()`, C++ `delete`, or any other allocator is undefined
//!   behaviour, as is freeing it twice or using it after freeing. Never freeing
//!   it leaks the allocation.
//!
//! ## Threading
//! No entry point in this module touches global or `static` mutable state, and
//! the crate contains no `static mut`, no interior-mutable globals, and no
//! hand-written `Send`/`Sync` impls. Concurrent calls from multiple threads are
//! therefore safe provided each call is given its own input buffer and each
//! returned pointer is freed exactly once by exactly one thread.

use std::ffi::{CStr, CString};
use std::os::raw::c_char;

use serde::{Deserialize, Serialize};

use crate::envelope;
use crate::policy::PolicyEngine;
use crate::proofs::{ownership, range};
use crate::types::*;

/// FFI response wrapper
#[derive(Serialize)]
struct FfiResponse {
    success: bool,
    #[serde(skip_serializing_if = "Option::is_none")]
    data: Option<serde_json::Value>,
    #[serde(skip_serializing_if = "Option::is_none")]
    error: Option<String>,
}

impl FfiResponse {
    fn ok(data: serde_json::Value) -> Self {
        FfiResponse {
            success: true,
            data: Some(data),
            error: None,
        }
    }

    fn err(msg: String) -> Self {
        FfiResponse {
            success: false,
            data: None,
            error: Some(msg),
        }
    }

    /// Consume the response and hand its JSON to the caller as an owned,
    /// heap-allocated C string.
    ///
    /// Named `into_*` rather than `to_*` because it takes `self` by value:
    /// the response is consumed and its allocation ownership is transferred
    /// out across the FFI boundary.
    fn into_c_string(self) -> *mut c_char {
        let json = serde_json::to_string(&self).unwrap_or_else(|_| {
            r#"{"success":false,"error":"Failed to serialize response"}"#.to_string()
        });
        CString::new(json)
            .unwrap_or_else(|_| CString::new("null").unwrap())
            .into_raw()
    }
}

/// Helper to parse a C string to a Rust `&str`.
///
/// # Safety
///
/// `ptr` may be null; that case is checked and returned as an error. If `ptr`
/// is non-null it must point to a NUL-terminated byte sequence lying entirely
/// within one live allocation, and that allocation must stay valid and
/// unmutated for as long as the returned `&str` is used.
///
/// The returned lifetime `'a` is unconstrained — it is chosen by the caller,
/// not derived from the pointer — so the borrow checker will not catch a
/// use-after-free here. Every caller in this module uses the result only
/// within the body of a single FFI call, which is the only pattern this
/// helper is safe for.
///
/// Non-UTF-8 input is an error, not undefined behaviour.
unsafe fn parse_c_str<'a>(ptr: *const c_char) -> Result<&'a str, String> {
    if ptr.is_null() {
        return Err("Null pointer".to_string());
    }
    CStr::from_ptr(ptr)
        .to_str()
        .map_err(|e| format!("Invalid UTF-8: {}", e))
}

// ============================================================================
// FFI Functions
// ============================================================================

/// Generate an ownership proof.
///
/// Input JSON:
/// ```json
/// {
///   "secret_key_hex": "...",    // 32-byte secret key, hex-encoded
///   "context_data_hex": "..."   // context data, hex-encoded
/// }
/// ```
///
/// Output JSON:
/// ```json
/// {
///   "success": true,
///   "data": { "ownership_proof": { ... } }
/// }
/// ```
///
/// # Safety
///
/// `input_json` may be null (handled: an error response is returned). If it is
/// non-null it must point to a NUL-terminated byte sequence contained entirely
/// within one live allocation owned by the caller — there is no length
/// argument, so an unterminated buffer reads out of bounds. The bytes need not
/// be valid UTF-8. The buffer must not be mutated or freed by another thread
/// for the duration of the call, and this function does not take ownership of
/// it.
///
/// The returned pointer is never null, is allocated by Rust's global allocator,
/// and transfers ownership to the caller. Free it exactly once with
/// `coldstar_zk_free_string` — never with libc `free()`.
///
/// ## Secret material
/// This entry point is the only one in this module that consumes a private key:
/// `secret_key_hex` is a hex-encoded 32-byte Ed25519 seed. Two consequences the
/// caller must handle:
/// * **The caller owns wiping the input buffer.** This function reads the
///   secret out of the caller's memory and never writes to or zeroizes that
///   buffer. Whoever allocated it must wipe it.
/// * **The intermediate copies made here are not zeroized.** The decoded
///   `String` and the `[u8; 32]` seed built from it are ordinary values dropped
///   without being wiped, so plaintext key bytes can remain in freed heap and
///   stack memory after this call returns. (`ownership::prove_ownership` does
///   zeroize the scalars it derives; the gap is in this FFI shim, not the
///   proof code.)
///
/// The returned JSON contains only public proof material — public key,
/// commitment, challenge, response — and never the secret key.
#[no_mangle]
pub unsafe extern "C" fn coldstar_zk_prove_ownership(input_json: *const c_char) -> *mut c_char {
    let input = match parse_c_str(input_json) {
        Ok(s) => s,
        Err(e) => return FfiResponse::err(e).into_c_string(),
    };

    #[derive(Deserialize)]
    struct Input {
        secret_key_hex: String,
        context_data_hex: String,
    }

    let params: Input = match serde_json::from_str(input) {
        Ok(p) => p,
        Err(e) => return FfiResponse::err(format!("Invalid input: {}", e)).into_c_string(),
    };

    let secret_key = match hex::decode(&params.secret_key_hex) {
        Ok(k) if k.len() == 32 => {
            let mut arr = [0u8; 32];
            arr.copy_from_slice(&k);
            arr
        }
        Ok(k) => {
            return FfiResponse::err(format!("Secret key must be 32 bytes, got {}", k.len()))
                .into_c_string()
        }
        Err(e) => return FfiResponse::err(format!("Invalid hex: {}", e)).into_c_string(),
    };

    let context_data = match hex::decode(&params.context_data_hex) {
        Ok(d) => d,
        Err(e) => return FfiResponse::err(format!("Invalid context hex: {}", e)).into_c_string(),
    };

    match ownership::prove_ownership(&secret_key, &context_data) {
        Ok(proof) => {
            let data = serde_json::to_value(&proof).unwrap();
            FfiResponse::ok(serde_json::json!({ "ownership_proof": data })).into_c_string()
        }
        Err(e) => FfiResponse::err(format!("Proof generation failed: {}", e)).into_c_string(),
    }
}

/// Verify an ownership proof.
///
/// Input JSON:
/// ```json
/// {
///   "proof": { ... },           // OwnershipProof
///   "context_data_hex": "..."   // context data, hex-encoded
/// }
/// ```
///
/// # Safety
///
/// `input_json` may be null (handled: an error response is returned). If it is
/// non-null it must point to a NUL-terminated byte sequence contained entirely
/// within one live allocation owned by the caller — there is no length
/// argument, so an unterminated buffer reads out of bounds. The bytes need not
/// be valid UTF-8. The buffer must not be mutated or freed by another thread
/// for the duration of the call, and this function does not take ownership of
/// it.
///
/// The returned pointer is never null, is allocated by Rust's global allocator,
/// and transfers ownership to the caller. Free it exactly once with
/// `coldstar_zk_free_string` — never with libc `free()`.
///
/// This entry point handles no secret material; both the proof and the context
/// data are public.
///
/// ## Reading the result correctly
/// A **failed verification is reported as `success: true` with
/// `data.valid == false`** — not as `success: false`. `success: false` means
/// the request itself was malformed (bad pointer content, bad JSON, bad hex).
/// A caller that gates signing on `success` alone will treat an invalid
/// ownership proof as a pass. Gate on `data.valid`.
#[no_mangle]
pub unsafe extern "C" fn coldstar_zk_verify_ownership(input_json: *const c_char) -> *mut c_char {
    let input = match parse_c_str(input_json) {
        Ok(s) => s,
        Err(e) => return FfiResponse::err(e).into_c_string(),
    };

    #[derive(Deserialize)]
    struct Input {
        proof: OwnershipProof,
        context_data_hex: String,
    }

    let params: Input = match serde_json::from_str(input) {
        Ok(p) => p,
        Err(e) => return FfiResponse::err(format!("Invalid input: {}", e)).into_c_string(),
    };

    let context_data = match hex::decode(&params.context_data_hex) {
        Ok(d) => d,
        Err(e) => return FfiResponse::err(format!("Invalid context hex: {}", e)).into_c_string(),
    };

    match ownership::verify_ownership(&params.proof, &context_data) {
        Ok(()) => FfiResponse::ok(serde_json::json!({ "valid": true })).into_c_string(),
        Err(e) => FfiResponse::ok(serde_json::json!({
            "valid": false,
            "error": format!("{}", e)
        }))
        .into_c_string(),
    }
}

/// Generate a range proof.
///
/// Input JSON:
/// ```json
/// {
///   "value": 1000000000,
///   "num_bits": 64,
///   "context_data_hex": "..."
/// }
/// ```
///
/// # Safety
///
/// `input_json` may be null (handled: an error response is returned). If it is
/// non-null it must point to a NUL-terminated byte sequence contained entirely
/// within one live allocation owned by the caller — there is no length
/// argument, so an unterminated buffer reads out of bounds. The bytes need not
/// be valid UTF-8. The buffer must not be mutated or freed by another thread
/// for the duration of the call, and this function does not take ownership of
/// it.
///
/// The returned pointer is never null, is allocated by Rust's global allocator,
/// and transfers ownership to the caller. Free it exactly once with
/// `coldstar_zk_free_string` — never with libc `free()`.
///
/// `num_bits` arrives from untrusted JSON but is **not** an unchecked
/// allocation size: `range::prove_range` rejects anything outside
/// `[1, MAX_RANGE_BITS]` (64) before allocating per-bit proof material, so a
/// hostile `num_bits` cannot drive an unbounded allocation through this
/// boundary. Proof size is O(num_bits); a 64-bit proof is roughly 10 KB of
/// returned JSON, which the caller must free.
///
/// ## The blinding factor is discarded
/// `range::prove_range` returns `(proof, blinding_factor)` and documents that
/// the caller should retain the blinding factor to open the commitment later.
/// This FFI shim drops it. Callers reaching the range proof through this
/// boundary therefore **cannot** open the value commitment afterwards; if that
/// is needed, the Rust API must be used directly.
#[no_mangle]
pub unsafe extern "C" fn coldstar_zk_prove_range(input_json: *const c_char) -> *mut c_char {
    let input = match parse_c_str(input_json) {
        Ok(s) => s,
        Err(e) => return FfiResponse::err(e).into_c_string(),
    };

    #[derive(Deserialize)]
    struct Input {
        value: u64,
        num_bits: usize,
        context_data_hex: String,
    }

    let params: Input = match serde_json::from_str(input) {
        Ok(p) => p,
        Err(e) => return FfiResponse::err(format!("Invalid input: {}", e)).into_c_string(),
    };

    let context_data = match hex::decode(&params.context_data_hex) {
        Ok(d) => d,
        Err(e) => return FfiResponse::err(format!("Invalid context hex: {}", e)).into_c_string(),
    };

    match range::prove_range(params.value, params.num_bits, &context_data) {
        Ok((proof, _blinding)) => {
            let data = serde_json::to_value(&proof).unwrap();
            FfiResponse::ok(serde_json::json!({ "range_proof": data })).into_c_string()
        }
        Err(e) => FfiResponse::err(format!("Range proof failed: {}", e)).into_c_string(),
    }
}

/// Verify a range proof.
///
/// Input JSON:
/// ```json
/// {
///   "proof": { ... },           // RangeProof
///   "context_data_hex": "..."
/// }
/// ```
///
/// # Safety
///
/// `input_json` may be null (handled: an error response is returned). If it is
/// non-null it must point to a NUL-terminated byte sequence contained entirely
/// within one live allocation owned by the caller — there is no length
/// argument, so an unterminated buffer reads out of bounds. The bytes need not
/// be valid UTF-8. The buffer must not be mutated or freed by another thread
/// for the duration of the call, and this function does not take ownership of
/// it.
///
/// The returned pointer is never null, is allocated by Rust's global allocator,
/// and transfers ownership to the caller. Free it exactly once with
/// `coldstar_zk_free_string` — never with libc `free()`.
///
/// The proof is deserialised from untrusted JSON, so `input_json` is expected
/// to be attacker-influenced; a hostile proof produces a verification failure,
/// not memory unsafety. This entry point handles no secret material.
///
/// ## Reading the result correctly
/// As with `coldstar_zk_verify_ownership`, a **failed verification is reported
/// as `success: true` with `data.valid == false`**. `success: false` only means
/// the request was malformed. Gate on `data.valid`, not on `success`.
#[no_mangle]
pub unsafe extern "C" fn coldstar_zk_verify_range(input_json: *const c_char) -> *mut c_char {
    let input = match parse_c_str(input_json) {
        Ok(s) => s,
        Err(e) => return FfiResponse::err(e).into_c_string(),
    };

    #[derive(Deserialize)]
    struct Input {
        proof: RangeProof,
        context_data_hex: String,
    }

    let params: Input = match serde_json::from_str(input) {
        Ok(p) => p,
        Err(e) => return FfiResponse::err(format!("Invalid input: {}", e)).into_c_string(),
    };

    let context_data = match hex::decode(&params.context_data_hex) {
        Ok(d) => d,
        Err(e) => return FfiResponse::err(format!("Invalid context hex: {}", e)).into_c_string(),
    };

    match range::verify_range(&params.proof, &context_data) {
        Ok(()) => FfiResponse::ok(serde_json::json!({ "valid": true })).into_c_string(),
        Err(e) => FfiResponse::ok(serde_json::json!({
            "valid": false,
            "error": format!("{}", e)
        }))
        .into_c_string(),
    }
}

/// Build and verify a complete transfer envelope.
///
/// Input JSON:
/// ```json
/// {
///   "envelope_json": "..."  // Serialized TransferEnvelope
/// }
/// ```
///
/// # Safety
///
/// `input_json` may be null (handled: an error response is returned). If it is
/// non-null it must point to a NUL-terminated byte sequence contained entirely
/// within one live allocation owned by the caller — there is no length
/// argument, so an unterminated buffer reads out of bounds. The bytes need not
/// be valid UTF-8. The buffer must not be mutated or freed by another thread
/// for the duration of the call, and this function does not take ownership of
/// it.
///
/// The returned pointer is never null, is allocated by Rust's global allocator,
/// and transfers ownership to the caller. Free it exactly once with
/// `coldstar_zk_free_string` — never with libc `free()`.
///
/// Note the double encoding: the outer JSON object carries the envelope as a
/// *string* field, which is then parsed as JSON a second time. Both layers are
/// untrusted input and both are checked; neither can produce memory unsafety.
///
/// ## Replay protection does not survive this boundary
/// This function constructs a fresh `PolicyEngine` on every call.
/// `PolicyEngine` implements nonce replay protection by accumulating seen
/// nonces in a `HashSet` that lives on the engine, so a per-call engine starts
/// with an empty set and the "Nonce freshness (replay protection)" check
/// **always reports `passed: true`** through this entry point, including for an
/// envelope that has already been validated and signed. Callers must not treat
/// that check as meaningful replay defence; replay state has to be kept on the
/// caller's side, or the Rust API used directly with a long-lived engine.
///
/// ## Policy limits are unconfigured
/// For the same reason the engine is created with default settings, so the
/// transfer-limit and destination-allowlist checks are inert here (`0` = no
/// limit, empty allowlist = allow all). They report `passed: true` because
/// nothing is configured, not because a configured limit was satisfied.
#[no_mangle]
pub unsafe extern "C" fn coldstar_zk_validate_envelope(input_json: *const c_char) -> *mut c_char {
    let input = match parse_c_str(input_json) {
        Ok(s) => s,
        Err(e) => return FfiResponse::err(e).into_c_string(),
    };

    #[derive(Deserialize)]
    struct Input {
        envelope_json: String,
    }

    let params: Input = match serde_json::from_str(input) {
        Ok(p) => p,
        Err(e) => return FfiResponse::err(format!("Invalid input: {}", e)).into_c_string(),
    };

    let env = match envelope::deserialize_envelope(&params.envelope_json) {
        Ok(e) => e,
        Err(e) => {
            return FfiResponse::err(format!("Invalid envelope: {}", e)).into_c_string()
        }
    };

    let mut engine = PolicyEngine::new();
    match engine.validate_envelope(&env) {
        Ok((result, summary)) => {
            let data = serde_json::json!({
                "verification": serde_json::to_value(&result).unwrap(),
                "summary": serde_json::to_value(&summary).unwrap(),
            });
            FfiResponse::ok(data).into_c_string()
        }
        Err(e) => FfiResponse::err(format!("Validation failed: {}", e)).into_c_string(),
    }
}

/// Get the library version.
#[no_mangle]
pub extern "C" fn coldstar_zk_version() -> *mut c_char {
    let version = format!(
        "{{\"version\":\"{}\",\"name\":\"coldstar_zk\"}}",
        crate::VERSION
    );
    CString::new(version).unwrap().into_raw()
}

/// Free a string returned by any coldstar_zk function.
///
/// # Safety
///
/// `ptr` must be either null (handled: this is a no-op) or a pointer that was
/// returned by one of the `coldstar_zk_*` functions in this module and has not
/// been freed yet. It is reclaimed with `CString::from_raw`, i.e. through
/// Rust's global allocator.
///
/// Undefined behaviour results from any of:
/// * freeing the same pointer twice, or using it after this call returns;
/// * passing a pointer obtained from anywhere other than a `coldstar_zk_*`
///   function — including one produced by `malloc`, `strdup`, or a different
///   Rust library, since the allocator must match;
/// * passing an interior pointer, or a pointer whose bytes were modified such
///   that the NUL terminator moved (`from_raw` recomputes the length by
///   scanning for the terminator, and a moved terminator means the wrong
///   allocation size is handed back to the allocator);
/// * calling this concurrently with any other use of the same pointer.
///
/// Conversely, never freeing a returned pointer simply leaks it.
#[no_mangle]
pub unsafe extern "C" fn coldstar_zk_free_string(ptr: *mut c_char) {
    if !ptr.is_null() {
        drop(CString::from_raw(ptr));
    }
}
