#!/usr/bin/python
import sys
import os
import pytz
import datetime
import json
import commands
import time
from docker import Client

if (len(sys.argv) == 2):
    sleeptime = int(sys.argv[1])
else:
    sleeptime = 60
os.system('nginx')
sock = Client(base_url='unix://var/run/docker.sock');
oldids = []
oldhttps = []
httptpl = open("/home/http.tpl")
httpstr = httptpl.read()
httptpl.close()
httpstpl = open("/home/https.tpl")
httpsstr = httpstpl.read()
httpstpl.close()
srvtpl = 'server %s:%s weight=10;'
awp_host=os.getenv('HOSTNAME');
awp_info = sock.inspect_container(container=awp_host)
awp_net = awp_info['NetworkSettings']['Networks'].keys()
while 1:
    newids = []
    newhttps = []
    news = {}
    containers = sock.containers()
    for container in containers:
        container_info = sock.inspect_container(container=container['Id'])
        container_env = {}
        if(not container_info['Config']['Env']):
            continue
        for env_item in container_info['Config']['Env']:
            env_str_arr = env_item.split('=')
            if (len(env_str_arr) == 2):
                container_env[env_str_arr[0]] = env_str_arr[1]
        if (container_env.has_key('AWP_DOMAIN')):
            domainname = container_env['AWP_DOMAIN']
            for net_key in container_info['NetworkSettings']['Networks']:
                if (net_key in awp_net):
                    if (not (news.has_key(domainname)) or not (isinstance(news[domainname], list))):
                        news[domainname] = []
                    news[domainname].append({
                        'container_name': container_info['Name'],
                        'ip': container_info['NetworkSettings']['Networks'][net_key]['IPAddress'],
                        'port': container_env['AWP_PORT'] if container_env.has_key('AWP_PORT') else '80'
                    })
                    break;
            newids.append(container['Id'])
            if os.path.exists("/https/%s/ssl.crt" % (domainname)) and os.path.exists(
                            "/https/%s/ssl.key" % (domainname)):
                newhttps.append(domainname)
    newids.sort()
    oldids.sort()
    newhttps.sort()
    oldhttps.sort()
    if (newids != oldids or newhttps != oldhttps):
        tz = pytz.timezone('Asia/Shanghai')
        print 'Find new change , the servers will reconfig '.ljust(56, "."), (
            '[ %s ]' % (datetime.datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S'))).rjust(23)
        tfn = open("/etc/nginx/conf.d/auto.conf", "w+")
        configs = ''
        for key in news.keys():
            upstream = key.replace('.', '')
            upstreamsrvs = ''
            for srv in news[key]:
                newsrv = srvtpl % (srv['ip'], srv['port'])
                upstreamsrvs = "%s\n%s" % (upstreamsrvs, newsrv)
            if (key in newhttps):
                temp = httpsstr.replace('%upstream%', upstream)
                temp = temp.replace('%servers%', upstreamsrvs)
                temp = temp.replace('%domainname%', key)
                temp = temp.replace('%sslpem%', "/https/%s/ssl.crt" % (key))
                temp = temp.replace('%sslkey%', "/https/%s/ssl.key" % (key))
            else:
                temp = httpstr.replace('%upstream%', upstream)
                temp = temp.replace('%servers%', upstreamsrvs)
                temp = temp.replace('%domainname%', key)
            configs = "%s\n%s" % (configs, temp)
        tfn.write(configs)
        tfn.close()
        oldhttps = newhttps
        print '-> check new config file '.ljust(68, "."),
        ret = commands.getoutput('nginx -t')
        if ret.find('successful') == -1:
            print ' [ Failed ]'
            print '-> Error:'
            print ret
            print '-> Please check your configs , will do nothings'
            print "\n"
        else:
            print "[ SUCCESS ]"
            print '-> reload config'.ljust(68, "."),
            ret = commands.getoutput('nginx -s reload')
            if ret.find('error') == -1:
                print "[ SUCCESS ]"
                oldids = newids
                oldhttps = newhttps
                print " Sites List ".center(80, "-")
                print "|", ('* Sites: %s *' % (len(news))).center(38), ('* Containers: %s *' % (len(newids))).center(
                        38), "|"
                print "".center(80, "-")
                for key in news.keys():
                    if key in newhttps:
                        prot = "https"
                    else:
                        prot = "http"
                    print ("|- [ %s://%s ]" % (prot, key)).ljust(40), ("[ Containers: %d ] " % (len(news[key]))).rjust(
                            40)
                    for nitem in news[key]:
                        print ("|    |- %s " % (nitem['container_name'])).ljust(60), nitem['ip'].ljust(15), nitem[
                            'port'].ljust(5)
                    print "|", "".center(78, "`")
                print "\n"

            else:
                print ' [ Failed ]'
                print '-> Error : nginx server have error , will restart'.ljust(80)
                exit()
    time.sleep(sleeptime)
    pass
