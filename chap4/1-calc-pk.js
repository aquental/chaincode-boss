const secp256k1 = require('@savingsatoshi/secp256k1js')
// Multiply the private key by the ECDSA generator point G to
// produce a new curve point which is the public key.
// Return that curve point (also known as a group element)
// which will be an instance of secp256k1.GE
// See the library source code for the exact definition
// https://github.com/saving-satoshi/secp256k1js/blob/main/secp256k1.js
const G = secp256k1.G

function privateKeyToPublicKey(privateKey) {
    // Convert the hex string private key to a BigInt
    const privKeyInt = BigInt(`0x${privateKey}`);

    // Multiply the generator point G by the private key scalar
    // The .mul() method is available on secp256k1.GE instances
    const publicKeyPoint = G.mul(privKeyInt);

    return publicKeyPoint;
}
