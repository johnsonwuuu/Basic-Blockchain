# Basic-Blockchain

Simple Blockchain simulation created in Python. Demonstrates basic concepts of Blockchain technology.

## Features
- Transaction Creation: Facilitate transactions between users.
- Transaction Validation: Checks that transations do not result in overdraft, or sum of deposits/withdrawals dont go past zero.
- Block Creation: Groups valid transactions into blocks and computes their hashes.
- Chain Integrity: Validates the entire blockchain to ensure that all blocks are correctly linked and that their contents match their hashes.

## Requirements
- Python 3.x
- `hashlib`, `json`, `sys`, `random`, and `copy` modules (included in the Python standard library)
