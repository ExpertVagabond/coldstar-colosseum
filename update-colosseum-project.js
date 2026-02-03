// Colosseum Project Update Script
// Run this in your browser console while logged into colosseum.com

(async function updateColosseumProject() {
  const API_BASE = 'https://agents.colosseum.com/api';

  // Get API key from localStorage or prompt
  let apiKey = localStorage.getItem('colosseumApiKey') ||
                localStorage.getItem('apiKey') ||
                sessionStorage.getItem('apiKey');

  if (!apiKey) {
    console.log('API key not found in storage. Checking for it in the page...');
    // Try to extract from any visible elements or network requests
    const storageKeys = Object.keys(localStorage);
    console.log('LocalStorage keys:', storageKeys);

    apiKey = prompt('Please enter your Colosseum API key (starts with ahk_):');
    if (!apiKey) {
      console.error('❌ API key required to update project');
      return;
    }
  }

  console.log('✓ API key found');

  // Project update data
  const updateData = {
    technicalDemoLink: 'https://coldstar.dev/colosseum',
    presentationLink: '', // Add when video is ready
    description: 'The first air-gapped cold wallet that turns any USB drive into hardware-grade security. Coldstar enables agents and users to manage Solana assets with complete network isolation, DAO governance for multi-sig vaults, QR-based transaction signing, Jupiter DEX swaps, and Pyth price feeds. Built for maximum security in the agent economy where private keys are the most valuable asset.',
    solanaIntegration: 'Coldstar deeply integrates with Solana through: (1) Native SOL and SPL token transfers with full transaction serialization, (2) Jupiter DEX integration for secure air-gapped swaps across all Solana DEXes with best-route finding, (3) Pyth Network price feeds for real-time market data and portfolio valuation in USD, (4) Custom DAO governance program for community-managed cold storage vaults with proposal voting, (5) Voter-stake-registry program for decentralized decision-making on fund movements, (6) Integration with Solana RPC for balance queries and transaction broadcasting, (7) Air-gapped USB environment running Alpine Linux with blacklisted network drivers ensuring private keys never touch networked devices, (8) QR code-based unsigned transaction import and signed transaction export workflow for complete air-gap security, (9) Support for Solana devnet, testnet, and mainnet with configurable RPC endpoints.'
  };

  try {
    console.log('📤 Updating project...');

    // Update project
    const updateResponse = await fetch(`${API_BASE}/my-project`, {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(updateData)
    });

    if (!updateResponse.ok) {
      const error = await updateResponse.json();
      console.error('❌ Update failed:', error);
      return;
    }

    const updatedProject = await updateResponse.json();
    console.log('✅ Project updated successfully:', updatedProject);

    // Ask if ready to submit
    const readyToSubmit = confirm(
      'Project updated!\n\n' +
      'Demo link: https://coldstar.dev/colosseum\n\n' +
      'Do you want to SUBMIT the project for judging?\n' +
      '(This is IRREVERSIBLE - you cannot edit after submission)'
    );

    if (readyToSubmit) {
      console.log('📤 Submitting project for judging...');

      const submitResponse = await fetch(`${API_BASE}/my-project/submit`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${apiKey}`,
          'Content-Type': 'application/json'
        }
      });

      if (!submitResponse.ok) {
        const error = await submitResponse.json();
        console.error('❌ Submission failed:', error);
        return;
      }

      const submittedProject = await submitResponse.json();
      console.log('🎉 PROJECT SUBMITTED FOR JUDGING!', submittedProject);
      console.log('Status:', submittedProject.project.status);
      console.log('View at: https://colosseum.com/agent-hackathon/projects/coldstar-air-gapped-solana-vault');
    } else {
      console.log('ℹ️  Project updated but NOT submitted. It remains in DRAFT status.');
      console.log('You can submit later by running the submission part or using the website.');
    }

  } catch (error) {
    console.error('❌ Error:', error);
  }
})();
