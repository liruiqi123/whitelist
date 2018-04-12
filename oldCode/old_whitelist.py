# -*- coding: utf-8 -*-
import sys
import csv
import re
from sys import stdin
from gzip import GzipFile
import base64
from cStringIO import StringIO
import json
import time
import datetime
import urllib2
import subprocess

reload(sys)
sys.setdefaultencoding('utf-8')

ONE_DAY_SECONDS = 60 * 60 * 24
SIX_MONTH_SECONDS = ONE_DAY_SECONDS * 183

CUR_YEAR, CUR_MONTH = (int(x) for x in time.strftime("%Y-%m", time.localtime(time.time())).split("-"))

BadContract = set()

pt1 = re.compile("\d{12}")
pt2 = re.compile("\d{11}")
pt3 = re.compile("\d{9}")
pt4 = re.compile("\d{7}")

gt1 = re.compile("\d{11}")
gt2 = re.compile("(\d){3,4}-(\d){7,8}")
gt3 = re.compile("\d{7,8}")

with open("bad_contract.csv", "r") as csf:
    for each in csf:
        BadContract.add(each.strip())

def getNumber(line):
    global gt1, gt2, gt3
    each = line[7]

    out1 = gt1.search(each)
    if out1:
        return out1.group(0)

    out2 = gt2.search(each)
    if out2:
        return out2.group(0)

    out3 = gt3.search(each)
    if out3:
        return out3.group(0)
    return each

def checkNumber(line):
    global pt1, pt2, pt3, pt4

    each = line[7]
    if each == "NULL":
        return False

    if pt1.search(each):
        return False

    elif pt2.search(each):
        return True

    elif pt3.search(each):
        return False

    elif pt4.search(each):
        return True

    else:
        return False

def checkAge(line):
    # 需要新的生日字段，line[0] 1972-08-12
    try:
        birthday = line[0].split('-')
        birthday[0] = str(int(birthday[0]) + 60)
        birth = ''.join(birthday)

    except Exception, e:
        try:
            id_num = line[6]
            year = str(int(id_num[6:10]) + 60)
            birth = year + id_num[10:14]

        except Exception, e:
            return False

    struct_time = time.strptime(birth, "%Y%m%d")
    birth_60year = time.mktime(struct_time)

    if birth_60year < time.time():
        return False

    return True

def checkCurrentOverDue(line):
    if str(line[-21]) == '0' or line[-21] == 'NULL':
        return True

    else:
        return False

def checkHistoryOverDue(line):
    codes = line[-22]
    codes = re.sub('\n\s*', '', codes)
    codes = "'%s'" % (codes)
    codes = eval(codes)
    codes = codes.replace(' ', '')
    codes = codes.replace('\n', '')
    codes = codes.replace('\x5Cr\x5Cn','\r\n')
    line = codes
    line = base64.b64decode(line)
    try:
        line = GzipFile('', 'r', 0, StringIO(line)).read()
    except Exception as e:
        return False
    jline = json.loads(line)

    count = 0
    for each in jline:
        if each['overdueDays'] >= 6:
            if time.time() < time.mktime(time.strptime(each['returnDate'], '%Y-%m-%d %H:%M:%S')) + SIX_MONTH_SECONDS:
                count += 1

    if count >= 3:
        return False

    return True

def checkLastBorrow(line):
    okStatus = ('正常还清', '提前结清', '减免结清', '特殊减免结清')
    if line[74] in okStatus:
        return True

    if int(line[-13]) >= 12:
        return True

    if line[-29] != 'NULL':
        if int(line[-13]) >= int(line[-29]) / 2:
            return True

    return False

def checkProductType(line):

    baseProducts = ('车主现金贷','精英贷', '精英贷（银行合作）', '新薪贷', '新薪贷（银行合作）', '新薪宜楼贷', '助业贷', '新薪贷(低)', '授薪', '自雇')
    if line[24] not in baseProducts:
        return False

    badProducts = ('助业宜楼贷',)
    restrictProducts = ('精英贷（银行合作）', '新薪贷（银行合作）')

    okStatus = ('正常还清', '提前结清', '减免结清', '特殊减免结清')

    if line[24] in badProducts:
        return False

    if int(line[-18]) >= 15:
        return False

    if line[24] in restrictProducts:
        if line[74] not in okStatus:
            return False

    return True

