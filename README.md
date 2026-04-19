# Text Steganography Messenger 

**Text Steganography Messenger** is a Python-based security tool designed to conceal secret messages within ordinary-looking text. It utilizes invisible Unicode characters to hide data, making the secret message undetectable to the human eye while remaining fully retrievable by the recipient.

This project was developed to demonstrate the intersection of **Discrete Mathematics**, **Cryptography**, and **Linguistic Steganography**.

---

## 🚀 How It Works

The application hides information by mapping binary data to "Zero-Width" characters. These characters exist in the Unicode standard but have no visual width, meaning they do not change the appearance of the text when rendered in modern apps like WhatsApp or Telegram.

### 1. The Encoding Process
1. **Binary Conversion:** The secret message is converted into a sequence of bits (0s and 1s) using UTF-8 encoding.
2. **Metadata Header:** A header is prepended to the data containing a **Magic Marker** (for identification), the **Payload Length**, and a **Checksum**.
3. **Encryption:** If a password is provided, the data undergoes bitwise **XOR encryption** using a keystream derived from SHA-256.
4. **Injection:** The bits are mapped to invisible characters:
   - `0` → `\u200b` (Zero Width Space)
   - `1` → `\u200c` (Zero Width Non-Joiner)
5. **Merging:** These invisible characters are inserted into a "Cover Text" (e.g., *"See you at the park"*).

### 2. The Decoding Process
1. **Extraction:** The script filters the input text, ignoring all visible characters and collecting only the hidden Zero-Width symbols.
2. **Bit Reconstruction:** The symbols are converted back into a binary stream.
3. **Validation:** The script checks for the Magic Marker. if found, it parses the header to determine the message length and checksum.
4. **Decryption:** If the message is password-protected, the XOR operation is reversed using the provided password.
5. **Integrity Check:** The checksum is verified to ensure no bits were lost during transmission.

---

##  Mathematical Foundations

This project serves as a practical implementation of several discrete mathematical concepts:

### I. Binary Representation
Every character in the secret message is represented as a byte (8 bits). For any character $x$, its integer value is expressed in base-2:
$$x_{10} = \sum_{i=0}^{7} b_i 2^i$$
where $b \in \{0, 1\}$. This allows any digital data to be treated as a simple sequence of two states, which we map to our two invisible Unicode symbols.

### II. XOR Cipher (Bitwise Logic)
Encryption is handled via the **Exclusive OR** ($\oplus$) operation. XOR is a logical operation that outputs true only when inputs differ. It is used here because it is a **self-inverse** operation:
$$C = M \oplus K$$
$$M = C \oplus K$$
*(Where $M$ is the message, $K$ is the key, and $C$ is the ciphertext).*
Mathematically, $(M \oplus K) \oplus K = M \oplus (K \oplus K) = M \oplus 0 = M$.

### III. Modular Arithmetic (Checksums)
To ensure the message was not corrupted during copy-pasting, we use an Adler-32 style checksum. For a data stream $D$, we calculate two values $A$ and $B$ modulo a large prime:
$$A = (1 + \sum d_i) \pmod{65521}$$
$$B = (\sum A_i) \pmod{65521}$$
The prime $65521$ is chosen as the largest 16-bit prime to ensure an even distribution of hash values and minimize "collisions" (where two different messages produce the same checksum).

---

##  Installation & Usage

### Requirements
- Python 3.6+
- A Unicode-compliant text editor or messaging app (WhatsApp, Telegram, etc.)

### Running the App
1. Clone this repository or save `main.py`.
2. Run the application:
   ```bash
   python main.py