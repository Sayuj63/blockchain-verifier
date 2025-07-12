// JavaScript Fetch API Example for Blockchain Verifier

// 1. Hash a file and add to blockchain
async function hashFile(file) {
  const formData = new FormData();
  formData.append('file', file);
  const resp = await fetch('http://localhost:8000/hash', {
    method: 'POST',
    body: formData
  });
  const data = await resp.json();
  console.log('Hash File Response:', data);
  return data;
}

// 2. Verify file integrity
async function verifyFile(file, storedHash) {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('stored_hash', storedHash);
  const resp = await fetch('http://localhost:8000/verify', {
    method: 'POST',
    body: formData
  });
  const data = await resp.json();
  console.log('Verify File Response:', data);
  return data;
}

// 3. View blockchain log
async function viewLog() {
  const resp = await fetch('http://localhost:8000/blockchain-log');
  const data = await resp.json();
  console.log('Blockchain Log:', data);
  return data;
}

// 4. Validate chain
async function validateChain() {
  const resp = await fetch('http://localhost:8000/validate-chain');
  const data = await resp.json();
  console.log('Chain Validation:', data);
  return data;
}

// Usage example (in browser with file input):
// const fileInput = document.querySelector('input[type=file]');
// hashFile(fileInput.files[0]);