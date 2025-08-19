require("dotenv").config();
const { ethers } = require("ethers");

const RPC_URL = process.env.RPC_URL;
const signer = new ethers.Wallet(
  process.env.PRIVATE_KEY,
  new ethers.providers.JsonRpcProvider(RPC_URL)
);

const GOV_ADDR = process.env.GOVERNOR_ADDRESS;
const BURN_CONTROLLER = process.env.BURN_CONTROLLER;
const TOKEN = process.env.TOKEN_ADDRESS;

const GovernorABI = [
  "function propose(address[] targets, uint256[] values, bytes[] calldatas, string description) returns (uint256)",
];

const BurnControllerABI = [
  "function burnToken(address token, uint256 amount) external",
];

async function buildBurnProposal(burnAmountRaw, rationale) {
  const burnIface = new ethers.utils.Interface(BurnControllerABI);
  const calldata = burnIface.encodeFunctionData("burnToken", [TOKEN, burnAmountRaw]);

  const targets = [BURN_CONTROLLER];
  const values = [0];
  const calldatas = [calldata];
  const description = `Ethanol Engine Proposal: burn ${ethers.utils.formatUnits(
    burnAmountRaw,
    18
  )} MDX\n\nRationale:\n${rationale}`;

  return { targets, values, calldatas, description };
}

async function submitGovernorProposal(burnAmountRaw, rationale) {
  const gov = new ethers.Contract(GOV_ADDR, GovernorABI, signer);
  const { targets, values, calldatas, description } = await buildBurnProposal(
    burnAmountRaw,
    rationale
  );
  console.log("Submitting proposal...");
  const tx = await gov.propose(targets, values, calldatas, description);
  console.log("Proposal tx sent:", tx.hash);
  const receipt = await tx.wait();
  console.log("Proposal created; tx hash:", receipt.transactionHash);
}

async function main() {
  // Example burn: 500,000 MDX (adjust decimals)
  const burnAmount = ethers.utils.parseUnits("500000", 18);

  const rationale = `Offsetting recent inflation event and realigning supply.

- Current treasury MDX balance: TBD
- Burn amount: 500,000 MDX
- Impact simulation: TBD`;

  await submitGovernorProposal(burnAmount, rationale);
}

main().catch(console.error);
