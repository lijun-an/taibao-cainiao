import requests
import datetime
import copy
import json
import re
from lxml import etree


def get_data(num=None, store='', cookie=''):
    x_xsrf_token = re.findall('FE_XSRF_TOKEN=(.*?);', cookie)[0]
    if num is None or num == 0:
        query_limit = 10
    else:
        query_limit = num
    headers = {
        'authority': 'g.cainiao.com',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'zh-CN,zh;q=0.9',
        'bx-v': '2.2.3',
        'content-type': 'application/json',
        'cookie': cookie,
        'origin': 'https://g.cainiao.com',
        'referer': 'https://g.cainiao.com/store/one-plate-inventory-query/batch-inventory-query-v2',
        'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
        'x-xsrf-token': x_xsrf_token,
    }

    data = '{"storeCodes":["' + store + '"],"limit":10,"page":1,"itemParam":[]}'

    response = requests.post('https://g.cainiao.com/omni/inventory/batchInv/queryInv', headers=headers, data=data)

    data_dic = response.json()
    total = data_dic['data']['paging']['totalCount']
    if num is None:
        return total
    else:
        if total == 0:
            return
        else:
            store_data = list()
            for item in data_dic['data']['tableData']:
                # external_bar_code,warehouse_name,business_model,store_amount,production_date,expiring_date,data_time,account_id,good_quality
                store_dic = dict()
                store_dic['external_bar_code'] = item['itemBarCode']
                store_dic['business_model'] = item['channelName']
                store_dic['store_amount'] = item['qty']
                store_dic['production_date'] = item['produceDate']
                store_dic['expiring_date'] = item['expiryDate']
                store_dic['data_time'] = datetime.datetime.now().strftime("%Y%m%d")
                store_dic['good_quality'] = item['expiryDateStatus']
                store_data.append(store_dic)
            return store_data


# 获取该账户下的仓库名以及对应的value值
# 如：'菜鸟郑州保税5号仓': 'CGO504'
def get_store_map(cookie):
    x_xsrf_token = re.findall('FE_XSRF_TOKEN=(.*?);', cookie)[0]
    try:
        headers = {
            'authority': 'g.cainiao.com',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'bx-v': '2.2.3',
            'content-type': 'application/json;charset=utf-8',
            'cookie': cookie,
            'eagleeye-traceid': '43ffcb8c16635685187421046d53b9',
            'gos-lang': 'zh',
            'referer': 'https://g.cainiao.com/store/one-plate-inventory-query/warehouse-inventory-query-v2',
            'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
            'x-xsrf-token': x_xsrf_token,
        }

        response = requests.get('https://g.cainiao.com/omni/inventory/enums/storeList', headers=headers).json()
        storehouse_code_dic = dict()
        if response['success'] is True:
            for store in response['data']:
                storehouse_code_dic[store['nameCn']] = store['code']
        return storehouse_code_dic
    except:
        print('cookie信息已过期')


# 爬取指定仓库的数据
def save_data_pro(warehouse_name, cookie, ca_id=''):
    store_map = get_store_map(cookie)
    # 获取该店铺的数据总数
    # get_data中num参数为空时，返回值为数据总数，否则返回items
    if warehouse_name in store_map.keys():
        total = get_data(store=store_map[warehouse_name], cookie=cookie)
        print(warehouse_name, total)
        if total == 0:
            print(f'{warehouse_name}中无数据')
        else:
            store_data = get_data(num=total, store=store_map[warehouse_name], cookie=cookie)
            if store_data is not None:
                for item in store_data:
                    item['warehouse_name'] = warehouse_name
                    item['account_id'] = ca_id
            return store_data
    else:
        print(f'该账户没有{warehouse_name}的信息')


