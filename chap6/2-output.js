const assert = require('assert');
const bech32 = require('@savingsatoshi/bech32js');
// Use the bech32 library to find the version and data components from the address
// See the library source code for the exact definition
// https://github.com/saving-satoshi/bech32js/blob/main/bech32.js

class Output {
    constructor() {
        this.value = 0;
        this.witness_version = 0;
        this.witness_data = Buffer.alloc(0);
    }

    static from_options(addr, value) {
        assert(Number.isInteger(value));
        const self = new this();
        const { version, program } = bech32.decode('bc', addr);
        self.witness_version = version;
        self.witness_data = Buffer.from(program);
        self.value = value;
        return self;
    }

    serialize() {
        const buf = Buffer.alloc(11);
        buf.writeBigInt64LE(BigInt(this.value), 0);
        buf.writeUInt8(this.witness_data.length + 2, 8);
        buf.writeUInt8(this.witness_version, 9);
        buf.writeUInt8(this.witness_data.length, 10);
        return Buffer.concat([buf, this.witness_data]);
    }
}
