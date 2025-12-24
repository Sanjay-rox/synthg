const hre = require("hardhat");

async function main() {
  console.log("🚀 Deploying SynthGuard Consortium to Polygon Amoy...\n");

  // Get deployer account
  const [deployer] = await hre.ethers.getSigners();
  console.log("📝 Deploying with account:", deployer.address);

  // Check balance
  const balance = await hre.ethers.provider.getBalance(deployer.address);
  console.log("💰 Account balance:", hre.ethers.formatEther(balance), "MATIC\n");

  // Deploy contract
  const SynthGuardConsortium = await hre.ethers.getContractFactory("SynthGuardConsortium");
  console.log("⏳ Deploying contract...");
  
  const consortium = await SynthGuardConsortium.deploy();
  await consortium.waitForDeployment();

  const contractAddress = await consortium.getAddress();
  console.log("✅ SynthGuardConsortium deployed to:", contractAddress);
  
  // Save deployment info
  const fs = require('fs');
  const deploymentInfo = {
    network: "Polygon Amoy Testnet",
    contractAddress: contractAddress,
    deployer: deployer.address,
    timestamp: new Date().toISOString(),
    blockExplorer: `https://amoy.polygonscan.com/address/${contractAddress}`
  };
  
  fs.writeFileSync(
    'deployment-info.json', 
    JSON.stringify(deploymentInfo, null, 2)
  );
  
  console.log("\n📄 Deployment info saved to deployment-info.json");
  console.log("🔍 View on Polygonscan:", deploymentInfo.blockExplorer);
  console.log("\n✨ Deployment complete!");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error("❌ Deployment failed:", error);
    process.exit(1);
  });