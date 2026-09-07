import unittest
import sqlite3
from marketplace import Marketplace, Principal, Denied
from marketplace.connectors import Grant, preflight
from marketplace.demo import run

class MarketTests(unittest.TestCase):
    def setUp(self):
        self.m=Marketplace()
        for u,o,r in [('b','buyer','buyer'),('s','supplier','supplier'),('x','other','buyer'),('r','buyer','reviewer')]: self.m.enroll(u,o,r)
        self.b=Principal('b','buyer'); self.s=Principal('s','supplier'); self.x=Principal('x','other')
        self.m.request(self.b,'r','Assessment',['Evidence reviewed'],['supplier'])
    def proposal(self): self.m.propose(self.s,'p','r',10000,'Synthetic review')
    def engagement(self):
        self.proposal(); self.m.submit(self.s,'p'); self.m.engage(self.b,'e','p')
    def test_full_demo(self):
        result=run(); self.assertEqual(result['engagement']['state'],'accepted'); self.assertFalse(result['money_moved'])
    def test_cross_org_request(self):
        with self.assertRaises(Denied): self.m.read(self.x,'r')
    def test_invited_supplier_read(self): self.assertEqual(self.m.read(self.s,'r')['state'],'open')
    def test_revocation(self):
        self.m.revoke('s','supplier')
        with self.assertRaises(Denied): self.m.read(self.s,'r')
    def test_agent_cannot_submit(self):
        self.proposal()
        with self.assertRaises(Denied): self.m.submit(Principal('s','supplier',True),'p')
    def test_agent_cannot_award(self):
        self.proposal(); self.m.submit(self.s,'p')
        with self.assertRaises(Denied): self.m.engage(Principal('b','buyer',True),'e','p')
    def test_draft_cannot_award(self):
        self.proposal()
        with self.assertRaises(Denied): self.m.engage(self.b,'e','p')
    def test_duplicate_award(self):
        self.engagement()
        with self.assertRaises(Denied): self.m.engage(self.b,'e2','p')
    def test_supplier_cannot_accept(self):
        self.engagement(); self.m.deliver(self.s,'e','synthetic://report')
        with self.assertRaises(Denied): self.m.review(self.s,'e',True,{'Evidence reviewed':True})
    def test_incomplete_acceptance(self):
        self.engagement(); self.m.deliver(self.s,'e','synthetic://report')
        with self.assertRaises(Denied): self.m.review(self.b,'e',True,{})
    def test_rework(self):
        self.engagement(); self.m.deliver(self.s,'e','synthetic://v1'); self.m.review(self.b,'e',False,{})
        self.m.deliver(self.s,'e','synthetic://v2'); self.m.review(self.b,'e',True,{'Evidence reviewed':True})
        self.assertEqual(self.m.read(self.b,'e')['artifact'],'synthetic://v2')
    def test_audit_access(self):
        self.engagement()
        with self.assertRaises(Denied): self.m.events(self.x,'e')
    def test_price_validation(self):
        for price in [True,0,-1,float('nan'),1.5]:
            with self.assertRaises(Denied): self.m.propose(self.s,'p','r',price,'scope')
    def test_copy_isolation(self):
        self.m.read(self.b,'r')['criteria'].clear()
        self.assertEqual(self.m.read(self.b,'r')['criteria'],['Evidence reviewed'])
    def test_pay_disabled(self):
        with self.assertRaises(Denied): self.m.pay()
    def test_catalog_consent(self):
        self.m.list_service(self.s,'private','Private',['governance'],'synthetic://e')
        self.m.list_service(self.s,'public','Public',['governance'],'synthetic://e',True)
        self.assertEqual([r['id'] for r in self.m.discover(['governance'])],['public'])
    def test_wrong_actor_delivery(self):
        self.engagement()
        with self.assertRaises(Denied): self.m.deliver(self.b,'e','synthetic://report')
    def test_duplicate_id_atomic(self):
        self.proposal()
        before=self.m.db.execute('SELECT COUNT(*) FROM events').fetchone()[0]
        with self.assertRaises(sqlite3.IntegrityError): self.proposal()
        self.assertEqual(before,self.m.db.execute('SELECT COUNT(*) FROM events').fetchone()[0])

class ConnectorTests(unittest.TestCase):
    def setUp(self):
        self.g=Grant('org','member','opportunities',('channel',),100,'synthetic-admin-reference')
        self.args=dict(org='org',member='member',purpose='opportunities',channel='channel',visibility='public',shared=False,action='read',now=1)
    def test_valid_preflight(self): self.assertTrue(preflight(self.g,**self.args))
    def test_rejected_boundaries(self):
        for field,values in {'visibility':['private','dm',None],'shared':[True,None],'purpose':['marketing'],'org':['other'],'member':['other'],'action':['send','ban'],'now':[100,float('nan')],'channel':['unknown']}.items():
            for value in values:
                with self.subTest(field=field,value=value),self.assertRaises(Denied): preflight(self.g,**{**self.args,field:value})
    def test_revoked(self):
        from dataclasses import replace
        with self.assertRaises(Denied): preflight(replace(self.g,revoked=True),**self.args)
    def test_admin_missing(self):
        from dataclasses import replace
        with self.assertRaises(Denied): preflight(replace(self.g,admin_reference=''),**self.args)

if __name__=='__main__': unittest.main()
