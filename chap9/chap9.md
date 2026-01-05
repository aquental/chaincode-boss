# Bitcoin script

We mentioned bitcoin script back in chapter 6 but we didn't dwell on it because the coins you were spending were locked by a simple mechanism: a single signature and an implied script that evaluated that signature with a public key. Now things are going to get more interesting.

There are two important parts to spending a bitcoin output: A script and a stack.

We'll explore the two concepts at a high level first.

## The stack

Think of a stack of books. If you want to add a book, you have to place it on top of the stack. There's nowhere else for it to go. If you want to read a book, the only one you can access is the one on top of the stack. Even if you want more than one you have start at the top of the stack and work your way down. In computing terms, a stack is like an array of data items with two operations:

`OP_PUSH` Add an item to the "top" of the stack.

`OP_POP` Remove the "top" item from the stack for processing.

Example:

Here is a stack: `[]`
Push the number 1: `[1]`
Push the number 2: `[1, 2]`
Pop the top item off the stack: `[1]`

Notice that the first item pushed on to the stack will be the last item popped off the stack, so it will be the last item processed by the script. For this reason the stack has an "upside down" or "backwards" feel to it, and the first thing you see on the stack will likely be the solution required at the end of script processing.

When spending a bitcoin transaction output, the elements required by the spender are provided in the witness section of the spending transaction's input (see chapter 6) and those elements get pushed on to the stack before any script processing begins. We will refer to those items as the INITIAL STACK. They are important because they are literally the data that unlocks a script and allows coins to be spent!

## OpCodes

Script is a linear series of commands that are executed one by one, manipulating items on the stack. When the end of the script is reached, there must be EXACTLY ONE NON-ZERO (NON-FALSE) ITEM remaining on the stack, or the entire operation is invalid and so is your bitcoin transaction. There are over 100 commands in the bitcoin script language, called "opcodes". We are only going to use a handful of them for this challenge.

Let's demonstrate an example where we lock up a bitcoin with the math problem 1 + 2 = ? Whoever knows the answer to this math problem can spend the coins.

The script would look like this:

```
OP_1 OP_2 OP_ADD OP_EQUAL
```

This is script will be hashed and bech32-encoded into an address where someone can send coins.

##

The stack solution
The stack solution would look like this and the spending transaction needs to contain all these elements. They go in the witness section of the input that is trying to spend these coins. Let's step through it:

| Step   | Stack                           | Script Execution |
| ------ | ------------------------------- | ---------------- |
| (init) | OP_1 OP_2 OP_ADD OP_EQUAL       | [3]              |
| 1      | **[OP_1]** OP_2 OP_ADD OP_EQUAL | [3,1]            |
| 2      | OP_1 **[OP_2]** OP_ADD OP_EQUAL | [3,1,2]          |
| 3      | OP_1 OP_2 **[OP_ADD]** OP_EQUAL | [3,3]            |
| 4      | OP_1 OP_2 OP_ADD **[OP_EQUAL]** | [True]           |

Explanation

- init: the funding transaction output and spending transaction input are brought together.
- step 1: `OP_1` pushes "1" onto the stack.
- step 2: `OP_2` pushes "2" onto the stack.
- step 3: `OP_ADD` pops two items off the stack, adds them together, and pushes the sum back to the stack.
- step 4: `OP_EQUAL`pops two items off the stack, compares them, and pushes a boolean result back to the stack.

Now we have reached the end of the script and there is only a single TRUE item left on the stack - the coins are spent!

If we started this example with a 4 on the stack, we would not be able to spend the coins because the OP_EQUAL would evaluate to FALSE. For these challenges we are going to use a very limited set of opcodes, which we will introduce by category.

## Basic Arithmetic

Bitcoin script can do simple math operations. You could lock coins using simple math but then anyone who can do math could spend the coins! In other words, do not try this on mainnet.

Opcodes that push integers or arbitrary data to the stack

`OP_0`
Pushes the number 0 on to the stack.

`OP_1`
Pushes the number 1 on to the stack.

`OP_2`
Pushes the number 2 on to the stack.