if __name__ == '__main__':
    store_list = ['郑州中心退货仓', '上海中心退货仓', '上海心怡中心仓', '上海基森中心仓', '郑州心怡中心退货仓', '郑州中心退货仓', '郑州B保中心仓退货仓', '郑州心怡中心仓',
                  '郑州全速通中心仓', '郑州自贸达中心仓']
    cookie = 'cna=5miXG6QbLVsCAdpMK26/pPOf; XSRF-TOKEN=afcb6f1b-5c7b-47fe-bdae-78fc3630825a; xlly_s=1; FE_XSRF_TOKEN=afcb6f1b-5c7b-47fe-bdae-78fc3630825a; cn_account_lang=zh; t=20324eba69e24879840a91575c4d6d10; _tb_token_=fed3f3bf383ee; cookie2=103b77974a79baf3d69e0562f95a532e; cancelledSubSites=empty; _hvn_login=21; lvt=1663557499460; cncc=a9c68b9915a8647a9ec207d11b690aef; TwAhx8HL=C6BCB215B673113B88DEFEF22D0D5CD441D3D197ABA710AE36592A8446521ABF4E847B432E59A0C9D0832D19BFAFC45AC52442A503A828A2DB39D28946C3782ACCB851901076809488E46F78407D132F3B8D0BE6CEC5B0E8F1C1FA5150B64F7F1E33C3BB7744616D68238ADC582305950400CF21A1A2CAC3366283F76DBC958D1CFF2FE805339F901DE6E5F3711D15E16E0633D13C9FE4C22503EDAA8505E6D3989F8F5CD189B978D910AAEA6FA8F3CBDE99D8706FF028A2D70BB94A073306A650604D558C0F23BD4DF53D6F6E5A7F981C5A154027A7409DD588568A74E1A56E4AEECD7B820787A9EFEB4CD7C0434AD043B80BE7F37BED53B4DE02F9FE885E04A99C7EBA3E7BCED7D47C3D1FD972A8148EB357FF542508D2E83FCF3E60B43442C5A0F42201FD0CE64335C0FFE8D37A19244CA5DD42FA0FC1D68B9BD5FBF8AB8B362C40944D4F2BAB24D29EC991F921F28ADE9E0085B6B98F829CB962D51A7B730B3F9CC385F52B9918A556631D4177080F4A96732762EA41ACDA4154B5B493E3E90BB7FD8C781E8BF4187CC8135CB539F6DC6634FDCB1F1EE6A5BC116BD0FABAC3BDA96CDFDA3A356A8155BD1BC5843C30372C4D02C491570216407D7C6324BBAB1A32F97147FF9E54236AAEF547BDA24403AFDCF5F481BFC3C1D51E4FC7A1846C7B3D8997548BB61A42D881084F7B10BC81B32854E53CA2601D466F0A32BDF4DF8FBA6C759A21D264413368B7D6444C5F359F0F20341BA7D3808B32C1718EA5A84B2952800ABC3D6E33B2B5AB5931B03FFD6CD97043F2950B72BD8E1D696716CC84EF2FD391A957419A7E291DE0ADDC0C07A85569121E7BB98F0904E41024532061E3CB07A6E9C0DAE22FE849659F9C4008F241F7C86C477482010B3B256F498E09B0BF9CCEFD71425333C0352B72722EE098218A299DAA548FCF2D8D4726315869C1559BA1E59AFD9154DAB7BB78FBBDE5DD77BE05034EBE8E01DF6C01C9F391BB68FBF086B4AB57ED12D94BD2F18F92B30D96403B1566F4E08322BA1F59D34A83A3FFEB479BAF8FB746889CF895E7207705DF04B388B83F51E0CFC70A81B8E02D1D651A70494F632DA926D452CD02BD3F59BF457C98F321ACE4CED1D64906D17BFCC17BC15995419C123B16793C5F2117D3A22228B9E6EB291A11136081951B32024EEDCAB209C95EBE38032B3606; SL34syaT=8C5D983BCBE6B9EFC7610EFF8ADB68A1; accountId=MjIxMDYzNDUyNzMxMw==; cpcode=CP964950; isLogin=true; account=MTUzODgwOTExOTI=; lid=%E6%B0%B4%E7%BE%8A%E5%9B%BD%E9%99%85%3Aapollo03; unb=2210605210150; sn=%E6%B0%B4%E7%BE%8A%E5%9B%BD%E9%99%85%3Aapollo03; x-hng=lang=zh-CN; sgcookie=E1004ZAp6R59RjNApadWa%2Fjee4HoQmbkjcc2COReovXhZ1a0tuvm9pEEULS%2FcOOBxk7sLX%2FHev7%2FBv9s9%2B5DA3wvzvka4ijmixiQkfVpVzwZD3I%3D; uc1=cookie14=UoeyDb0AxueG9w%3D%3D&cookie21=WqG3DMC9Eman; csg=392a8a51; _m_h5_c=b96c5fbaa2be2210d8e37390b876b3e6_1663573925661%3B1d481bcee49fbab4413e9c2595240223; isg=BJ2dpwYiohRP70Y0wi8k5nTcrHmXutEM3wFra19nMvSrFrBIJwvH3V7AQAoQ1unE; l=eBT3VztPTxEcBeG3KO5a-urza77T5CdXCsPzaNbMiInca6IAahgZ-d5EXDLpudtjgt5vQetz5Tzfvde6--438xwbV48wnHJhSxp6Se1..; tfstk=cgEFB0Z9QMIFFJZWdcozb3E8tWBdaUy3Ehkj-shggBdcueDZgsVkwAAXXAkWQQ0h.'
    for key in store_list:
        items = save_data_pro(warehouse_name=key, cookie=cookie)
        print(items)
