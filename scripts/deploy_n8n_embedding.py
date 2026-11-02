"""Admin-only workflow repair using supported n8n CLI, not credential-table access."""
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import uuid


def cli(*args):
    result = subprocess.run(['docker', 'exec', 'automation-n8n', 'n8n', *args],
                            capture_output=True, text=True, timeout=60)
    if result.returncode:
        raise RuntimeError(f'n8n CLI {args[0]} failed: {result.stderr[-300:]}')


def deploy(token, backup_dir):
    workflow_id = 'UdohyzeRmFe4no5K'
    backup_dir = Path(backup_dir)
    export = '/tmp/memex-workflow-before.json'
    cli('export:workflow', '--id=' + workflow_id, '--output=' + export)
    subprocess.run(['docker', 'cp', 'automation-n8n:' + export,
                    str(backup_dir / 'n8n-workflow-before.json')], check=True, capture_output=True)
    workflow = json.loads((backup_dir / 'n8n-workflow-before.json').read_text())[0]
    with sqlite3.connect('file:/opt/automation/n8n/data/database.sqlite?mode=ro', uri=True) as con:
        project = con.execute('SELECT projectId FROM shared_workflow WHERE workflowId=? LIMIT 1',
                              (workflow_id,)).fetchone()[0]
    credential = [{'id': 'memexembedbridge20261102', 'name': 'Memex embedding bridge',
                   'type': 'httpHeaderAuth', 'data': {'name': 'Authorization', 'value': 'Bearer ' + token}}]
    private = backup_dir / 'embedding-credential-import.json'
    private.write_text(json.dumps(credential))
    private.chmod(0o600)
    try:
        subprocess.run(['docker', 'cp', str(private), 'automation-n8n:/tmp/memex-embedding-credential.json'],
                        capture_output=True, check=True)
        cli('import:credentials', '--input=/tmp/memex-embedding-credential.json', '--projectId=' + project)
    finally:
        private.unlink(missing_ok=True)
        subprocess.run(['docker', 'exec', '-u', 'root', 'automation-n8n', 'rm', '-f',
                        '/tmp/memex-embedding-credential.json'], capture_output=True)
    code = next(n for n in workflow['nodes'] if n['type'] == 'n8n-nodes-base.code')
    text = code['parameters']['jsCode']
    text = text.replace('const input = $input.first().json;', "const input = $('Webhook').first().json;")
    text = text.replace('const vector = Array(768).fill(0);', '''const embedding = $input.first().json;
  const vector = embedding.embeddings?.[0];
  if (embedding.model !== 'nomic-embed-text:latest' || !Array.isArray(vector) ||
      vector.length !== 768 || !vector.every(Number.isFinite) || !vector.some(v => v !== 0)) {
    throw new Error('Invalid local embedding');
  }''')
    text = text.replace('// Placeholder vector to satisfy Qdrant collection schema.\n  // This keeps the workflow working, but it is not semantic recall.', '// Real local embedding; reject placeholders and model mismatch.')
    text = text.replace("source: 'memex',", "source: 'memex',\n    embedding_model: 'nomic-embed-text:latest',\n    embedding_dimensions: 768,")
    code['parameters']['jsCode'] = text
    embed = {'id': 'memex-real-local-embedding', 'name': 'Local embedding',
        'type': 'n8n-nodes-base.httpRequest', 'typeVersion': 4.2, 'position': [450, 300],
        'parameters': {'method': 'POST', 'url': 'http://192.168.1.24:11435/api/embed',
            'authentication': 'genericCredentialType', 'genericAuthType': 'httpHeaderAuth',
            'sendBody': True, 'specifyBody': 'json',
            'jsonBody': "={{ {model: 'nomic-embed-text:latest', input: 'search_document: ' + String(($json.body ?? $json).title || '') + '\\n' + String(($json.body ?? $json).summary || '')} }}",
            'options': {'timeout': 90000}},
        'credentials': {'httpHeaderAuth': {'id': 'memexembedbridge20261102', 'name': 'Memex embedding bridge'}}}
    workflow['nodes'] = [n for n in workflow['nodes'] if n['name'] != 'Local embedding'] + [embed]
    workflow['connections']['Webhook'] = {'main': [[{'node': 'Local embedding', 'type': 'main', 'index': 0}]]}
    workflow['connections']['Local embedding'] = {'main': [[{'node': code['name'], 'type': 'main', 'index': 0}]]}
    for node in workflow['nodes']:
        if node['name'] == 'HTTP Request':
            node['parameters']['url'] = 'http://192.168.1.20:6333/collections/memex-knowledge-768d/points?wait=true'
    workflow['versionId'] = str(uuid.uuid4())
    target = backup_dir / 'n8n-workflow-updated.json'
    target.write_text(json.dumps([workflow]))
    target.chmod(0o600)
    subprocess.run(['docker', 'cp', str(target), 'automation-n8n:/tmp/memex-workflow-updated.json'],
                    capture_output=True, check=True)
    cli('import:workflow', '--input=/tmp/memex-workflow-updated.json', '--projectId=' + project)
    cli('publish:workflow', '--id=' + workflow_id)
    subprocess.run(['docker', 'restart', 'automation-n8n'], capture_output=True, check=True, timeout=45)
    subprocess.run(['docker', 'exec', '-u', 'root', 'automation-n8n', 'rm', '-f',
                    '/tmp/memex-workflow-updated.json', export], capture_output=True)
    return {'workflow': workflow_id, 'embedding_node_installed': True, 'published': True}
