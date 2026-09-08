"""Run against a fresh loopback demo. Synthetic actions only."""
import http.client, re, json
from urllib.parse import urlencode
from pathlib import Path

def request(method,path='/',data=None,origin='http://127.0.0.1:8765',host='127.0.0.1:8765'):
    c=http.client.HTTPConnection('127.0.0.1',8765,timeout=5)
    headers={'Host':host,'Origin':origin,'Content-Type':'application/x-www-form-urlencoded'}
    c.request(method,path,urlencode(data) if data is not None else None,headers)
    r=c.getresponse();text=r.read().decode();status=r.status;c.close();return status,text

results=[]
status,html=request('GET');assert status==200 and 'Opted-in service catalog' in html
csrf=re.search('name="csrf" value="([^"]+)"',html).group(1)
for name,kwargs in [('csrf',{'data':{'csrf':'invalid'}}),('origin',{'data':{'csrf':csrf},'origin':'https://example.invalid'}),('host',{'data':{'csrf':csrf},'host':'example.invalid'})]:
    status,_=request('POST','/request',**kwargs);assert status==403;results.append({'check':name,'status':status})
for action,expected,status_code in [('request','Request state: <strong>open',200),('draft','Proposal: draft',200),('agent-submit','Human approval required',400),('submit','Proposal: submitted',200),('engage','Engagement state: <strong>active',200),('deliver','Engagement state: <strong>submitted',200),('rework','changes_requested',200),('deliver','Engagement state: <strong>submitted',200),('accept','Engagement state: <strong>accepted',200)]:
    status,html=request('POST','/'+action,{'csrf':csrf,'title':'Synthetic HTTP assessment'})
    assert status==status_code and expected in html,(action,status)
    results.append({'check':action,'status':status})
report={'mode':'synthetic_http','passed':len(results),'checks':results,'browser_visual_verification':'unavailable: browser tool timed out','external_services_called':False}
Path('evidence/http-check.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
