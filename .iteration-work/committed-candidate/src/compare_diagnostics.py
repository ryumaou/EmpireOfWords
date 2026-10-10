#!/usr/bin/env python3
"""Compare two Empire Of Words diagnostic runs by sentence ID, not totals alone."""
import argparse, collections, json, re
from pathlib import Path

def parse(path):
    text=Path(path).read_text(encoding='utf-8-sig')
    version=re.search(r'^Translator version: (.+)$',text,re.M)
    total=re.search(r'^Sentences: (\d+)$',text,re.M)
    summary={k:int(v) for k,v in re.findall(r'^(Complete|Partial|Missing vocabulary|Unsupported grammar): (\d+)$',text,re.M)}
    records={}
    pat=re.compile(r'^#(\d+) (.+)\n  Status: ([^\n]+)\n  Reason: ([^\n]+)',re.M)
    for m in pat.finditer(text):
        sid=int(m.group(1))
        if sid in records: raise ValueError(f'duplicate sentence #{sid} in {path}')
        records[sid]={'sentence':m.group(2),'status':m.group(3),'reason':m.group(4)}
    if not total or not version or sum(summary.values())!=int(total.group(1)):
        raise ValueError(f'invalid/incomplete diagnostics summary: {path}')
    if len(records)!=int(total.group(1))-summary.get('Complete',0):
        raise ValueError(f'diagnostic per-sentence records do not match non-complete count: {path}')
    return {'version':version.group(1),'total':int(total.group(1)),'summary':summary,'records':records}

def compare(before,after):
    if before['total']!=after['total']:raise ValueError('corpus size differs')
    ids=set(before['records'])|set(after['records'])
    changed=[]
    for sid in sorted(ids):
        b=before['records'].get(sid);a=after['records'].get(sid)
        bs=b['status'] if b else 'ok'; ast=a['status'] if a else 'ok'
        if bs!=ast or (b and a and b['reason']!=a['reason']):
            changed.append({'id':sid,'sentence':(a or b)['sentence'],'before':bs,'after':ast,'before_reason':b['reason'] if b else '', 'after_reason':a['reason'] if a else ''})
    return {'before_version':before['version'],'after_version':after['version'],'before':before['summary'],'after':after['summary'],'changes':changed,'newly_noncomplete':[r for r in changed if r['before']=='ok' and r['after']!='ok'],'newly_complete':[r for r in changed if r['before']!='ok' and r['after']=='ok']}

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--before',required=True);ap.add_argument('--after',required=True);ap.add_argument('--output')
    args=ap.parse_args();result=compare(parse(args.before),parse(args.after))
    lines=[f"Versions: {result['before_version']} -> {result['after_version']}",f"Totals: {result['before']} -> {result['after']}",f"Newly non-complete: {len(result['newly_noncomplete'])}; newly complete: {len(result['newly_complete'])}"]
    for r in result['changes']:lines.append(f"#{r['id']} {r['before']} -> {r['after']}: {r['sentence']} | {r['after_reason']}")
    report='\n'.join(lines)+'\n'
    if args.output:Path(args.output).write_text(report,encoding='utf-8')
    print(report,end='')
if __name__=='__main__':main()
