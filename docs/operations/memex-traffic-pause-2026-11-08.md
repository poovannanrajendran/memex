# Memex traffic pause — 8 November 2026

## Decision and reason

Pause Memex production traffic and its recurring ingestion watcher while investigating a sudden increase in Vercel Fast Data Transfer. On 8 November, the Vercel Hobby team dashboard showed 101.58 GB / 100 GB for the last 30 days. The Projects view attributed 101.45 GB (99.9%) to `memex`; the steep daily rise began around 2–3 November. Vercel's email warned that the account would be paused on 9 November unless the limit issue was addressed.

The timing overlaps the 2 November pipeline remediation, but causation has not been established. The live Quartz search index at `/static/contentIndex.json` is about 9.76 MB uncompressed and about 2.05 MB with Brotli. Each page starts a browser fetch for this index, making repeated downloads one plausible contributor. The index was CDN-cached when checked. We did not obtain Vercel's detailed top-path or client breakdown; the available metrics query required Observability Plus. Do not treat the index hypothesis as a confirmed root cause.

## Pause state recorded

- Vercel project `memex` was paused interactively by the owner on 8 November. Verification immediately after showed HTTP 503 at both `https://memex.poovi.me/` and `https://memex-poovi.vercel.app/`.
- The 15-minute watcher cron on `automation-runner-01` (`192.168.1.30`) was commented out. The original crontab was saved at `/home/labadmin/memex/crontab-before-pause-20261108.txt` (mode 0600).
- At verification, no watcher or ingestion process was running. `memex-runner.service` and the runner API remained active.
- n8n workflow `Memex → Qdrant Sync` (`UdohyzeRmFe4no5K`) remained active. Inspection showed a webhook trigger and no schedule node. No other active Memex n8n schedule was identified.
- No Memex GitHub Actions schedule or Memex systemd timer was found in the checks performed.

## Next investigation steps

1. Keep the Vercel project and watcher paused until the investigation is complete.
2. In Vercel Usage → Fast Data Transfer, select project `memex` and the period covering 2–8 November. Inspect Observability/top paths, request counts and, if available, bot, user-agent, referrer and cache details. Export or record the leading paths and dates. Observability Plus was unavailable on the Hobby account during the initial check; do not upgrade without an explicit decision.
3. Compare the top paths and daily bytes with deployed asset sizes, especially `/static/contentIndex.json`, large generated HTML pages, sitemap and media. Check request volume and cache behavior as well as response size.
4. Establish whether requests came from normal visitors, crawlers, a third-party consumer or an automated probe. Search existing runner logs and any available access logs. The local `scripts/probe_vercel.py` fetches only the homepage and does not run browser JavaScript, so that probe alone does not explain search-index downloads.
5. Review changes deployed around 2–4 November and determine whether any generated asset size, page behavior, or external indexing activity changed. Agree and verify a fix before resuming service.

## Resume instructions

Only resume after reviewing the traffic findings and deciding to restore service.

- Restore the runner's saved schedule: `ssh labadmin@192.168.1.30 'crontab /home/labadmin/memex/crontab-before-pause-20261108.txt'`. This restores the complete crontab snapshot, so first inspect it and merge any legitimate cron changes made since the backup rather than blindly overwriting them.
- Resume Vercel production traffic from the Memex repo with `vercel project resume memex`, then verify both public URLs and the homepage/search behavior.
- The n8n webhook workflow and runner API were left active. If they were independently stopped during investigation, inspect their state before restarting; do not run manual ingestion until the paused schedule and service state are understood.
- After resuming, monitor Fast Data Transfer daily and re-pause if the same sharp increase returns.

## Evidence limits

The usage total and project attribution came from the owner's Vercel dashboard screenshot. Public HTTP checks confirmed the pause. The checks did not identify the exact high-volume URL, requester, or root cause. Preserve this distinction in future incident notes.
