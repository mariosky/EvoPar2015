__author__ = 'mariosky'


from one_max import initialize, work
import time, yaml



config = yaml.load(open("conf/conf.yaml"))

experiment = "w%d-%d-p%d" % (config["NUMBER_OF_WORKERS"], config["RETURN_RATE"]*100,config["POPULATION_SIZE"])
experiment_id = experiment + "-%d" % round(time.time(),0)

datafile = open("data/one_max-"+experiment_id+".dat","a")
conf_out = open("conf/one_max-"+experiment_id+".yaml","w")
yaml.dump(config, conf_out)
conf_out.close()

for i in range(2):
    start = time.time()

    init_job = initialize.delay(config=config)
    while not init_job.ready():
        time.sleep(2)
        print "waiting to initialize"
    print "EvoSpace Initialized"

    tInitialize = time.time()-start
    print i, tInitialize

    params = [(w, config) for w in range(config["NUMBER_OF_WORKERS"])]

    jids = map(work.delay, params )
    results_list = []
    while jids:
        time.sleep(2)
        print "Working"
        for job in jids:
            if job.ready():
                if job.status == 'FAILURE':
                    print job.traceback
                time.sleep(2)
                r = job.get()
                print r
                results_list.append(r)
                jids.remove(job)

    tTotal = time.time()-start
    totals = "%d,%0.2f,%0.2f" % (i, round(tTotal,2), round(tInitialize,2))
    print totals
    datafile.write(totals + '\n')
    for worker_list in results_list:
        for data_list in worker_list:
            datafile.write(str(i) +"," + ",".join(map(str,data_list)) + '\n')