`OP_3`
Pushes the number 3 on to the stack.

`OP_DUP`
Pushes a duplicate of the top stack item on to the stack.

`OP_PUSH`
Pushes the following script value on to the stack. Example values include SIG(alice), PUBKEY(alice), HASH256(secret), secret. Lowercase strings represent real-world data and the other opcodes in this interpreter will process them as if they are actual keys, signatures, hash digests and preimages.

Opcodes that do arithmetic

`OP_ADD`
Pops two items off the stack, adds them together, pushes their sum back to the stack.

`OP_EQUAL`
Pops two items off the stack, compares their equality, pushes a boolean back to the stack.

`OP_EQUALVERIFY`
Like OP_EQUAL but throws an error and halts script execution immediately if the two items are not equal.

## Simple Cryptography

We've explored "pay to public key hash" in previous chapters. This is the bitcoin script that was written explicitly in millions of transaction outputs before segregated witness came along and abbreviated it. Coins are locked by the hash of a public key. The spender must reveal the public key that matches that hash, and then provide a signature verified by that public key.

Opcodes that do simple cryptography

`OP_HASH256`
Pops one item off the stack, computes the double-SHA256 digest and pushes that digest back to the stack. In our exercise this operation is symbolized using strings. Example: The script OP_1 OP_HASH256 produces the stack [HASH256(1)]

`OP_CHECKSIG`
Pops two items off the stack. The first item it pops must be a public key in the format PUBKEY(...). The second item must be a signature in the format SIG(...). If the strings inside the parentheses in both items are equal we consider that a valid ECDSA signature and push TRUE back to the stack, otherwise FALSE

## Multisig

Multisignature policies provide a list of public keys and a number of signatures required for a valid spend. It can be described as "m-of-n" meaning "m number of signatures are required from this list of n public keys". The public keys and the m and n values are typically included in the locking script and the spender only needs to provide the right number of signatures.

### OP_CHECKMULTISIG

Processes m-of-n multisignature by following this algorithm.

- Pop a single integer off the stack. This is the n value.
- Pop n number of items off the stack, these are all expected to be public keys of the format PUBKEY(...)
- Pop a single integer off the stack. This is the m value.
- Pop m number of items off the stack, these are all expected to be signatures of the format SIG(...)
- Pop an extra element off the stack for absolutely no reason at all.
- Iterate through each public key: Verify the key against the stack-topmost signature. If it is valid, remove both the key and the signature and continue with the next public key. If it is not valid, remove the public key only and continue to the next public key (which will begin by checking against that same topmost signature)
- If all public keys have been tested and there are any signatures remaining, the operation fails.
- Once all signatures have been removed the operation can finish early with success, even if more public keys remain.
  Note that m <= n. There may be more public keys than signatures but never more signatures than public keys. Also note that the keys and signatures MUST be in the same order, even if some keys are not used to sign.

## Time Locks

Way back in the last century a document entitled BIP 65 proposed a new opcode to bitcoin which was eventually added to the consensus rules. It is used to require that the nLocktime of a transaction is at or above a value specified by the script. Bitcoin's consensus rules already prohibit including a transaction in a block if that block's height is greater than the transaction's nLocktime. In other words, this opcode makes a transaction unspendable until a the blockchain reaches a certain height some time in the future. Because it was added with a soft fork, it does NOT actually pop anything off the stack, meaning most uses will also require an `OP_DROP` as well. If the opcode determines it is too early to include this transaction in a block, script evaluation stops immediately with an error.

Opcodes that do block timelocks

`OP_DROP`
Pops one item off the stack, ignores it.

`OP_CHECKLOCKTIMEVERIFY`
Reads (does not pop) the top stack item and interprets it as a block height. If the height argument consumed by the opcode is not at least equal to the NEXT block height, the operation is invalid.

## 2 of 2 multisig

The first thing Vanderpoole suggests is a 2-of-2 multisig. All donations will be split between you and the Lil Bits Foundation 50/50. This will be managed by you both, with each of you signing all spending transactions from the donation address. This means you will have to agree on all withdrawals from the donation address.