def checkEasyProductType(line):

    baseProducts = ('车主现金贷','精英贷', '精英贷（银行合作）', '新薪贷', '新薪贷（银行合作）', '新薪宜楼贷', '助业贷', '新薪贷(低)', '授薪', '自雇')
    if line[24] not in baseProducts:
        return False

    badProducts = ('助业宜楼贷',)
    restrictProducts = ('精英贷（银行合作）', '新薪贷（银行合作）')

    okStatus = ('正常还清', '提前结清', '减免结清', '特殊减免结清')

    # if line[24] in badProducts:
    #     return False

    if int(line[-18]) >= 30:
        return False

    if line[24] in restrictProducts:
        if line[74] not in okStatus:
            return False

    return True

def checkLoanType(line):
    if line[26] == '循环贷' and line[-25].strip() != 'NULL' and line[-25].strip() != ''  and line[-25].strip() != '\N':
        return False
    return True


def checkBusimode(line):
    donotKeep = ("0", "1", "3", "4")
    if line[74] == "还款中" and (line[-9] in donotKeep):
        return False

    return True

def checkBadContract(line):
    if line[74] == "还款中" and line[76] in BadContract:
        return False
    else:
        return True

def calcPoint(line):
    overdueDays = int(line[-11])
    if overdueDays <= 0:
        sum_delay = -0.3146

    elif overdueDays <= 5:
        sum_delay = 0.0695

    elif overdueDays <= 10:
        sum_delay = 0.4051

    else:
        sum_delay = 0.6971

    applyYear, applyMonth = (int(x) for x in line[9].split("-")[:2])
    interMonths = 12 * (CUR_YEAR - applyYear) + (CUR_MONTH - applyMonth)
    if interMonths <= 13:
        inter_month = 0.1795

    elif interMonths <= 14:
        inter_month = -0.0888

    elif interMonths <= 17:
        inter_month = -0.2814

    else:
        inter_month = -0.6701

    if line[-5].split("CR")[-1] == "NULL":
        return 10, 0.0


    crIndex = int(line[-5].split("CR")[-1])
    if crIndex <= 16:
        a_CR_50 = -0.6901

    elif crIndex <= 36:
        a_CR_50 = -0.0647

    elif crIndex <= 48:
        a_CR_50 = 0.5246

    else:
        a_CR_50 = 1.1119

    sPoint = -1.7331 + 1.0104 * sum_delay + 0.9508 * inter_month + 0.8906 * a_CR_50
    if sPoint <= -2.75000594:
        return 1, sPoint

    elif sPoint <= -2.4949063:
        return 2, sPoint

    elif sPoint <= -2.3576301:
        return 3, sPoint

    elif sPoint <= -2.01853986:
        return 4, sPoint

    elif sPoint <= -1.93792506:
        return 5, sPoint

    elif sPoint <= -1.72778426:
        return 6, sPoint

    elif sPoint <= -1.54983042:
        return 7, sPoint

    elif sPoint <= -1.41309448:
        return 8, sPoint

    elif sPoint <= -1.02499984:
        return 9, sPoint

    else:
        return 10, sPoint

def calc_details(line):
    predata = line
    codes = line[-22]
    codes = re.sub('\n\s*', '', codes)
    codes = "'%s'" % (codes)
    codes = eval(codes)
    codes = codes.replace(' ', '')
    codes = codes.replace('\n', '')
    codes = codes.replace('\x5Cr\x5Cn','\r\n')
    line = codes
    line = base64.b64decode(line)
    try:
        line = GzipFile('', 'r', 0, StringIO(line)).read()
    except Exception:
        return False

    jline = json.loads(line)

    count = 0
    lastTermDate = ""

    expected_corpus = str(jline[0]['expectReturnCorpus'])

    for each in jline:
        count += float(each['realReturnCorpus'])
        if each['realReturnAmount'] != 0:
            try:
                lastTermDate = each['returnTime'].split(' ')[0]
            except Exception as e:
                # print(each)
                lastTermDate = each['returnDate'].split(' ')[0]

    return str(count), jline[0]['returnDate'].split(' ')[0], lastTermDate, expected_corpus

def totalStream(line):
    trans_id = line[3]

    if not checkNumber(line):
        return False, "checkNumber Fail." + " transport_id: " + trans_id

    if not checkAge(line):
        return False, "checkAge Fail." + " transport_id: " + trans_id

    if not checkCurrentOverDue(line):
        return False, "checkCurrentOverDue Fail." + " transport_id: " + trans_id

    if not checkHistoryOverDue(line):
        return False, "checkHistoryOverDue Fail." + " transport_id: " + trans_id

    if not checkLastBorrow(line):
        return False, "checkLastBorrow Fail." + " transport_id: " + trans_id

    if not checkProductType(line):
        return False, "checkProductType Fail." + " transport_id: " + trans_id

    if not checkLoanType(line):
        return False, "checkLoanType Fail." + " transport_id: " + trans_id

    if not checkBusimode(line):
        return False, "checkBusimode Fail." + " transport_id: " + trans_id

    if not checkBadContract(line):
        return False, "checkBadContract Fail." + " transport_id: " + trans_id

    return True, ""

