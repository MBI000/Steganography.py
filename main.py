import hashlib
import binascii


class SteganographyMessenger:
    def __init__(self):
        # Using Zero-Width characters for binary mapping
        self.ZERO_WIDTH_MAP = {'0': '\u200b', '1': '\u200c'}
        self.REVERSE_MAP = {v: k for k, v in self.ZERO_WIDTH_MAP.items()}
        self.MAGIC_MARKER = "STR"  # Identifies our stego file
        self.MOD_CONSTANT = 65521  # Prime for checksum (Modular Arithmetic)

    def _calculate_checksum(self, data_bytes):
        """Modular arithmetic checksum (Adler-32 style)."""
        a, b = 1, 0
        for byte in data_bytes:
            a = (a + byte) % self.MOD_CONSTANT
            b = (b + a) % self.MOD_CONSTANT
        return (b << 16) | a

    def _get_keystream(self, password, length):
        """Generates a SHA-256 derived keystream for XOR encryption."""
        stream = b""
        counter = 0
        while len(stream) < length:
            hash_input = f"{password}{counter}".encode()
            stream += hashlib.sha256(hash_input).digest()
            counter += 1
        return stream[:length]

    def encode(self, cover_text, secret_text, password=None):
        # 1. Prepare Payload
        secret_bytes = secret_text.encode('utf-8')
        checksum = self._calculate_checksum(secret_bytes)
        has_password = 1 if password else 0

        # 2. XOR Encryption (Optional)
        if password:
            keystream = self._get_keystream(password, len(secret_bytes))
            secret_bytes = bytes([b ^ k for b, k in zip(secret_bytes, keystream)])

        # 3. Build Header: MAGIC|LEN|CHECKSUM|PWD_FLAG
        # Format: STR (3 bytes) | 4 byte len | 4 byte checksum | 1 byte flag
        header = self.MAGIC_MARKER.encode() + \
                 len(secret_bytes).to_bytes(4, 'big') + \
                 checksum.to_bytes(4, 'big') + \
                 has_password.to_bytes(1, 'big')

        full_payload = header + secret_bytes

        # 4. Convert to Binary and then to Zero-Width
        binary_string = "".join(format(b, '08b') for b in full_payload)
        invisible_data = "".join(self.ZERO_WIDTH_MAP[bit] for bit in binary_string)

        # 5. Embed after the first word
        words = cover_text.split(' ', 1)
        if len(words) > 1:
            return f"{words[0]}{invisible_data} {words[1]}"
        return f"{cover_text}{invisible_data}"

    def decode(self, stego_text, password=None):
        # 1. Extract zero-width characters
        bits = "".join(self.REVERSE_MAP[char] for char in stego_text if char in self.REVERSE_MAP)
        if not bits:
            return "Error: No hidden data detected."

        # 2. Convert bits to bytes
        payload_bytes = bytes(int(bits[i:i + 8], 2) for i in range(0, len(bits), 8))

        # 3. Parse Header
        magic = payload_bytes[:3].decode(errors='ignore')
        if magic != self.MAGIC_MARKER:
            return "Error: Not a valid steganography file."

        msg_len = int.from_bytes(payload_bytes[3:7], 'big')
        stored_checksum = int.from_bytes(payload_bytes[7:11], 'big')
        is_protected = int.from_bytes(payload_bytes[11:12], 'big')

        # 4. Extract Secret Data
        encrypted_data = payload_bytes[12:12 + msg_len]

        # 5. Decrypt if necessary
        if is_protected:
            if not password:
                return "Error: This message is password protected."
            keystream = self._get_keystream(password, len(encrypted_data))
            decrypted_bytes = bytes([b ^ k for b, k in zip(encrypted_data, keystream)])
        else:
            decrypted_bytes = encrypted_data

        # 6. Verify Integrity
        if self._calculate_checksum(decrypted_bytes) != stored_checksum:
            return "Error: Integrity check failed. Data may be corrupted or password incorrect."

        return decrypted_bytes.decode('utf-8')


# --- Interactive CLI ---
def main():
    stego = SteganographyMessenger()
    print("--- Text Steganography Messenger ---")
    choice = input("1. Encode\n2. Decode\nSelect (1/2): ")

    if choice == '1':
        cover = input("Enter cover text: ")
        secret = input("Enter secret message: ")
        pwd = input("Enter password (optional, press enter to skip): ")
        result = stego.encode(cover, secret, pwd if pwd else None)
        print(f"\nEncoded Result (Copy the line below):\n{result}")

    elif choice == '2':
        text = input("Paste the stego text: ")
        pwd = input("Enter password (if any): ")
        print(f"\nDecoded Message: {stego.decode(text, pwd if pwd else None)}")


if __name__ == "__main__":
    main()