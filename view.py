#!/usr/bin/env python3
"""
Simple viewer for PM Exercise markdown files.
Run: python3 view.py
"""

import os
import webbrowser
import tempfile
import html

DIR = os.path.dirname(os.path.abspath(__file__))

# Read markdown files - 5 deliverables in exercise order
files = {
    'competitive-analysis': 'competitive-analysis.md',
    'prompt-log': 'prompt-log.md',
    'workflow-spec': 'workflow-spec.md',
    'adoption-ux-flow': 'adoption-ux-flow.md',
    'eval': 'eval.md'
}

docs = {}
for key, filename in files.items():
    filepath = os.path.join(DIR, filename)
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            # Escape backticks and backslashes for JS template literal
            content = f.read()
            content = content.replace('\\', '\\\\')
            content = content.replace('`', '\\`')
            content = content.replace('${', '\\${')
            docs[key] = content
    else:
        docs[key] = f'# File not found\n\n`{filename}` does not exist.'

# HTML template
html_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PM Exercise - Competitive Intel</title>
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: #0d1117;
            color: #c9d1d9;
            display: flex;
            height: 100vh;
        }

        /* Sidebar */
        .sidebar {
            width: 280px;
            background: #161b22;
            border-right: 1px solid #30363d;
            padding: 24px 16px;
            display: flex;
            flex-direction: column;
            flex-shrink: 0;
        }

        .sidebar h1 {
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: #8b949e;
            margin-bottom: 20px;
            padding: 0 12px;
        }

        .nav-item {
            padding: 12px 16px;
            border-radius: 8px;
            cursor: pointer;
            margin-bottom: 4px;
            transition: all 0.15s ease;
            border-left: 3px solid transparent;
        }

        .nav-item:hover {
            background: #21262d;
        }

        .nav-item.active {
            background: #1f6feb22;
            border-left-color: #58a6ff;
            color: #58a6ff;
        }

        .nav-item .title {
            font-weight: 600;
            font-size: 14px;
            margin-bottom: 4px;
        }

        .nav-item .desc {
            font-size: 12px;
            color: #8b949e;
        }

        .nav-item.active .desc {
            color: #58a6ff99;
        }

        /* Main content */
        .main {
            flex: 1;
            overflow-y: auto;
            padding: 48px 64px;
        }

        .content {
            max-width: 900px;
            margin: 0 auto;
        }

        /* Markdown styles */
        .content h1 {
            font-size: 32px;
            font-weight: 600;
            margin-bottom: 16px;
            padding-bottom: 12px;
            border-bottom: 1px solid #30363d;
            color: #f0f6fc;
        }

        .content h2 {
            font-size: 24px;
            font-weight: 600;
            margin-top: 32px;
            margin-bottom: 16px;
            color: #f0f6fc;
        }

        .content h3 {
            font-size: 18px;
            font-weight: 600;
            margin-top: 24px;
            margin-bottom: 12px;
            color: #f0f6fc;
        }

        .content p {
            line-height: 1.7;
            margin-bottom: 16px;
        }

        .content ul, .content ol {
            margin-bottom: 16px;
            padding-left: 24px;
        }

        .content li {
            line-height: 1.7;
            margin-bottom: 8px;
        }

        .content strong {
            color: #f0f6fc;
            font-weight: 600;
        }

        .content em {
            color: #a5d6ff;
        }

        .content code {
            background: #161b22;
            padding: 2px 6px;
            border-radius: 4px;
            font-family: 'SF Mono', Monaco, 'Courier New', monospace;
            font-size: 13px;
        }

        .content pre {
            background: #161b22;
            padding: 16px;
            border-radius: 8px;
            overflow-x: auto;
            margin-bottom: 16px;
            border: 1px solid #30363d;
        }

        .content pre code {
            background: none;
            padding: 0;
            white-space: pre;
        }

        .content table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 16px;
            font-size: 14px;
        }

        .content th {
            background: #161b22;
            padding: 12px 16px;
            text-align: left;
            font-weight: 600;
            border: 1px solid #30363d;
            color: #f0f6fc;
        }

        .content td {
            padding: 12px 16px;
            border: 1px solid #30363d;
            vertical-align: top;
        }

        .content tr:nth-child(even) {
            background: #161b2233;
        }

        .content hr {
            border: none;
            border-top: 1px solid #30363d;
            margin: 32px 0;
        }

        .content blockquote {
            border-left: 4px solid #3fb950;
            padding-left: 16px;
            margin: 16px 0;
            color: #8b949e;
        }

        .content a {
            color: #58a6ff;
            text-decoration: none;
        }

        .content a:hover {
            text-decoration: underline;
        }

        /* Print styles */
        @media print {
            body {
                background: white;
                color: black;
            }
            .sidebar {
                display: none;
            }
            .main {
                padding: 0;
            }
            .content {
                max-width: 100%;
            }
            .content h1, .content h2, .content h3, .content strong {
                color: black;
            }
            .content em {
                color: #0066cc;
            }
            .content table, .content th, .content td {
                border-color: #ccc;
            }
            .content th {
                background: #f5f5f5;
                color: black;
            }
            .content pre, .content code {
                background: #f5f5f5;
                border-color: #ccc;
            }
        }
    </style>
