# Making a payment

Let's recap:

- You sent 100,000 satoshis to a 2-of-2 multisig output between you and Laszlo.
- You have, offline, a refund transaction that spends that output.
- That refund transaction specifies two options for how the funds can be spent:
  1. You to get all 99,000 satoshis back accounting for fees after 700 blocks, or
  2. Laszlo gets all the money if he gets the private key `REVOCATION_YOU_1` from you
- Laszlo has already signed this refund transaction, and you can sign it whenever you want to broadcast it.
- Once Laszlo signed this refund (child) transaction, you were safe to sign and broadcast the parent transaction that sends the funds to the 2-of-2 multisig.
- The transaction that funded the multisig output is called the funding transaction. Confirming it on the blockchain opens the payment channel.

The offline refund transaction that spends the output of the funding transaction is called the commitment transaction. Confirming it on the blockchain would close the channel. The first commitment transaction is your full refund because you haven't made any payments to Laszlo yet.

While the channel is open, you and Laszlo can make offline payments to each other, back and forth, by negotiating new commitment transactions and revoking old ones. As you buy more drinks, your "refund" amount will go down and Laszlo's portion of the original 100,000 satoshis locked in the multisig goes up.

# Complete the payment

Let's do another recap.

There are several off-chain transactions that spend the 100,000 satoshi (sat) output locked in the 2-of-2 multisig:

You will end up with these transactions:

```
Commitment 1 (You)
- Input 0: signed by Laszlo
- Output 0: 99,000 sats to you after 700 blocks or Laszlo with `REVOCATION_YOU_1`
- Miner fees: 1,000 sats

Commitment 2 (You)
- Input 0: signed by Laszlo
- Output 0: 98,000 sats to you after 700 blocks or Laszlo with `REVOCATION_YOU_2`
- Output 1: 1,000 sats to Laszlo
- Miner fees: 1,000 sats
```

Laszlo will end up with this transaction:

```
Commitment 2 (Laszlo)
- Input 0: signed by you
- Output 0: 1,000 sats to Laszlo after 700 blocks or you with REVOCATION_LASZLO_1
- Output 1: 98,000 sats to you
- Miner fees: 1,000 sats
```


All three of these transactions are signed and valid, but Laszlo hasn't handed you a Lightning Lemonade yet. Why not? Only one thing left to do, send Laszlo your previous revocation key, `REVOCATION_YOU_1`!
