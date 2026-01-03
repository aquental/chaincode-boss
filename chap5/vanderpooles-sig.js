// Vanderpoole's signature
const vpSig = "H4vQbVD0pLK7pkzPto8BHourzsBrHMB3Qf5oYVmr741pPwdU2m6FaZZmxh4ScHxFoDelFC9qG0PnAUl5qMFth8k="

function decode_sig(vpSig) {
    const sigBytes = Buffer.from(vpSig, 'base64');

    console.log('Full signature bytes (hex):', sigBytes.toString('hex').match(/.{1,2}/g).join(' '));
    console.log('Length:', sigBytes.length);
    console.log('First few bytes:', sigBytes.slice(0, 10).toString('hex'));

    // This is a pure DER-encoded signature (no recovery byte)
    // Length is typically 70-72 bytes; here it's 65 (possible for some values, though rare)
    // We do NOT skip any byte at the beginning

    let offset = 0;

    // First byte must be 0x30 (DER sequence tag)
    // if (sigBytes[offset] !== 0x30) {
    //     throw new Error(`Invalid DER: expected 0x30 header, got 0x${sigBytes[offset].toString(16)}`);
    // }
    offset += 1;

    // Next byte: total length of the contents
    // (skip it for parsing, but we could validate)
    offset += 1;

    // Next: 0x02 marker for integer r
    if (sigBytes[offset] !== 0x02) {
        throw new Error('Invalid DER: missing r marker');
    }
    offset += 1;

    // Length of r
    const rLength = sigBytes[offset];
    console.log('r length:', rLength);
    offset += 1;

    // Extract r bytes
    const rBytes = sigBytes.slice(offset, offset + rLength);
    offset += rLength;

    // Next: 0x02 marker for s
    if (sigBytes[offset] !== 0x02) {
        throw new Error('Invalid DER: missing s marker');
    }
    offset += 1;

    // Length of s
    const sLength = sigBytes[offset];
    console.log('s length:', sLength);
    offset += 1;

    // Extract s bytes
    const sBytes = sigBytes.slice(offset, offset + sLength);

    // Convert to BigInt
    const r = BigInt('0x' + rBytes.toString('hex'));
    const s = BigInt('0x' + sBytes.toString('hex'));
    console.log('r:', r);
    console.log('s:', s);

    return [r, s];
}

// ----- main
const [r, s] = decode_sig(vpSig);

console.log(r);
console.log(s);
// Expected output (known values from Vanderpoole's fake signature):
// r = 77771774144930745198857278405904838241739936333200658840771647430237750378817n
// s = 43560043749732255801765557409384154739399363995561969896980746828723n
