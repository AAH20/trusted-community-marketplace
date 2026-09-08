"""Loopback-only synthetic demo. Role buttons simulate humans, not authentication."""
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs
from html import escape
import secrets
from .core import Marketplace, Principal, Denied

m=Marketplace()
b=Principal('demo-buyer','demo-community');s=Principal('demo-supplier','demo-provider')
m.enroll(b.user,b.org,'buyer');m.enroll(s.user,s.org,'supplier')
m.list_service(s,'service','Community permission assessment',['governance','security'],'synthetic://supplier-portfolio',True)
csrf=secrets.token_urlsafe(32)
PORT=8765

def form(action,label,fields=''):
    return f'<form method="post" action="/{action}"><input type="hidden" name="csrf" value="{csrf}">{fields}<button>{label}</button></form>'

def page(message=''):
    listings=m.discover(['governance'])
    catalog=''.join(f'<li><strong>{escape(x["title"])}</strong><p>Supplier-asserted evidence. Matched tag: governance.</p></li>' for x in listings)
    try: request=m.read(b,'request');state=request['state']
    except Denied: request=None;state='No request'
    body=form('request','Create buyer request','<label>Request title<input name="title" required maxlength="140" value="Synthetic community permission review"></label>') if not request else f'<p>{escape(request["title"])}</p><p>Request state: <strong>{state}</strong></p>'
    try: proposal=m.read(s,'proposal')
    except Denied: proposal=None
    if request and not proposal: body+=form('draft','Draft proposal as supplier agent')
    if proposal:
        body+=f'<p>Proposal: {escape(proposal["state"])}. Illustrative price: USD 250.00. No charge.</p>'
        if proposal['state']=='draft': body+=form('agent-submit','Test blocked agent commitment')+form('submit','Approve proposal as supplier human')
        elif state=='open': body+=form('engage','Approve engagement as buyer human')
    try: engagement=m.read(b,'engagement')
    except Denied: engagement=None
    if engagement:
        body+=f'<p>Engagement state: <strong>{engagement["state"]}</strong>. Payments: disabled.</p>'
        if engagement['state'] in {'active','changes_requested'}:body+=form('deliver','Submit synthetic report as supplier human')
        elif engagement['state']=='submitted':body+=form('accept','Accept criteria as buyer human')+form('rework','Request changes as buyer human')
        body+='<h3>Engagement audit</h3><ol>'+''.join(f'<li>{escape(action)}</li>' for _,action in m.events(b,'engagement'))+'</ol>'
    return f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Trusted Community Marketplace Demo</title><style>
    body{{font:18px system-ui,sans-serif;background:#f2f5f7;color:#162f40;margin:0}}main{{max-width:1040px;margin:50px auto;padding:0 24px}}h1{{font-size:42px;line-height:1.15}}h2{{font-size:26px}}section{{background:white;padding:26px;margin:22px 0;border:1px solid #cbd6df;border-radius:12px}}button{{background:#195f7b;color:white;border:0;border-radius:6px;padding:12px 18px;font:inherit;cursor:pointer}}form{{margin:14px 0}}input:not([type=hidden]){{display:block;width:90%;padding:12px;font:inherit;margin:10px 0}}.notice{{padding:18px;background:#fff1cc}}a{{color:#185a79}}li{{margin:10px 0}}
    </style><main><p>A2Z SOC / LOCAL SYNTHETIC DEMO</p><h1>Trusted Community Marketplace</h1><p>Professional services with explicit human decisions.</p><p class="notice">Role buttons simulate identities. This is not production authentication. No Slack, Discord, outreach, signatures or payments. No CNCF endorsement.</p><p role="status">{escape(message)}</p><section><h2>Opted-in service catalog</h2><ul>{catalog}</ul></section><section><h2>Engagement workflow</h2>{body}</section><p><a href="https://a2zsoc.com">A2Z SOC</a> / <a href="https://github.com/AAH20/trusted-community-marketplace">Source and limitations</a></p></main></html>'''

class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args): pass
    def valid_host(self): return self.headers.get('Host')==f'127.0.0.1:{PORT}'
    def respond(self,status,message):
        data=page(message).encode();self.send_response(status)
        self.send_header('Content-Type','text/html; charset=utf-8');self.send_header('Content-Length',str(len(data)))
        self.send_header('Cache-Control','no-store');self.send_header('X-Frame-Options','DENY');self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('Content-Security-Policy',"default-src 'none'; style-src 'unsafe-inline'; form-action 'self'; frame-ancestors 'none'")
        self.end_headers();self.wfile.write(data)
    def do_GET(self):
        if not self.valid_host(): self.send_error(403);return
        self.respond(200,'Synthetic data only. Restart the process to reset the demonstration.')
    def do_POST(self):
        if not self.valid_host() or self.headers.get('Origin')!=f'http://127.0.0.1:{PORT}': self.send_error(403);return
        try: size=int(self.headers.get('Content-Length','0'))
        except ValueError:self.send_error(400);return
        if size<1 or size>4096:self.send_error(413);return
        params=parse_qs(self.rfile.read(size).decode())
        if not secrets.compare_digest(params.get('csrf',[''])[0],csrf):self.send_error(403);return
        try:
            if self.path=='/request':m.request(b,'request',params.get('title',[''])[0],['Scope documented','Permissions reviewed'],[s.org])
            elif self.path=='/draft':m.propose(Principal(s.user,s.org,True),'proposal','request',25000,'Review synthetic configuration only')
            elif self.path=='/agent-submit':m.submit(Principal(s.user,s.org,True),'proposal')
            elif self.path=='/submit':m.submit(s,'proposal')
            elif self.path=='/engage':m.engage(b,'engagement','proposal')
            elif self.path=='/deliver':m.deliver(s,'engagement','synthetic://report')
            elif self.path=='/accept':m.review(b,'engagement',True,{'Scope documented':True,'Permissions reviewed':True})
            elif self.path=='/rework':m.review(b,'engagement',False,{})
            else:self.send_error(404);return
            self.respond(200,'Demo action recorded.')
        except (Denied,ValueError) as e:self.respond(400,str(e))
        except Exception:self.respond(409,'Action unavailable in the current demo state.')

if __name__=='__main__':
    print(f'Synthetic local demo: http://127.0.0.1:{PORT}',flush=True)
    HTTPServer(('127.0.0.1',PORT),Handler).serve_forever()
