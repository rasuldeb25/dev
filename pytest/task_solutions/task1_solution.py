"""
Task 1 - Breaking an Affine Cipher

PROBLEM STATEMENT:
The following hexadecimal byte sequence is an encrypted English plaintext.
The encryption was applied byte by byte using the affine formula:
    C = (a * P + b) mod 256

Where:
    P = plaintext byte
    C = ciphertext byte
    a, b = unknown keys (a is relatively prime to 256)

The plaintext is ASCII text and contains a known internal word: "CHANNEL"

OBJECTIVE:
Find the key values a and b, decrypt the ciphertext, and print the original message.

SOLUTION APPROACH:
This is a brute-force attack on the affine cipher. We:
1. Iterate through all possible values of 'a' (1-255, only odd values coprime to 256)
2. Iterate through all possible values of 'b' (0-255)
3. For each (a, b) pair, compute the modular inverse a_inv using Extended Euclidean Algorithm
4. Decrypt the ciphertext using: P = a_inv * (C - b) mod 256
5. Check if the known word "CHANNEL" appears in the decrypted plaintext
6. When found, display the key values and full plaintext

NOTE: During testing, we discovered an anomaly in the cipher data or problem specification.
See task1_debug_proof.py for detailed analysis showing that NO readable combinations
contain English words. This suggests the instructor may have intentionally provided
a corrupted or unsolvable cipher to test error detection skills.
"""

import math

def mod_inverse(a, m=256):
    """
    Calculate the modular inverse of 'a' modulo 'm' using the Extended Euclidean Algorithm.
    
    The modular inverse a_inv satisfies: (a * a_inv) mod m = 1
    This is essential for decrypting the affine cipher.
    
    Args:
        a: The number to find the inverse of
        m: The modulus (default 256 for byte encryption)
    
    Returns:
        The modular inverse of a mod m, or None if it doesn't exist (gcd(a,m) != 1)
    
    Algorithm: Extended Euclidean Algorithm
    - Maintains two sequences: (r, new_r) for remainders and (t, new_t) for coefficients
    - Iterates until new_r becomes 0
    - Returns t mod m as the modular inverse
    """
    # Check if gcd(a, m) = 1 (a and m must be coprime for inverse to exist)
    if math.gcd(a, m) != 1:
        return None
    
    # Initialize variables for Extended Euclidean Algorithm
    t, new_t = 0, 1
    r, new_r = m, a
    
    # Extended Euclidean Algorithm loop
    while new_r != 0:
        q = r // new_r  # Quotient
        # Update variables using recurrence relation
        t, new_t = new_t, t - q * new_t
        r, new_r = new_r, r - q * new_r
    
    # Return the modular inverse (normalized to positive value)
    return t % m


def decrypt_byte(c, a_inv, b):
    """
    Decrypt a single byte using the affine cipher decryption formula.
    
    Formula: P = (a_inv * (C - b)) mod 256
    
    Args:
        c: The ciphertext byte value
        a_inv: The modular inverse of 'a'
        b: The additive key
    
    Returns:
        The decrypted plaintext byte
    """
    return (a_inv * (c - b)) % 256


def main():
    """
    Main function that performs brute-force affine cipher cracking.
    """
    # Ciphertext provided in hexadecimal format
    cipher_hex = "bb 1d 8d 57 a0 45 57 8d a0 57 d1 4d 09 09 45 57 a0 5d 9d d1 4d a0 a0 45 57 17 d1 09 57 4d 8d a0 57 8d 8d a0 a0 09 45 4d 45 a0 a0 57 4d 17 9d 57 4d d1"
    
    # Convert hexadecimal string to bytes
    cipher = bytes(int(x, 16) for x in cipher_hex.split())
    
    # Known internal word that should appear in plaintext
    KNOWN = "CHANNEL"
    
    print("=" * 70)
    print("AFFINE CIPHER BRUTE-FORCE ATTACK")
    print("=" * 70)
    print(f"\nCiphertext length: {len(cipher)} bytes")
    print(f"Ciphertext (hex): {cipher_hex}\n")
    print(f"Known word: '{KNOWN}'")
    print(f"Total combinations to try: {len(range(1, 256, 2)) * 256} = 32,768\n")
    print("-" * 70)
    
    # Brute-force search through all possible keys
    for a in range(1, 256, 2):  # Only odd values (coprime with 256)
        a_inv = mod_inverse(a)
        
        # Skip if modular inverse doesn't exist
        if a_inv is None:
            continue
        
        for b in range(256):
            # Decrypt the entire ciphertext with current (a, b) pair
            plaintext = ''.join(chr(decrypt_byte(c, a_inv, b)) for c in cipher)
            
            # Check if known word appears in decrypted plaintext (case-insensitive)
            if KNOWN in plaintext.upper():
                print(f"\nSOLUTION FOUND!")
                print(f"Key values: a = {a}, b = {b}\n")
                print("DECRYPTED MESSAGE:")
                print("-" * 70)
                print(plaintext)
                print("-" * 70)
                return True
    
    # If no solution found
    print("\nNo solution found.")
    print("\nIMPORTANT NOTICE:")
    print("The cipher data may be corrupted or incorrectly specified.")
    print("Run task1_debug_proof.py to see detailed analysis.")
    print("=" * 70)
    return False


if __name__ == "__main__":
    main()