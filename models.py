from django.db import models

# Create your models here.
#!/usr/bin/env python3
# coding: utf-8
# File: question_classifier.py
# Author: lhy<lhy_in_blcu@126.com,https://huangyong.github.io>
# Date: 18-10-4
import os
import ahocorasick
from py2neo import Graph

class QuestionClassifier:
    def __init__(self):
        cur_dir = '/'.join(os.path.abspath(__file__).split('/')[:-1])
        #　特征词路径
        self.bandwidth_path = os.path.join(cur_dir, 'D:/工程/111/static/data/bandwidth.txt')    # 实体类别
        self.equipment_path = os.path.join(cur_dir, 'D:/工程/111/static/data/equipment.txt')
        self.frequency_path = os.path.join(cur_dir, 'D:/工程/111/static/data/frequency.txt')
        self.launch_path = os.path.join(cur_dir, 'D:/工程/111/static/data/launch.txt')
        self.limiting_path = os.path.join(cur_dir, 'D:/工程/111/static/data/limiting.txt')
        self.manufacturer_path = os.path.join(cur_dir, 'D:/工程/111/static/data/manufacturer.txt')
        # 加载特征词
        self.bandwidth_wds= [i.strip() for i in open(self.bandwidth_path, 'r', encoding='utf-8') if i.strip()]   # 将每一个文本分成列表结构
        self.equipment_wds= [i.strip() for i in open(self.equipment_path, 'r', encoding='utf-8') if i.strip()]
        self.frequency_wds= [i.strip() for i in open(self.frequency_path, 'r', encoding='utf-8') if i.strip()]
        self.launch_wds= [i.strip() for i in open(self.launch_path, 'r', encoding='utf-8') if i.strip()]
        self.limiting_wds= [i.strip() for i in open(self.limiting_path, 'r', encoding='utf-8') if i.strip()]
        self.manufacturer_wds= [i.strip() for i in open(self.manufacturer_path, 'r', encoding='utf-8') if i.strip()]
             # set() 函数创建一个无序不重复元素集
        self.region_words = set(self.bandwidth_wds + self.equipment_wds + self.frequency_wds + self.launch_wds + self.limiting_wds + self.manufacturer_wds)
        # 构造领域actree
        self.region_tree = self.build_actree(list(self.region_words))
        # 构建词典
        self.wdtype_dict = self.build_wdtype_dict()
        # 问句疑问词
        self.zasan_qwds = ['杂散发射限值', '发射限值']
        self.bandwidth_qwds = ['占用带宽', '带宽']

        print('model init finished ......')

        return

    '''分类主函数'''  # 将问题进行分类
    def classify(self, question):   # 若question为  乳腺癌的症状有哪些？
        data = {}
        medical_dict = self.check_medical(question)   # {'乳腺癌': ['disease']}
        if not medical_dict:
            return {}
        data['args'] = medical_dict    # data['args']    {'乳腺癌': ['disease']}
        #收集问句当中所涉及到的实体类型
        types = []
        for type_ in medical_dict.values():
            types += type_    # types    ['disease']
        question_type = 'others'

        question_types = []

        # 华为技术有限公司生产的无线电发射设备有哪些？
        if 'manufacturer' in types:
            question_type = 'manufacturer_shebei'
            question_types.append(question_type)

        # 发射功率为≤1W的无线电发射设备有哪些？
        if 'launch' in types:
            question_type = 'launch_shebei'
            question_types.append(question_type)

        # 占用带宽为≤35MHz的无线电设备有哪些？
        if self.check_words(self.bandwidth_qwds, question) and 'bandwidth' in types:
            question_type = 'bandwidth_shebei'
            question_types.append(question_type)

        # 调幅电台由哪些生产厂商生产？
        if 'equipment' in types:
            question_type = 'equipment_manu'
            question_types.append(question_type)

        # 杂散发射限值为≤-30dBm的无线电发射设备有哪些？
        if self.check_words(self.zasan_qwds, question) and 'limiting' in types:
            question_type = 'limiting_shebei'
            question_types.append(question_type)

        data['question_types'] = question_types

        return data     # 输出结果为  {'args': {'乳腺癌': ['disease']}, 'question_types': ['disease_symptom']}  一个字典结构

    '''构造词对应的类型'''
    def build_wdtype_dict(self):
        wd_dict = dict()   # 创建字典结构
        for wd in self.region_words:
            wd_dict[wd] = []   # '降脂通便胶囊': [],形式
            if wd in self.bandwidth_wds:
                wd_dict[wd].append('bandwidth')
            if wd in self.equipment_wds:
                wd_dict[wd].append('equipment')
            if wd in self.frequency_wds:
                wd_dict[wd].append('frequency')
            if wd in self.launch_wds:
                wd_dict[wd].append('launch')
            if wd in self.limiting_wds:
                wd_dict[wd].append('limiting')
            if wd in self.manufacturer_wds:
                wd_dict[wd].append('manufacturer')
        return wd_dict   # 将之前列表中的每一个实体赋予其实体类型，创建词典  {'降脂通便胶囊': ['drug'],宝庆丙戊酸钠片': ['producer'],'葱油莴笋饺': ['food'],'四肢远端麻木、...': ['symptom'],'清肺散结丸': ['drug'],

    '''构造actree，加速过滤'''
    def build_actree(self, wordlist):
        actree = ahocorasick.Automaton()
        for index, word in enumerate(wordlist):
            actree.add_word(word, (index, word))
        actree.make_automaton()
        return actree    # <ahocorasick.Automaton at 0x25bb1716570>形式

    '''问句过滤'''   # 将句子中上面对应的实体提取出来， 将问句提取成所属类别，is disease or others

    def check_medical(self, question):   #  question: 乳腺癌的症状有哪些？
        region_wds = []
        for i in self.region_tree.iter(question):   # iter() 函数用来生成迭代器
            wd = i[1][1]   # i的形式为(2, (14401, '乳腺癌')) (2, (1251, '腺癌'))   i[1][1]为 乳腺癌  腺癌
            region_wds.append(wd)    # ['乳腺癌', '腺癌']
        stop_wds = []
        for wd1 in region_wds:
            for wd2 in region_wds:
                if wd1 in wd2 and wd1 != wd2:   # 当wd1:腺癌,wd2:乳腺癌
                    stop_wds.append(wd1)      # ['腺癌']
        final_wds = [i for i in region_wds if i not in stop_wds]   # ['乳腺癌']
        final_dict = {i:self.wdtype_dict.get(i) for i in final_wds}   # {'乳腺癌': ['disease']}

        return final_dict   # {'乳腺癌': ['disease']}    字典结构

    '''基于特征词进行分类'''    # 若某个问句疑问词列表里的某个名词在question字符串中出现，返回true,继续执行，否则返回false
    def check_words(self, wds, sent):   # wds :self.symptom_qwds
        for wd in wds:
            if wd in sent:           # sent: question
                return True
        return False

