import json
from .core import Marketplace, Principal, Denied

def run():
    m=Marketplace()
    for user,org,role in [('buyer','community-a','buyer'),('supplier','provider-a','supplier'),('outsider','community-b','buyer')]: m.enroll(user,org,role)
    b=Principal('buyer','community-a'); s=Principal('supplier','provider-a'); a=Principal('supplier','provider-a',True)
    m.request(b,'request-1','Synthetic public-channel permission review',['Scope documented','Permissions reviewed'],['provider-a'])
    m.propose(a,'proposal-1','request-1',25000,'Review supplied synthetic configuration. No live Discord or Slack access.')
    blocked=[]
    for label,operation in [('agent_commit',lambda:m.submit(a,'proposal-1')),('cross_tenant_read',lambda:m.read(Principal('outsider','community-b'),'request-1'))]:
        try: operation()
        except Denied: blocked.append(label)
    m.submit(s,'proposal-1'); m.engage(b,'engagement-1','proposal-1')
    m.deliver(s,'engagement-1','synthetic://permission-report-v1')
    m.review(b,'engagement-1',True,{'Scope documented':True,'Permissions reviewed':True})
    return {'mode':'synthetic','engagement':m.read(b,'engagement-1'),'blocked':blocked,'events':m.events(b,'engagement-1'),'production_ready':False,'money_moved':False}

if __name__=='__main__': print(json.dumps(run(),indent=2))
