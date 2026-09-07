"""Offline reference model. Trusted local callers only; no network authentication."""
from dataclasses import dataclass
import copy
import hashlib
import json
import sqlite3

class Denied(ValueError):
    pass

@dataclass(frozen=True)
class Principal:
    user: str
    org: str
    agent: bool = False

class Marketplace:
    def __init__(self, path=':memory:'):
        self.db = sqlite3.connect(path)
        self.db.executescript('''
        CREATE TABLE IF NOT EXISTS members(user TEXT, org TEXT, role TEXT, PRIMARY KEY(user,org));
        CREATE TABLE IF NOT EXISTS objects(id TEXT PRIMARY KEY, kind TEXT, owner TEXT, data TEXT);
        CREATE TABLE IF NOT EXISTS events(seq INTEGER PRIMARY KEY, object_id TEXT, actor TEXT, action TEXT, previous TEXT, digest TEXT);
        ''')

    def enroll(self, user, org, role):
        """Trusted bootstrap API, never expose as a public endpoint."""
        if role not in {'buyer','supplier','reviewer'}: raise Denied('Unknown role')
        with self.db: self.db.execute('INSERT INTO members VALUES(?,?,?)', (user,org,role))

    def revoke(self, user, org):
        with self.db: self.db.execute('DELETE FROM members WHERE user=? AND org=?',(user,org))

    def _role(self, p, allowed):
        row = self.db.execute('SELECT role FROM members WHERE user=? AND org=?',(p.user,p.org)).fetchone()
        if not row or row[0] not in allowed: raise Denied('Membership or role denied')

    def _human(self,p):
        if p.agent: raise Denied('Human approval required')

    def _load(self, ident):
        row = self.db.execute('SELECT kind,owner,data FROM objects WHERE id=?',(ident,)).fetchone()
        if not row: raise Denied('Object unavailable')
        return row[0], row[1], json.loads(row[2])

    def _event(self, ident, p, action):
        prev = self.db.execute('SELECT digest FROM events ORDER BY seq DESC LIMIT 1').fetchone()
        prev = prev[0] if prev else '0'*64
        actor = p.org + ':' + p.user + (':agent' if p.agent else ':human')
        digest = hashlib.sha256(json.dumps([ident,actor,action,prev]).encode()).hexdigest()
        self.db.execute('INSERT INTO events(object_id,actor,action,previous,digest) VALUES(?,?,?,?,?)',(ident,actor,action,prev,digest))

    def _save(self, ident, kind, owner, data, p, action, new=False):
        text = json.dumps(data,allow_nan=False,sort_keys=True)
        with self.db:
            if new: self.db.execute('INSERT INTO objects VALUES(?,?,?,?)',(ident,kind,owner,text))
            else: self.db.execute('UPDATE objects SET data=? WHERE id=?',(text,ident))
            self._event(ident,p,action)

    def request(self, p, ident, title, criteria, suppliers):
        self._role(p,{'buyer'}); self._human(p)
        if not title.strip() or not criteria or not all(isinstance(x,str) and x.strip() for x in criteria): raise Denied('Acceptance criteria required')
        if not suppliers or p.org in suppliers: raise Denied('Independent invited supplier required')
        data={'title':title,'criteria':list(criteria),'invited':list(suppliers),'state':'open'}
        self._save(ident,'request',p.org,data,p,'request_created',True)

    def read(self,p,ident):
        self._role(p,{'buyer','supplier','reviewer'})
        kind,owner,data=self._load(ident)
        allowed={owner}
        if kind=='request': allowed.update(data['invited'])
        if kind=='proposal' and data['state']=='submitted': allowed.add(data['buyer'])
        if kind=='engagement': allowed.add(data['supplier'])
        if p.org not in allowed: raise Denied('Organization boundary')
        return copy.deepcopy(data)

    def propose(self,p,ident,request_id,cents,scope):
        self._role(p,{'supplier'})
        kind,buyer,request=self._load(request_id)
        if kind!='request' or p.org not in request['invited'] or request['state']!='open': raise Denied('Request unavailable')
        if type(cents) is not int or cents<=0 or not scope.strip(): raise Denied('Valid price and scope required')
        data={'request':request_id,'buyer':buyer,'cents':cents,'currency':'USD','scope':scope,'state':'draft'}
        self._save(ident,'proposal',p.org,data,p,'proposal_drafted',True)

    def submit(self,p,ident):
        self._role(p,{'supplier'}); self._human(p)
        kind,owner,data=self._load(ident)
        if kind!='proposal' or owner!=p.org or data['state']!='draft': raise Denied('Submission denied')
        data['state']='submitted'
        self._save(ident,kind,owner,data,p,'supplier_approved')

    def engage(self,p,ident,proposal_id):
        self._role(p,{'buyer'}); self._human(p)
        kind,supplier,proposal=self._load(proposal_id)
        if kind!='proposal' or proposal['buyer']!=p.org or proposal['state']!='submitted': raise Denied('Proposal unavailable')
        _,owner,request=self._load(proposal['request'])
        if request['state']!='open': raise Denied('Request already awarded')
        data={'supplier':supplier,'proposal':proposal_id,'criteria':request['criteria'],'scope':proposal['scope'],'cents':proposal['cents'],'state':'active','artifact':None,'payment':'disabled'}
        # One transaction binds immutable proposal terms and prevents a second award.
        with self.db:
            self.db.execute('INSERT INTO objects VALUES(?,?,?,?)',(ident,'engagement',p.org,json.dumps(data)))
            request['state']='awarded'
            self.db.execute('UPDATE objects SET data=? WHERE id=?',(json.dumps(request),proposal['request']))
            self._event(ident,p,'buyer_approved_reference_engagement')

    def deliver(self,p,ident,artifact):
        self._role(p,{'supplier'}); self._human(p)
        kind,owner,data=self._load(ident)
        if kind!='engagement' or data['supplier']!=p.org or data['state'] not in {'active','changes_requested'}: raise Denied('Delivery denied')
        if not artifact.strip(): raise Denied('Artifact reference required')
        data.update(state='submitted',artifact=artifact)
        self._save(ident,kind,owner,data,p,'milestone_submitted')

    def review(self,p,ident,accept,checks):
        self._role(p,{'buyer','reviewer'}); self._human(p)
        kind,owner,data=self._load(ident)
        if kind!='engagement' or owner!=p.org or data['state']!='submitted': raise Denied('Review denied')
        if type(accept) is not bool: raise Denied('Explicit decision required')
        if accept and (set(checks)!=set(data['criteria']) or any(v is not True for v in checks.values())): raise Denied('All criteria need explicit acceptance')
        data.update(state='accepted' if accept else 'changes_requested',checks=checks)
        self._save(ident,kind,owner,data,p,'milestone_accepted' if accept else 'changes_requested')

    def events(self,p,ident):
        self.read(p,ident)
        return self.db.execute('SELECT actor,action FROM events WHERE object_id=? ORDER BY seq',(ident,)).fetchall()

    def pay(self,*args): raise Denied('Payments disabled in reference pilot')

    def list_service(self,p,ident,title,tags,evidence,public=False):
        self._role(p,{'supplier'}); self._human(p)
        if not title.strip() or not tags or not evidence.strip() or type(public) is not bool: raise Denied('Listing evidence and consent required')
        self._save(ident,'service',p.org,{'title':title,'tags':list(tags),'evidence':evidence,'public':public,'verification':'supplier_asserted'},p,'listing_created',True)

    def discover(self,terms):
        """Public opted-in service metadata only. No person profiling or private graph."""
        wanted={x.casefold() for x in terms}
        results=[]
        for ident,owner,raw in self.db.execute("SELECT id,owner,data FROM objects WHERE kind='service'"):
            data=json.loads(raw)
            overlap=sorted(wanted & {x.casefold() for x in data['tags']})
            if data['public'] and overlap: results.append({'id':ident,'supplier':owner,**data,'matched_tags':overlap})
        return sorted(results,key=lambda r:(-len(r['matched_tags']),r['id']))
