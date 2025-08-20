# CDAI Ethanol Engine Prototype — v2 with Hardhat Wiring

This update adds:
1. Worker integration with a local Hardhat node for tx submission.
2. Solidity contract tests and a Hardhat deploy script.

---

## New Files

### /scripts/deploy.js
```javascript
const hre = require("hardhat");

async function main() {
  const [deployer] = await hre.ethers.getSigners();
  console.log("Deploying contracts with the account:", deployer.address);

  const BurnController = await hre.ethers.getContractFactory("BurnController");
  const burnController = await BurnController.deploy(deployer.address);
  await burnController.deployed();
  console.log("BurnController deployed to:", burnController.address);

  const CreamVault = await hre.ethers.getContractFactory("CreamVault");
  const creamVault = await CreamVault.deploy(deployer.address);
  await creamVault.deployed();
  console.log("CreamVault deployed to:", creamVault.address);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
```

---

### /test/contracts.test.js
```javascript
const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("Contracts", function () {
  it("Should deploy BurnController and set allowed token", async function () {
    const [owner] = await ethers.getSigners();
    const BurnController = await ethers.getContractFactory("BurnController");
    const burnController = await BurnController.deploy(owner.address);
    await burnController.deployed();

    const token = owner.address; // dummy address
    await burnController.setAllowedToken(token, true);
    expect(await burnController.allowedTokens(token)).to.equal(true);
  });

  it("Should deploy CreamVault and deposit entry", async function () {
    const [owner] = await ethers.getSigners();
    const CreamVault = await ethers.getContractFactory("CreamVault");
    const creamVault = await CreamVault.deploy(owner.address);
    await creamVault.deployed();

    const mandalaHash = ethers.utils.formatBytes32String("mandala_v1");
    await creamVault.deposit(owner.address, 1000, mandalaHash, 0, "strategyA");
    const entry = await creamVault.entries(0);
    expect(entry.amount).to.equal(1000);
  });
});
```

---

### /python_app/worker.py — Hardhat wiring
```python
import time
import requests
from web3 import Web3

# connect to local Hardhat node
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
PRIVATE_KEY = "<replace_with_dev_key>"
BURN_CONTROLLER_ADDR = "<replace_with_deployed_address>"
BURN_CONTROLLER_ABI = [...]  # ABI JSON array for BurnController

def send_burn_tx(token_address, amount):
    account = w3.eth.account.from_key(PRIVATE_KEY)
    contract = w3.eth.contract(address=BURN_CONTROLLER_ADDR, abi=BURN_CONTROLLER_ABI)
    tx = contract.functions.burnToken(token_address, amount).build_transaction({
        'from': account.address,
        'nonce': w3.eth.get_transaction_count(account.address),
        'gas': 200000,
        'gasPrice': w3.toWei('1', 'gwei')
    })
    signed_tx = w3.eth.account.sign_transaction(tx, private_key=PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    print(f"Burn tx sent: {tx_hash.hex()}")

# integrate into decide_action logic to send burns when triggered
```

---

## Next Steps
- Replace `<replace_with_dev_key>` and `<replace_with_deployed_address>` with local dev values.
- Fill in ABI array for BurnController.
- Run `npx hardhat compile && npx hardhat run scripts/deploy.js --network localhost` to deploy.
- Start Hardhat node with `npx hardhat node` before running the worker.

This gives you a full local loop: Mock Oracle → Worker scoring → Hardhat tx submission → Contracts executing burns/rotations.

