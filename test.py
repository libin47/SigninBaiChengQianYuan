# -*- coding: utf-8 -*-
import requests
import json


if __name__=='__main__':
    url = "http://dev.new-norm.c75d8bc666510432fa0201ebf36ebef4e.cn-hangzhou.alicontainer.com/"
    findCollege = url + 'findCollege'
    findBatch = url + 'findBatchInfo'
    token = "5wUkP4xyKj34RxsOF3EppNTZtEerY0dpnTZBt75ibkc="

    for i in range(30):
        province_id = i + 1
        pay_batch = json.dumps({"province_id": province_id, "token": token})
        r = requests.post(findBatch, data=pay_batch)
        if r.status_code==200:
            print("[%s]:批次获取成功"%province_id)
            batch_dict = json.loads(r.text)['batch_info']
            for batch in batch_dict:
                print("[%s]:[%s]:%s"%(province_id, batch['batch_norm'], batch["goal_years"]))
                if batch['wenli'] == 0:
                    wenli = [0]
                elif batch['wenli'] == 12:
                    wenli = [1, 2]
                elif batch['wenli'] == 12:
                    wenli = [21, 22]
                for wl in wenli:
                    pay_college = json.dumps({"province_id": province_id, "token": token,
                                              "wenli":wl, "score":555, "rank":55555, "batch_text":batch})
                    r_college = requests.post(findCollege, data=pay_college)
                    if r_college.status_code!=200:
                        print("error!")

        print(666)


    print(666)
    print(666)
    print(666)
