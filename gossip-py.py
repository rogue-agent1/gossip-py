#!/usr/bin/env python3
"""Gossip protocol simulation — epidemic information dissemination."""
import sys,random

class Node:
    def __init__(self,nid):self.id=nid;self.data={};self.peers=[]
    def update(self,key,value,version):
        if key not in self.data or self.data[key][1]<version:
            self.data[key]=(value,version);return True
        return False
    def gossip_out(self):return dict(self.data)
    def gossip_in(self,remote):
        changed=False
        for k,(v,ver) in remote.items():
            if self.update(k,v,ver):changed=True
        return changed

def simulate(n_nodes=10,rounds=10,fanout=3,seed=42):
    rng=random.Random(seed)
    nodes=[Node(i)for i in range(n_nodes)]
    for n in nodes:n.peers=[o for o in nodes if o.id!=n.id]
    # Seed data on node 0
    nodes[0].update("key1","value1",1)
    for r in range(rounds):
        for node in nodes:
            targets=rng.sample(node.peers,min(fanout,len(node.peers)))
            digest=node.gossip_out()
            for t in targets:t.gossip_in(digest)
    return nodes

def main():
    if len(sys.argv)>1 and sys.argv[1]=="--test":
        nodes=simulate(10,10,3)
        # All nodes should have the data after enough rounds
        assert all("key1" in n.data for n in nodes),f"Not converged: {[n.id for n in nodes if 'key1' not in n.data]}"
        assert all(n.data["key1"]==("value1",1) for n in nodes)
        # Multi-key
        nodes2=simulate(5,1,1)  # 1 round, fanout 1 — may not converge
        nodes2[0].update("k2","v2",1);nodes2[3].update("k3","v3",1)
        for _ in range(20):
            for n in nodes2:
                t=random.choice(n.peers);t.gossip_in(n.gossip_out())
        assert all("k2" in n.data and "k3" in n.data for n in nodes2)
        print("All tests passed!")
    else:
        nodes=simulate();print(f"After gossip: {sum(1 for n in nodes if 'key1' in n.data)}/{len(nodes)} nodes have data")
if __name__=="__main__":main()
