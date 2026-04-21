import { chromium } from 'playwright';
import fs from 'fs';
import path from 'path';

async function testLinks() {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  const baseUrl = 'https://memex-poovi.vercel.app';
  
  console.log(`Starting link test on ${baseUrl}...`);
  
  const results = {
    working: [],
    broken: []
  };

  try {
    await page.goto(baseUrl);
    // Get all wiki links (they usually start with ./sources, ./entities, etc. or absolute /)
    const links = await page.evaluate(() => {
      return Array.from(document.querySelectorAll('a'))
        .map(a => a.getAttribute('href'))
        .filter(href => href && (href.startsWith('./') || href.startsWith('/')) && !href.startsWith('#'));
    });

    const uniqueLinks = [...new Set(links)];
    console.log(`Found ${uniqueLinks.length} unique internal links to test.`);

    for (const link of uniqueLinks) {
      const targetUrl = link.startsWith('/') ? `${baseUrl}${link}` : `${baseUrl}/${link.replace(/^\.\//, '')}`;
      process.stdout.write(`Testing ${targetUrl}... `);
      
      try {
        const response = await page.goto(targetUrl, { waitUntil: 'domcontentloaded', timeout: 10000 });
        const status = response.status();
        if (status === 200) {
          console.log('✅ 200');
          results.working.push(targetUrl);
        } else {
          console.log(`❌ ${status}`);
          results.broken.push({ url: targetUrl, status });
        }
      } catch (err) {
        console.log(`❌ Error: ${err.message}`);
        results.broken.push({ url: targetUrl, error: err.message });
      }
    }

  } catch (err) {
    console.error(`Failed to navigate to base URL: ${err.message}`);
  }

  await browser.close();

  console.log('\n--- Link Test Summary ---');
  console.log(`Working: ${results.working.length}`);
  console.log(`Broken: ${results.broken.length}`);
  
  if (results.broken.length > 0) {
    console.log('\nBroken Links Detail:');
    results.broken.forEach(b => console.log(`- ${b.url} (${b.status || b.error})`));
  }
  
  fs.writeFileSync('output/link_test_results.json', JSON.stringify(results, null, 2));
}

testLinks();
