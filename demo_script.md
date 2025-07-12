# Demo Video Script: Blockchain Verifier in Action

---

**1. Hashing a Document → Blockchain Entry**
- "Let's upload a document to the Blockchain Verifier. The system calculates its SHA-256 hash and creates a new block in the immutable audit trail."
- (Show: Upload file via API or UI, receive hash and block info)

**2. Verifying Unchanged Document → Valid**
- "Now, we'll verify the same document. The verifier checks the hash and confirms the file is valid and untampered."
- (Show: Upload same file, receive 'valid' result)

**3. Tampering Detection → Invalid Result**
- "Let's modify the document and try again. The system detects the tampering and returns an 'invalid' result."
- (Show: Upload altered file, receive 'invalid' result)

**4. Viewing Audit Trail**
- "We can view the full blockchain audit trail, which records every hash and verification event with cryptographic chaining."
- (Show: Call /blockchain-log endpoint, display log)

**5. Validating Chain Integrity**
- "Finally, let's validate the entire chain. The /validate-chain endpoint confirms the blockchain's integrity, ensuring no tampering has occurred."
- (Show: Call /validate-chain, receive 'valid' response)

---

"Blockchain Verifier: Bringing trust and transparency to file integrity."