class QuestionPaser:

    '''构建实体节点'''
    def build_entitydict(self, args):   # args:   {'乳腺癌': ['disease']}
        entity_dict = {}   # 字典结构
        for arg, types in args.items():   # items函数可以历遍出dict内的key和value，并以一对为元组的形式，组成一个list   arg :'乳腺癌'   types :  ['disease']
            for type in types:
                if type not in entity_dict:
                    entity_dict[type] = [arg]
                else:
                    entity_dict[type].append(arg)

        return entity_dict   # {'disease': ['乳腺癌']}

    '''解析主函数'''
    def parser_main(self, res_classify):   # res_classify:   {'args': {'乳腺癌': ['disease']}, 'question_types': ['disease_symptom']}
        args = res_classify['args']   # args:   {'乳腺癌': ['disease']}
        entity_dict = self.build_entitydict(args)   # {'disease': ['乳腺癌']}
        question_types = res_classify['question_types']   # ['disease_symptom']
        sqls = []
        for question_type in question_types:
            sql_ = {}
            sql_['question_type'] = question_type
            sql = []
            if question_type == 'manufacturer_shebei':
                sql = self.sql_transfer(question_type, entity_dict.get('manufacturer'))

            elif question_type == 'launch_shebei':
                sql = self.sql_transfer(question_type, entity_dict.get('launch'))

            elif question_type == 'bandwidth_shebei':
                sql = self.sql_transfer(question_type, entity_dict.get('bandwidth'))

            elif question_type == 'equipment_manu':
                sql = self.sql_transfer(question_type, entity_dict.get('equipment'))

            elif question_type == 'limiting_shebei':
                sql = self.sql_transfer(question_type, entity_dict.get('limiting'))

            if sql:
                sql_['sql'] = sql
                                    # sql_ {'question_type': 'disease_symptom', 'sql': ["MATCH (m:Disease)-[r:has_symptom]->(n:Symptom) where m.name = '乳腺癌' return m.name, r.name, n.name"]}
                sqls.append(sql_)   # sql_ 字典结构

        return sqls   # [{'question_type': 'disease_symptom', 'sql': ["MATCH (m:Disease)-[r:has_symptom]->(n:Symptom) where m.name = '乳腺癌' return m.name, r.name, n.name"]}]

    '''针对不同的问题，分开进行处理'''
    def sql_transfer(self, question_type, entities):   # 生成cypher语句
        if not entities:
            return []

        # 查询语句
        sql = []
        # 华为技术有限公司生产的无线电发射设备有哪些？
        if question_type == 'manufacturer_shebei':
            sql = ["match (n:`生产厂商`)<-[:`厂商生产`]-(m) where n.名称 = '{0}' return m.名称, n.名称".format(i) for i in entities]

        # 发射功率为≤1W的无线电发射设备有哪些？
        elif question_type == 'launch_shebei':
            sql = ["match (n:`发射功率`)<-[r]-(m:`无线电设备`) where n.功率 = '{0}' return m.名称, n.功率".format(i) for i in entities]

        # 占用带宽为≤35MHz的无线电设备有哪些？
        elif question_type == 'bandwidth_shebei':
            sql = ["match (n:`占用带宽`)<-[r]-(m:`无线电设备`) where n.带宽 = '{0}' return m.名称, n.带宽".format(i) for i in entities]

        # 调幅电台由哪些生产厂商生产？
        elif question_type == 'equipment_manu':
            sql = ["match (n:`无线电设备`)-[r]->(m:`生产厂商`) where n.名称 = '{0}' return m.名称, n.名称".format(i) for i in entities]

        # 杂散发射限值为≤-30dBm的无线电发射设备有哪些？
        elif question_type == 'limiting_shebei':
            sql = ["match (n:`杂散发射限值`)<-[r]-(m) where n.限值 = '{0}' return m.名称, n.限值".format(i) for i in entities]

        return sql

