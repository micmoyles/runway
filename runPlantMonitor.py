import runway.plantmonitor

p = plantMonitor()
p.get_all_known_plants()
p.start()
p.updateProductionProfiles()