</head>
<body>
    <div class="sidebar">
        <h1>PM Exercise</h1>

        <div class="nav-item active" data-file="competitive-analysis">
            <div class="title">Competitive Analysis</div>
            <div class="desc">West Elm vs CB2 deep dive</div>
        </div>

        <div class="nav-item" data-file="prompt-log">
            <div class="title">Prompt Log</div>
            <div class="desc">Design decisions & the prompt</div>
        </div>

        <div class="nav-item" data-file="workflow-spec">
            <div class="title">Workflow Spec</div>
            <div class="desc">/competitive-intel skill</div>
        </div>

        <div class="nav-item" data-file="adoption-ux-flow">
            <div class="title">Adoption UX Flow</div>
            <div class="desc">Figma-ready wireframes</div>
        </div>

        <div class="nav-item" data-file="eval">
            <div class="title">Eval</div>
            <div class="desc">Promptfoo test results</div>
        </div>
    </div>

    <div class="main">
        <div class="content" id="content">
            <p>Loading...</p>
        </div>
    </div>

    <script>
        const docs = {
            'competitive-analysis': `''' + docs['competitive-analysis'] + '''`,
            'prompt-log': `''' + docs['prompt-log'] + '''`,
            'workflow-spec': `''' + docs['workflow-spec'] + '''`,
            'adoption-ux-flow': `''' + docs['adoption-ux-flow'] + '''`,
            'eval': `''' + docs['eval'] + '''`
        };

        let currentDoc = 'competitive-analysis';

        function loadDoc(name) {
            currentDoc = name;
            const content = docs[name];
            document.getElementById('content').innerHTML = marked.parse(content);

            document.querySelectorAll('.nav-item').forEach(item => {
                item.classList.remove('active');
                if (item.dataset.file === name) {
                    item.classList.add('active');
                }
            });
        }

        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', () => {
                loadDoc(item.dataset.file);
            });
        });

        document.addEventListener('keydown', (e) => {
            const items = ['competitive-analysis', 'prompt-log', 'workflow-spec', 'adoption-ux-flow', 'eval'];
            const currentIndex = items.indexOf(currentDoc);

            if (e.key === 'ArrowDown' || e.key === 'j') {
                const next = items[(currentIndex + 1) % items.length];
                loadDoc(next);
            } else if (e.key === 'ArrowUp' || e.key === 'k') {
                const prev = items[(currentIndex - 1 + items.length) % items.length];
                loadDoc(prev);
            }
        });

        loadDoc('competitive-analysis');
    </script>
</body>
</html>
'''

# Write to temp file and open
output_path = os.path.join(DIR, 'viewer_app.html')
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(html_template)

print(f"Opening viewer at: {output_path}")
webbrowser.open(f'file://{output_path}')