class AnswerSearcher:
    def __init__(self):
        self.g = Graph(
            host="localhost",   # 本地ip地址
            http_port=7474,
            user="neo4j",
            password="1")
        self.num_limit = 15

    '''执行cypher查询，并返回相应结果'''
    def search_main(self, sqls):    #  sqls 为  [{'question_type': 'disease_symptom', 'sql': ["MATCH (m:Disease)-[r:has_symptom]->(n:Symptom) where m.name = '乳腺癌' return m.name, r.name, n.name"]}]
        final_answers = []  # 用来装问句最后的问答结果
        for sql_ in sqls:
            question_type = sql_['question_type']   # question_type： 'disease_symptom'，
            queries = sql_['sql']  # queries：["MATCH (m:Disease)-[r:has_symptom]->(n:Symptom) where m.name = '乳腺癌' return m.name, r.name, n.name"]}]
            answers = []
            for query in queries:   # query即为对应问句的cypher语句
                ress = self.g.run(query).data()  # ress为：[{'m.name': '乳腺癌', 'r.name': '症状', 'n.name': '肝肿大'}, {'m.name': '乳腺癌', 'r.name': '症状', 'n.name': '胸痛'}, {'m.name': '乳腺癌', 'r.name': '症状', 'n.name': '乳房肿块'}, {'m.name': '乳腺癌', 'r.name': '症状', 'n.name': '剧痛'}, {'m.name': '乳腺癌', 'r.name': '症状', 'n.name': '乳头内陷'}, {'m.name': '乳腺癌', 'r.name': '症状', 'n.name': '泌乳障碍'}, {'m.name': '乳腺癌', 'r.name': '症状', 'n.name': '乳腺癌的远处转移'}, {'m.name': '乳腺癌', 'r.name': '症状', 'n.name': '乳头溢液'}, {'m.name': '乳腺癌', 'r.name': '症状', 'n.name': '乳头破碎'}]
                answers += ress    # [{'m.name': '乳腺癌', 'r.name': '症状', 'n.name': '肝肿大'}, {'m.name': '乳腺癌', 'r.name': '症状', 'n.name': '胸痛'}, {'m.name': '乳腺癌', 'r.name': '症状', 'n.name': '乳房肿块'}, {'m.name': '乳腺癌', 'r.name': '症状', 'n.name': '剧痛'}, {'m.name': '乳腺癌', 'r.name': '症状', 'n.name': '乳头内陷'}, {'m.name': '乳腺癌', 'r.name': '症状', 'n.name': '泌乳障碍'}, {'m.name': '乳腺癌', 'r.name': '症状', 'n.name': '乳腺癌的远处转移'}, {'m.name': '乳腺癌', 'r.name': '症状', 'n.name': '乳头溢液'}, {'m.name': '乳腺癌', 'r.name': '症状', 'n.name': '乳头破碎'}]
            final_answer = self.answer_prettify(question_type, answers)   # 调对应问题类型回答的模板
            if final_answer:
                final_answers.append(final_answer)    # ['乳腺癌的症状包括：胸痛;剧痛;乳头内陷;泌乳障碍;乳头溢液;乳头破碎;肝肿大;乳腺癌的远处转移;乳房肿块']
        return final_answers

    '''根据对应的qustion_type，调用相应的回复模板'''
    def answer_prettify(self, question_type, answers):
        final_answer = []
        if not answers:
            return ''
        if question_type == 'manufacturer_shebei':
            desc = list(set([i['m.名称'] for i in answers]))   # desc为n(症状)的实体名称    症状实体名称的一个列表
            subject = answers[0]['n.名称']   # answers为上述的一个列表，subject为去列表中第一个字典的[m.name]的实体名称，即疾病名称
            final_answer ='{0}的无线电发射设备有：{1}'.format(subject, '；'.join(desc[:self.num_limit])) # desc为该疾病对应的症状的名称的列表，set创建一个无需不重复元素集，list(set(desc))为一个列表，';'.join病症之间以‘；’分开，[:self.num_limit]限制输出前num_limit个病症名称，即20个

        elif question_type == 'launch_shebei':
            desc = list(set([i['m.名称'] for i in answers]))
            subject = answers[0]['n.功率']
            final_answer = '发射功率为{0}的无线电发射设备有：{1}'.format(subject, '；'.join(desc[:self.num_limit]))

        elif question_type == 'bandwidth_shebei':
            desc = list(set([i['m.名称'] for i in answers]))
            subject = answers[0]['n.带宽']
            final_answer = '占用带宽为{0}的无线电发射设备有：{1}'.format(subject, '；'.join(desc[:self.num_limit]))

        elif question_type == 'equipment_manu':
            desc = list(set([i['m.名称'] for i in answers]))
            subject = answers[0]['n.名称']
            final_answer = '{0}的生产厂商有：{1}'.format(subject, '；'.join(desc[:self.num_limit]))

        elif question_type == 'limiting_shebei':
            desc = list(set([i['m.名称'] for i in answers]))
            subject = answers[0]['n.限值']
            final_answer = '杂散发射限值为{0}的无线电发射设备有：{1}'.format(subject, '；'.join(desc[:self.num_limit]))

        return final_answer   # 返回结果一个字符串文字


