require('dotenv').config();
/**
 * Webhook Relay using smee.io
 * 
 * This script forwards Jira webhooks to GitHub Actions via smee.io
 * Run this locally or on any server that can stay online
 */

const SmeeClient = require('smee-client');
const axios = require('axios');

// Configuration
const SMEE_URL = process.env.SMEE_URL || 'https://smee.io/YOUR_UNIQUE_CHANNEL';
const GITHUB_TOKEN = process.env.GITHUB_TOKEN; // Personal Access Token with repo scope
const GITHUB_REPO = process.env.GITHUB_REPO || 'panda-mooncake-890/jira-confluence-integration';

// GitHub repository dispatch endpoint
const GITHUB_API_URL = `https://api.github.com/repos/${GITHUB_REPO}/dispatches`;

console.log('Starting webhook relay...');
console.log(`Smee URL: ${SMEE_URL}`);
console.log(`GitHub Repo: ${GITHUB_REPO}`);
console.log('');

const smee = new SmeeClient({
  source: SMEE_URL,
  target: 'http://localhost:3000/webhook', // Local endpoint
  logger: console
});

// Start the smee client
const events = smee.start();

// Simple HTTP server to receive webhooks from smee
const http = require('http');

const server = http.createServer(async (req, res) => {
  if (req.method === 'POST' && req.url.startsWith('/webhook')) {
    let body = '';
    
    req.on('data', chunk => {
      body += chunk.toString();
    });
    
    req.on('end', async () => {
      try {
        const payload = JSON.parse(body);
        console.log('Full payload:', JSON.stringify(payload, null, 2));
        
        console.log('Received webhook from Jira');
        console.log('Webhook event:', payload.webhookEvent);
        
        // Check if this is a status change to DONE
        const changelog = payload.changelog || {};
        const items = changelog.items || [];
        
        const statusChangedToDone = items.some(
          item => item.field === 'status' && item.toString.toUpperCase() === 'DONE'
        );
        
        if (statusChangedToDone) {
          console.log('✓ Status changed to DONE - triggering GitHub Actions...');
          
          // Trigger GitHub Actions via repository dispatch
          await axios.post(
            GITHUB_API_URL,
            {
              event_type: 'jira-status-updated',
              client_payload: payload
            },
            {
              headers: {
                'Authorization': `token ${GITHUB_TOKEN}`,
                'Accept': 'application/vnd.github.v3+json',
                'Content-Type': 'application/json'
              }
            }
          );
          
          console.log('✓ GitHub Actions workflow triggered successfully');
        } else {
          console.log('⊘ Status not changed to DONE - ignoring');
        }
        
        res.writeHead(200);
        res.end('OK');
        
      } catch (error) {
        console.error('Error processing webhook:', error.message);
        res.writeHead(500);
        res.end('Error');
      }
    });
  } else {
    res.writeHead(404);
    res.end('Not Found');
  }
});

server.listen(3000, () => {
  console.log('Webhook relay server listening on port 3000');
  console.log('Waiting for Jira webhooks...');
  console.log('');
});

// Handle graceful shutdown
process.on('SIGINT', () => {
  console.log('\nShutting down webhook relay...');
  events.close();
  server.close();
  process.exit(0);
});
