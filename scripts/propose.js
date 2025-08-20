require('dotenv').config();
const { ethers } = require('ethers');

const RPC_URL = process.env.RPC_URL;
const signer = new ethers.Wallet(process.env.PRIVATE_KEY, new ethers.providers.JsonRpcProvider(RPC_URL));

const GOV_ADDR = process.env.GOVERNOR_ADDRESS;
const BURN_CONTROLLER = process.env.BURN_CONTROLLER;
const TOKEN = process.env.TOKEN_ADDRESS;

// Minimal ABIs
const GovernorABI = [
  "function propose(address[] targets, uint256[] values, bytes[] calldatas, string description) returns (uint256)"
];
const BurnControllerABI = [
  "function burnToken(address token, uint256 amount) external"
];

async function buildBurnProposal(burnAmountRaw, rationale) {
  const burnIface = new ethers.utils.Interface(BurnControllerABI);
  const calldata = burnIface.encodeFunctionData("burnToken", [TOKEN, burnAmountRaw]);
  const targets = [BURN_CONTROLLER];
  const values = [0];
  const calldatas = [calldata];
  const description = `Ethanol Engine Proposal: burn ${burnAmountRaw.toString()} of ${TOKEN}\n\nRationale:\n${rationale}`;
  return { targets, values, calldatas, description };
}

async function submitGovernorProposal(burnAmountRaw, rationale) {
  const gov = new ethers.Contract(GOV_ADDR, GovernorABI, signer);
  const p = await buildBurnProposal(burnAmountRaw, rationale);
  const tx = await gov.propose(p.targets, p.values, p.calldatas, p.description);
  console.log("proposal tx sent:", tx.hash);
  const receipt = await tx.wait();
  console.log("proposal created; receipt:", receipt.transactionHash);
}

async function main() {
  // Example: burn 1000 * 1e18
  const burnAmount = ethers.BigNumber.from("1000000000000000000000");
  const rationale = "Comp inflation spikes, propose burn to offset supply expansion. Simulation attached.";
  await submitGovernorProposal(burnAmount, rationale);
}

main().catch(console.error);
