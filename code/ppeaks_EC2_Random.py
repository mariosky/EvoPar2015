__author__ = 'mariosky'

from ppeaks_worker import initialize, work
import time, yaml, random



config = yaml.load(open("conf/conf.yaml"))

experiment = "w%d-%d-p%d" % (config["NUMBER_OF_WORKERS"], config["RETURN_RATE"]*100,config["POPULATION_SIZE"])
experiment_id = experiment + "-%d" % round(time.time(),0)

datafile = open("data/ppeaks-random"+experiment_id+".dat","a")
conf_out = open("conf/ppeaks-random"+experiment_id+".yaml","w")
yaml.dump(config, conf_out)
conf_out.close()



for j in range(2):
    config["MUTPB"] = random.random()
    config["CXPB"]  = random.random()
    config["SAMPLE_SIZE"] = random.randint(8,32)
    config["WORKER_GENERATIONS"] = random.randint(16, 128)
    for i in range(5):
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
        totals = "%d-%d,%0.2f,%0.2f" % (j, i, round(tTotal,2), round(tInitialize,2))
        print totals
        datafile.write(totals + '\n')
        for worker_list in results_list:
            for data_list in worker_list:
                datafile.write(str(j)+","+str(i) +"," + ",".join(map(str,data_list)) + '\n')
