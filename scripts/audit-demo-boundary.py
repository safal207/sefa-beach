"""Minimal public-demo security/privacy boundary: prevent accidental sales data and remote submission code."""
import csv
import json
import pathlib
import re
import sys
from html.parser import HTMLParser

ROOT=pathlib.Path(__file__).resolve().parents[1]
EXPECTED_HEADER=['order_id','item_id','qty','paid_unit_price_try','unit_food_cost_try','unit_packaging_cost_try','discount_try','payment_fee_try','refund_try']
class Tags(HTMLParser):
    def __init__(self):
        super().__init__();self.scripts=[];self.forms=[];self.robots=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='script' and a.get('src'):self.scripts.append(a['src'])
        if tag=='form' and (a.get('action') or a.get('method','get').lower()=='post'):self.forms.append(a)
        if tag=='meta' and a.get('name','').lower()=='robots':self.robots.append(a.get('content','').lower())

def audit(root):
    errors=[]
    for name in ['index.html','revenue-dashboard-local.html']:
        html=(root/name).read_text(encoding='utf-8')
        tags=Tags();tags.feed(html)
        if not any('noindex' in x for x in tags.robots):errors.append(name+': demo indexing unexpectedly enabled')
        if tags.scripts:errors.append(name+': external script needs explicit privacy review')
        if tags.forms:errors.append(name+': form can submit data to remote endpoint')
        for patt in [r'\bfetch\s*\(',r'\bXMLHttpRequest\b',r'\bsendBeacon\s*\(',r'\bWebSocket\s*\(']:
            if re.search(patt,html):errors.append(name+': network API needs explicit owner consent')
        if re.search(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|\bghp_[A-Za-z0-9]{36}\b|\bAKIA[A-Z0-9]{16}\b|\bsk-proj-[A-Za-z0-9_-]{25,}',html):
            errors.append(name+': potential secret accidentally embedded')
    for name,wanted in [('sales-lines-template.csv',EXPECTED_HEADER),('sales-context-template.csv',EXPECTED_HEADER+['service_date','service_hour','service_zone'])]:
        with (root/name).open(newline='',encoding='utf-8') as f:rows=list(csv.reader(f))
        if rows!=[wanted]:errors.append(name+': unexpected sales data or header drift')
    menu=json.loads((root/'menu-baseline.json').read_text(encoding='utf-8'))
    if len(menu)!=123 or len({x.get('id') for x in menu})!=123:errors.append('Catalog missing unique 123 ids')
    return errors

if __name__=='__main__':
    errors=audit(ROOT)
    for issue in errors:print('FAIL',issue)
    if errors:sys.exit(1)
    print('PASS: demo boundary — no remote order submission, no filled sales templates, no external scripts, no accidental indexing')
    print('NOTE: dashboard URL is publicly accessible and localStorage is not authenticated or encrypted. Do not upload confidential data to a publicly shared device.')
