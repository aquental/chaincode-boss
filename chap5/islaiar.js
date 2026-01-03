const { Hash } = require('crypto')
const secp256k1 = require('@savingsatoshi/secp256k1js')
// View the library source code
// https://github.com/saving-satoshi/secp256k1js/blob/main/secp256k1.js

const GE = secp256k1.GE
const FE = secp256k1.FE
const ORDER = secp256k1.ORDER

const publicKeyX = "0x11db93e1dcdb8a016b49840f8c53bc1eb68a382e97b1482ecad7b148a6909a5c"
const publicKeyY = "0xb2e0eaddfb84ccf9744464f82e160bfa9b8b64f9d4c03f999b8643f656b412a3"

// Defined by Bitcoin message signing protocol
const prefix = "Bitcoin Signed Message:\n"

// Provided by Vanderpoole
let text = "I am Vanderpoole and I have control of the private key Satoshi\n"
text += "used to sign the first-ever Bitcoin transaction confirmed in block #170.\n"
text += "This message is signed with the same private key."

// Encoded Signature
vpSig = "H4vQbVD0pLK7pkzPto8BHourzsBrHMB3Qf5oYVmr741pPwdU2m6FaZZmxh4ScHxFoDelFC9qG0PnAUl5qMFth8k="

function encode_message(text) {
  const prefix = Buffer.from('Bitcoin Signed Message:\n', 'ascii');
  const textBytes = Buffer.from(text, 'ascii');
  const vector = Buffer.concat([
    Buffer.from([prefix.length]),
    prefix,
    Buffer.from([textBytes.length]),
    textBytes
  ])
  const singleHash = Hash('sha256').update(vector).digest();
  const doubleHash = Hash('sha256').update(singleHash).digest();
  const msgHex = doubleHash.toString('hex');
  return BigInt('0x' + msgHex)
}

function decode_sig(vpSig) {
  const vpSigBytes = Buffer.from(vpSig, 'base64');
  const vpSigR = BigInt('0x' + vpSigBytes.slice(1, 33).toString('hex'));
  const vpSigS = BigInt('0x' + vpSigBytes.slice(33).toString('hex'));
  return [vpSigR, vpSigS]
}

function verify(sig_r, sig_s, key, msg) {
  // Verify an ECDSA signature given a public key and a message.
  // All input values will be 32-byte BigInt()'s.
  // Start by creating a curve point representation of the public key
  // Next, check the range limits of the signature values
  if (sig_r == 0n || sig_r >= ORDER) {
    console.log('invalid r value');
    return false;
  }
  if (sig_s == 0n || sig_s >= ORDER) {
    console.log('invalid s value');
    return false;
  }
  // Helper function:
  // Find modular multiplicative inverse using Extended Euclidean Algorithm
  function invert(value, modulus = ORDER) {
    let x0 = 0n;
    let x1 = 1n;
    let a = value;
    let m = modulus;

    while (a > 1n) {
      const q = a / m;
      let t = m;
      m = a % m;
      a = t;
      t = x0;
      x0 = x1 - q * x0;
      x1 = t;
    }

    if (x1 < 0n)
      x1 += modulus;

    return x1;
  }

  const sig_s_inverted = invert(sig_s);
  const u1 = (msg * sig_s_inverted) % ORDER;
  const u2 = (sig_r * sig_s_inverted) % ORDER;
  const R = (secp256k1.G.mul(u1)).add(key.mul(u2));
  return R.x.equals(new FE(sig_r));
}

// Define the necessary params for the verify() function
// YOUR CODE HERE
const [r, s] = decode_sig(vpSig);
const msg = encode_message(text);
const keyGE = new GE(BigInt(publicKeyX), BigInt(publicKeyY));
