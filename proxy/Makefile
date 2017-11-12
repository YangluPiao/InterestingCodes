NETSIM = ./netsim.py
PROXY =./proxy
start: ./proxy
	cd ../netsim && $(NETSIM) ../topos/topo1 start
run: ../topos/topo1/topo1.events
	cd ../netsim && $(NETSIM) -l log.txt ../topos/topo1 run
p11: 
	$(PROXY) log1_1.txt 0.1 2000 1.0.0.1 3.0.0.1
p15: 
	$(PROXY) log1_5.txt 0.5 2000 1.0.0.1 3.0.0.1
p19: 
	$(PROXY) log1_9.txt 0.9 2000 1.0.0.1 3.0.0.1
p21: 
	$(PROXY) log2_1.txt 0.1 3000 2.0.0.1 4.0.0.1
p25: 
	$(PROXY) log2_5.txt 0.5 3000 2.0.0.1 4.0.0.1
p29: 
	$(PROXY) log2_9.txt 0.9 3000 2.0.0.1 4.0.0.1
plot1:
	../plot/grapher.py ../netsim/log.txt log1_1.txt log2_1.txt 1
plot5:
	../plot/grapher.py ../netsim/log.txt log1_5.txt log2_5.txt 5
plot9:
	../plot/grapher.py ../netsim/log.txt log1_9.txt log2_9.txt 9