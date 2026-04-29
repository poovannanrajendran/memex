import { chromium } from 'playwright';
import fs from 'fs';

async function testLinks() {
  const baseUrl = process.env.BASE_URL || 'http://localhost:8080';

  if (baseUrl.includes('memex-poovi.vercel.app') && process.env.ALLOW_PROD_PROBE !== '1') {
    throw new Error(
      'Refusing to probe production Vercel site. Set ALLOW_PROD_PROBE=1 to override.'
    );
  }

  const browser = await chromium.launch();
  const page = await browser.newPage();

  console.log(`Starting link test on ${baseUrl}...`);

  const results = {
    working: [],
    broken: []
  };

  try {
    await page.goto(baseUrl, { waitUntil: 'domcontentloaded', timeout: 15000 });

    const links = await page.evaluate(() => {
      return Array.from(document.querySelectorAll('a'))
        .map(a => a.getAttribute('href'))
        .filter(href => href && (href.startsWith('./') || href.startsWith('/')) && !href.startsWith('#'));
    });

    const uniqueLinks = [...new Set(links)];
    console.log(`Found ${uniqueLinks.length} unique internal links to test.`);

    // If we have thousands of links, let's cap it in "safe mode" to avoid request floods
    const linksToTest = process.env.ALLOW_PROD_PROBE === '1' ? uniqueLinks : uniqueLinks.slice(0, 50);
    if (uniqueLinks.length > 50 && process.env.ALLOW_PROD_PROBE !== '1') {
        console.log(`Safety cap: Testing first 50 links only. Set ALLOW_PROD_PROBE=1 for full walk.`);
    }

    for (const link of linksToTest) {
      const targetUrl = link.startsWith('/')
        ? `${baseUrl}${link}`
        : `${baseUrl}/${link.replace(/^\.\//, '')}`;

      process.stdout.write(`Testing ${targetUrl}... `);

      try {
        const response = await page.goto(targetUrl, {
          waitUntil: 'domcontentloaded',
          timeout: 10000
        });

        const status = response?.status?.() ?? 0;
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

  fs.mkdirSync('output', { recursive: true });
  fs.writeFileSync('output/link_test_results.json', JSON.stringify(results, null, 2));
}

testLinks();
