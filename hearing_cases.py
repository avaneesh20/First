import requests
from bs4 import BeautifulSoup
import re
import sys
import json

def save_case_details( det, bench_number, item_no, item,bench,dated):
    #print("Bench Number - "+bench_number)
    #print("Item Number - "+item_no.replace('.',''))
    item_no=item_no.replace('.','').replace('(','').replace(')','')
    
    temp_dict=[]
    for i in det:
        case_d = i.split('/')
        item_value=item.split('Vs.')
        item_value_down=item_value[1].rsplit(" (",1)[0]
        temp_dict2={
                "case_type": case_d[0],
                "case_number": case_d[1],
                "case_year": case_d[2],
                "bench_number": bench_number,
                "bench":bench,
                "dated": dated,
                "item_number": item_no,
                "petitioner": item_value[0],
                "respondent": item_value_down
                }
        
        temp_dict.append(temp_dict2)
        #print("{0}\t{1}\t{2}".format(case_d[0], case_d[1], case_d[2]))
    #print(item)
    formated_json=json.dumps(temp_dict,indent=4)
    print(formated_json)
    #file=open("temp.txt","a")
    #file.write(formated_json)
    #file.close()
    #det.clear()
    
date=sys.argv[1]
resp = requests.get("http://cms.nic.in/ncdrcusersWeb/servlet/causelist.GetHtml?method=GetHtmlCL&method=GetHtml&stid=0&did=0&stdate="+date+"&selectedDate="+date+"&stName=NCDRC&distName=NCDRC")
soup = BeautifulSoup(resp.text, 'lxml')
all_docs_links=[]
for link in soup.find_all('a', href=True):
    all_docs_links.append(link['href'])
final_all_docs_links=[]
for i in range(0,len(all_docs_links)):
    if '&fmt=P' not in all_docs_links[i]:
        final_all_docs_links.append(all_docs_links[i])
    
for i in range(0,len(final_all_docs_links)-1):
    dated = final_all_docs_links[i].split('=')[-1]
    response = requests.get("http://cms.nic.in/ncdrcusersWeb/"+final_all_docs_links[i])

    soup = BeautifulSoup(response.content,"html.parser")

    p_strongs = soup.find_all('p')
    ouptut_result = []
    data_arr = []
    counter = 0
    bench_number = ''
    item_num = ''
    case_type = ''
    case_number = ''
    case_year = ''
    case_details = []
    bench=[]

    h2_strong=soup.find_all('h2')
    for h2 in h2_strong:
        if 'BY' in h2.text:
            break
        if ', PRESIDENT' in h2.text:
            bench.append(h2.text.replace('BEFORE:','').replace("HON'BLE",' ').strip().replace('\t',' ').replace('\n',' ').replace('\r',' '))
            continue
        if ', PRESIDING MEMBER' in h2.text:
            bench.append(h2.text.replace('BEFORE:','').replace("HON'BLE",' ').strip().replace('\t',' ').replace('\n',' ').replace('\r',' '))
            continue
        if 'MEMBER' in h2.text:
            bench.append(h2.text.replace("HON'BLE",' ').strip().replace('\t',' ').replace('\n',' ').replace('\r',' '))


    for ps in p_strongs:
        item = ps.text.strip().replace('\t',' ').replace('\n',' ').replace('\r',' ')
        if item != '':
            data_arr.append(item)
    flag = 0
    for item in data_arr:
    #     print("IGNORE - "+item)
        counter += 1
        if "BENCH NO." in item:
            bench_number = ''.join(re.findall("[0-9]", item))
            continue
        if item in re.findall(r"\([A-Z]\)", item) or item in ''.join(re.findall(r"[0-9].*", item)):
    #         save_case_details(case_details)
            item_num = item
            continue
        if '/' in item:
            for sp in item.split('  '):
                if len(sp.split('/')) == 3:
                    if 'M/S' not in sp:
                        case_details.append(sp)
        if 'Vs.' in item:
            save_case_details(case_details, bench_number, item_num, item,bench,dated)
            flag += 1
    #print("#################################1 PDF DONE############################################")
                