def partStream(line):
    trans_id = line[3]

    if not checkAge(line):
        return False, "checkAge Fail." + " transport_id: " + trans_id

    # if not checkLoanType(line):
    #     return False, "checkLoanType Fail." + " transport_id: " + trans_id

    if not checkEasyProductType(line):
        return False, "checkProductType Fail." + " transport_id: " + trans_id

    if not checkBadContract(line):
        return False, "checkBadContract Fail." + " transport_id: " + trans_id

    return True, ""

def modifyFile():

    failed = []
    total_pushed = 0

    retAns = []
    headers = ['ecifId', 'applyId', 'name', 'sex', 'consultationCityName', 'workPlace', 'consultationDepartName', 'phone', 'houseStatus', 'hasCar', 'doperateTime',
               'isCloseOff', 'intamortisation', 'haveReturnAmortisation', 'overdueAllDay', 'breachAmortisation', 'realSaleName', 'currentMonth',
               'scorepank', 'score', 'estimateQuota', 'contractAmount', 'loanAmount', 'repaymentAmount', 'surplustAmount',
               'indate', 'lastProduct', 'surplusTimes', 'repaymentDate', 'lastSettleTime', 'dataType', 'identityNumber', 'birthday', 'lastLoanSource',
               'lastCustomertype', 'lastCustomerLevel', 'marketChannelLev1', 'marketChannelLev2', 'identityType', 'transport_id', 'smpDepartId','stringfield1']
    first = True
    idx = 0

    cat = subprocess.Popen("hdfs dfs -cat /user/yisou/jiajincao/white_list_in/*", shell=True, stdout=subprocess.PIPE)

    num = 0
    for line in cat.stdout:
        #num += 1
        if num >= 300:
            continue
        each = line.split('\x01')
        if len(each) < 10:
            continue

        row = {}

        # 放款期数
        try:
            row['intamortisation'] = int(each[23])
        except Exception as e:
            failed.append("intamortisation convert Failed." + " trans_id: " + each[3])
            continue

        # 已还期数
        try:
            row['haveReturnAmortisation'] = int(each[-13])
        except Exception as e:
            failed.append("haveReturnAmortisation convert Failed." + " trans_id: " + each[3])
            continue

        # 逾期天数
        try:
            row['overdueAllDay'] = int(each[-11])
        except Exception as e:
            failed.append("overdueAllDay convert Failed." + " trans_id: " + each[3])
            continue

        # 计算提前结清
        details = calc_details(each)
        if not details:
            failed.append("returnList format Failed." + " trans_id: " + each[3])
            continue

        # 已还金额
        # 首个还款日
        row['repaymentAmount'] = details[0]
        row['repaymentDate'] = details[1]

        # 未还金额 与 未还期数
        okStatus = ('正常还清', '提前结清', '减免结清', '特殊减免结清')
        if each[74] in okStatus:
            row['haveReturnAmortisation'] = row['intamortisation']
            try:
                row['surplustAmount'] = float(each[-4])

            except Exception as e:
                failed.append( str(e) + " transport_id: " + each[3])
                continue
            row['surplusTimes'] = 0
        else:
            try:
                row['surplusTimes'] = int(each[23]) - int(each[-13])
                row['surplustAmount'] = float(each[-4])

            except Exception as e:
                failed.append( str(e) + " transport_id: " + each[3])
                continue

        # 结清时间 与 数据类型
        # 20171016 liruiqi修改
        # 判断新老户，dataType为1还是为2时，取白名单中settledate判断，若该字段为空，则尚未还款
        row['lastSettleTime'] = '未还清'
        if row['surplusTimes'] == 0:
            row['lastSettleTime'] = details[2]
            try:
               if each[-3] == '':
                   period = 0
               else:
                   period = int( (time.time() - time.mktime(time.strptime(each[-3], '%Y-%m-%d'))) / ONE_DAY_SECONDS)
               #period = int( (time.time() - time.mktime(time.strptime(details[2], '%Y-%m-%d'))) / ONE_DAY_SECONDS)
            except Exception as e:
                print(e)
                print(each[-3])
                print(details)
                print(each)
                continue
            if period >= 731:
                row['dataType'] = 4
            else:
                row['dataType'] = 3

        elif row['surplusTimes'] == 1:
            row['dataType'] = 2

        else:
            row['dataType'] = 1


        if row['dataType'] == 4:
            test = partStream(each)

        else:
            test = totalStream(each)

        if not test[0]:
            failed.append(test[1])
            continue

        grade  = calcPoint(each)
        if grade[0] >= 7 and row['dataType'] != 4:
            failed.append("checkCalcPoint Fail." + " transport_id: " + each[3])
            continue

        row['scorepank'] = str(grade[0])

        row['transport_id'] = each[3]

        # 工作城市
        row['workPlace'] = each[50]

        if each[74] == "还款中":
            if grade[0] <= 2:
                x_times = 2

            elif grade[0] <= 4:
                x_times = 1.8

            elif grade[0] <= 6:
                x_times = 1.5

            else:
                x_times = 1.0

        else:
            if grade[0] <= 2:
                x_times = 1.8

            elif grade[0] <= 4:
                x_times = 1.5

            elif grade[0] <= 6:
                x_times = 1.2

            else:
                x_times = 1.0

        # 客户标识、主键

        # 借款编号
        row['applyId'] = each[11]

        # 客户姓名
        row['name'] = each[4]

        # 性别
        try:
            if int(each[6][16]) % 2 == 0:
                row['sex'] = "0"
            else:
                row['sex'] = "1"
        except Exception as e:
            row['sex'] = "2"
        # 进件中心省市
        row['consultationCityName'] = each[14]

        # 进件营业部
        row['consultationDepartName'] = each[13].split('-')[1]

        # 电话号码
        row['phone'] = getNumber(each)

        # 房屋状态
        if each[-7] == '1':
            row['houseStatus'] = '3'

        elif each[-7] == '3':
            row['houseStatus'] = '2'

        else:
            row['houseStatus'] = '1'

        # 有无车辆
        if each[-6] == '1':
            row['hasCar'] = '1'

        elif each[-6] == '2':
            row['hasCar'] = '2'

        elif each[-6] == '3':
            row['hasCar'] = '3'

        else:
            row['hasCar'] = '0'

        # 放款时间
        row['doperateTime'] = each[-28].split(" ")[0]

        # 还款状态
        row['isCloseOff'] = each[74]

        # 逾期状态
        row['breachAmortisation'] = '0' if row['overdueAllDay'] == 0 else '1'

        # 直属销售
        row['realSaleName'] = each[44]

        # 推送月份
        row['currentMonth'] = time.strftime('%Y%m%d', time.localtime(time.time()))

        # 评分
        row['score'] = grade[-1]

        # 合同金额
        try:
            row['contractAmount'] = float(each[-31])
        except Exception as e:
            print(str(e))
            row['contractAmount'] = 0

        # 到手金额
        try:
            row['loanAmount'] = float(each[-8])
        except Exception as e:
            print(str(e))
            row['loanAmount'] = 0

        # 下次放款预估额度
        # '精英贷', '精英贷（银行合作）', '新薪贷', '新薪贷（银行合作）', '新薪宜楼贷', '助业贷', '新薪贷(低)'
        theMaxLine = {"车主现金贷":190000, "精英贷": 190000, "新薪贷": 190000, "新薪宜楼贷": 190000, "助业贷": 150000, "授薪": 190000,
                       "精英贷（银行合作）": 190000, "新薪贷（银行合作）": 190000, "新薪贷(低)": 190000, "自雇": 150000}

        TheLine = 150000

        try:
            if float(each[-8]) > TheLine:
                nextAmount = min(float(each[-8]), theMaxLine[each[24]]) - float(row['surplustAmount'])
            else:
                nextAmount = min(float(each[-8]) * x_times, theMaxLine[each[24]], 150000) - float(row['surplustAmount'])

        except Exception as e:
            failed.append( str(e) + " transport_id: " + each[3])
            continue

        # 如果上笔到手大于150000 且 目前未结清，则向下取整。
        if each[74] not in okStatus and float(each[-8]) > TheLine:
            nextAmount = int(nextAmount) / 5000 * 5000

        else:
            nextAmount = (0 if nextAmount % 5000 == 0 else 1) * 5000 + int(nextAmount) / 5000 * 5000

        if row['dataType'] != 4 and nextAmount < 20000:
            failed.append("CheckPreTimeInhand Fail." + " transport_id: " + each[3])
            continue

        if row['dataType'] == 4:
            nextAmount = 0

        row['estimateQuota'] = nextAmount

        # 进件日期
        row['indate'] = each[9].split(" ")[0]

        # 身份证号码
        row['identityNumber'] = each[6]

        # 生日
        if each[0]:
            row['birthday'] = each[0]

        else:
            row['birthday'] = each[6][6:10] + '-' + each[6][10:12] + '-' + each[6][12:14]

        # 前次放款源头
        LoanSource = {"00": "信托(机\构资产)", "01": "唐宁模式", "02": "火凤凰(P2P)", "03": "信托(贷后)", "04": "海南小贷",
                      "05": "银行模式", "06": "宜人贷", "07": "宜人贷信托" }
        if each[-9] in LoanSource:
            row['lastLoanSource'] = str(int(each[-9]))
        else:
            row['lastLoanSource'] = str(int(each[-9]))

        # 生成风险定价字段，根据前次产品判定。
        #LastProduct = {"新薪贷": ("1", "56", "E"), "精英贷": ("3", "56", "C"), "助业贷": ("5", "57", "E"), "助业宜楼贷": ("6", "57", "E"),
         #              "新薪宜楼贷": ("7", "56", "E"), "精英贷（银行合作）": ("10", "56", "C"), "新薪贷（银行合作）": ("13", "56", "E"),
          #             "新薪贷(低)": ("28", "56", "E"), "授薪": ("56", "56", ""), "自雇": ("57", "57", "")}

        #20180113 根据风控同事的最新需求，修改产品的定价等级，将E改为D，C改为B
        #同时，添加车主现金贷产品
        LastProduct = {"新薪贷": ("1", "56", "D"), "精英贷": ("3", "56", "B"), "助业贷": ("5", "57", "D"),
                       "助业宜楼贷": ("6", "57", "D"),
                       "新薪宜楼贷": ("7", "56", "D"), "精英贷（银行合作）": ("10", "56", "B"), "新薪贷（银行合作）": ("13", "56", "D"),
                       "新薪贷(低)": ("28", "56", "D"), "授薪": ("56", "56", "授薪"), "自雇": ("57", "57", "自雇"),
                       "车主现金贷": ("14", "56", "B")}


        if each[24] in LastProduct:
            row['lastProduct'], row['lastCustomertype'], row['lastCustomerLevel'] = LastProduct[each[24]]
        else:
            failed.append("Last Product Modify Error. transport_id: " + each[3])
            continue

        row['lastCustomertype'] = int(row['lastCustomertype'])
        # row['transport_id'] = each[3]

        row['ecifId'] = each[75]

        row['marketChannelLev1'] = 7
        row['marketChannelLev2'] = "城市信贷"
        row['identityType'] = 111
        row['smpDepartId'] = each[-33]
        row['stringfield1'] = each[-2]

        retAns.append(row)

        if len(retAns) >= 1000:
            total_pushed += len(retAns)
            with open('white_list_out.csv', 'a') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=headers)
                if first:
                    writer.writeheader()
                    first = False
                writer.writerows(retAns)

            with open('white_list_fail.txt', 'a') as failFile:
                for each in failed:
                    failFile.write(each + '\n')

            #url = "http://potential.jishu.idc:8080/qianke/data/alreadyCoustomerEnter"

            url = ""
            retry = 0
            print("push timestamp: " + str(time.time()) + ", push data length: " + str(len(retAns)))
            header = {'Content-Type': 'application/json', 'charset':'utf-8'}
            while retry < 1:
                retry += 1
                try:
                    request = urllib2.Request(url=url, headers=header, data=json.dumps(retAns))
                    # print(json.dumps(retAns))
                    response = urllib2.urlopen(request, timeout=30)
                    words = response.read()
                    print(words)
                    response.close()
                    #time.sleep(10)
                    retry = 3
                except Exception as e:
                    print(str(e))
                    print("Fail Part: network error!")

            retAns = []
            failed = []

    #url = "http://potential.jishu.idc:8080/qianke/data/alreadyCoustomerEnter"
    url = ""
    retry = 0
    print("push timestamp: " + str(time.time()) + ", push data length: " + str(len(retAns)))
    header = {'Content-Type': 'application/json', 'charset':'utf-8'}
    total_pushed += len(retAns)
    while retry < 1:
        retry += 1
        try:
            request = urllib2.Request(url=url, headers=header, data=json.dumps(retAns))
            # print(json.dumps(retAns))
            response = urllib2.urlopen(request, timeout=30)
            words = response.read()
            print(words)
            response.close()
            #time.sleep(1)
            retry = 3

        except Exception as e:
            print(str(e))
            print("Fail Part: network error!")

    print("total_pushed_length: " + str(total_pushed))

    with open('white_list_out.csv', 'a') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        if first:
            writer.writeheader()
            first = False
        writer.writerows(retAns)

    with open('white_list_fail.txt', 'a') as failFile:
        for each in failed:
            failFile.write(each + '\n')

if __name__ == "__main__":
    modifyFile()

