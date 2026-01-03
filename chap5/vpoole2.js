


function decode_sig(vpSig) {
  const vpSigBytes = Buffer.from(vpSig, 'base64');  // 65 bytes

  // Skip the first byte (recovery/header)
  const derBytes = vpSigBytes.slice(1);  // 64 bytes

  // Fixed split: first 32 bytes = r, last 32 bytes = s
  const vpSigBytesPartOne = derBytes.slice(0, 32);   // r bytes
  const vpSigBytesPartTwo = derBytes.slice(32, 64);  // s bytes

  const vpSigR = BigInt('0x' + vpSigBytesPartOne.toString('hex'));
  const vpSigS = BigInt('0x' + vpSigBytesPartTwo.toString('hex'));

  return [vpSigR, vpSigS];
}

// Vanderpoole's signature
const vpSig = "H4vQbVD0pLK7pkzPto8BHourzsBrHMB3Qf5oYVmr741pPwdU2m6FaZZmxh4ScHxFoDelFC9qG0PnAUl5qMFth8k="
const [r, s] = decode_sig(vpSig);
console.log('r:', r);
console.log('s:', s);
