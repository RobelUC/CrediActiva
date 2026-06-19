/**
 * Sustituye __API_URL__ en environment.production.ts durante el build en Render/CI.
 * Local: API_URL=http://localhost:8000 node scripts/set-api-url.js
 */
const fs = require('fs');
const path = require('path');

const apiUrl = (process.env.API_URL || 'http://localhost:8000').replace(/\/$/, '');
const target = path.join(__dirname, '..', 'src', 'environments', 'environment.production.ts');

let content = fs.readFileSync(target, 'utf8');
content = content.replace(/__API_URL__/g, apiUrl);
fs.writeFileSync(target, content, 'utf8');

console.log(`API URL de producción: ${apiUrl}/api/v1`);
