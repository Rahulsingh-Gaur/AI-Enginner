#!/usr/bin/env python3
"""Generate beautiful PDF from markdown using Playwright"""
from playwright.sync_api import sync_playwright
from pathlib import Path
import markdown

# Read markdown
md_content = Path('pdf.md').read_text(encoding='utf-8')

# Convert to HTML
html_body = markdown.markdown(md_content, extensions=['tables', 'fenced_code'])

# Full HTML with styling
html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        @page {{
            size: A4;
            margin: 2cm;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }}
        h1 {{
            color: #1a5276;
            font-size: 24px;
            border-bottom: 3px solid #1a5276;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #2874a6;
            font-size: 20px;
            margin-top: 30px;
            border-left: 4px solid #2874a6;
            padding-left: 10px;
        }}
        h3 {{
            color: #2e86ab;
            font-size: 16px;
            margin-top: 25px;
        }}
        h4 {{
            background: #eaf2f8;
            padding: 10px;
            border-radius: 5px;
            color: #1a5276;
        }}
        strong {{
            color: #1a5276;
        }}
        ul, ol {{
            padding-left: 25px;
        }}
        li {{
            margin-bottom: 8px;
        }}
        hr {{
            border: none;
            border-top: 2px solid #ddd;
            margin: 30px 0;
        }}
        code {{
            background: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: monospace;
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
            background: linear-gradient(135deg, #1a5276 0%, #2980b9 100%);
            color: white;
            border-radius: 10px;
        }}
        .header h1 {{
            color: white;
            border: none;
            margin: 0;
        }}
        .footer {{
            margin-top: 40px;
            padding: 20px;
            background: #1a5276;
            color: white;
            text-align: center;
            border-radius: 5px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>⚡ MSEB - Mahavitaran</h1>
        <p style="font-size: 18px; margin: 10px 0;">Standard Operating Procedure (SOP)</p>
        <p style="font-size: 14px; margin: 5px 0;">for Online Name Transfer/Change in Electricity Connection</p>
    </div>
    {html_body}
    <div class="footer">
        <p><strong>Document Prepared by Rahulsingh - 609</strong></p>
        <p>For queries: 8976258876</p>
        <p style="font-size: 12px; margin-top: 10px;">MSEB - Mahavitaran | Powering Your Life, Responsibly</p>
    </div>
</body>
</html>'''

# Save HTML
Path('output.html').write_text(html, encoding='utf-8')

# Generate PDF using Playwright
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.set_content(html)
    page.pdf(
        path='MSEB_SOP.pdf',
        format='A4',
        margin={
            'top': '2cm',
            'bottom': '2cm',
            'left': '2cm',
            'right': '2cm'
        },
        print_background=True
    )
    browser.close()

print('✅ PDF generated: MSEB_SOP.pdf')
print('✅ HTML generated: output.html')
