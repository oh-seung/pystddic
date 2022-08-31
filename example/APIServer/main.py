import json

from flask import Flask
from flask_restx import Resource, Api, Namespace
from STDCLASS import *
import waitress



app = Flask(__name__)
api = Api(app, version='0.1.2', title='판매/고객영역 데이터 자산화 프로젝트')

StdPaser = STDPARSING()

###########################################################################
ns1 = Namespace('DataStandard')
Parser1 = ns1.parser()

@ns1.route('/Word')
@ns1.expect(Parser1)
class StandardWord(Resource):
    def get(self):
        ret_val = {"count":len(StdPaser.StdWordSet[0:100]), "result":StdPaser.StdWordSet[0:100]}
        return ret_val
    
@ns1.route('/Term')
@ns1.expect(Parser1)
class StandardWord(Resource):
    def get(self):
        ret_val = {"count":len(StdPaser.StdTermSet[0:100]), "result":StdPaser.StdTermSet[0:100]}
        return ret_val

    
@ns1.route('/Domain')
@ns1.expect(Parser1)
class StandardWord(Resource):
    def get(self):
        ret_val = {"count":len(StdPaser.StdTDomSet[0:100]), "result":StdPaser.StdTDomSet[0:100]}
        return ret_val
    
###########################################################################
ns2 = Namespace('Parser')
Parser2 = ns2.parser()
Parser2.add_argument('ParsingTargetTerm', type=str, required=True, help="분석대상용어")

@ns2.route('/')
@ns2.expect(Parser2)
class ParsingTargetTerm(Resource):
    def get(self):
        try:
            args = Parser2.parse_args()
            ParsingTargetTerm = args['ParsingTargetTerm']
            info = StdPaser.TermParsing(ParsingTargetTerm)
            ret_val = {"count":len([info]), "result":[info]}
        except:
            info = {'용어논리명':'InternalError', '용어물리명':'', '비표준단어목록':'', '분할결과확인대상':'', '속성분류어':'', '속성분류어사용여부':'', '동의어내역':'', '금칙어내역':'', '표준용어등록여부':'', '비율관련속성검증':''}
            ret_val = {"count":0, "result":[info]}
        finally:
            return ret_val
    
###########################################################################
ns3 = Namespace('TemporaryWord')
Parser3 = ns3.parser()
Parser3.add_argument('LogicalWord', type=str, required=True, help="논리명")
Parser3.add_argument('PhysicalShortWord', type=str, required=False, help="물리약어")
Parser3.add_argument('PhysicalFullWord', type=str, required=False, help="물리의미")
Parser3.add_argument('Hostname', type=str, required=True, help="호스트명")
Parser3.add_argument('WordType', type=str, required=True, help="단어유형")
Parser3.add_argument('SynonymTargetWord', type=str, required=False, help="동의어 대상 표준단어")
Parser3.add_argument('Description', type=str, required=False, help="단어 설명")
Parser3.add_argument('AttrClsYN', type=str, required=False, help="속성분류어여부")


Parser4 = ns3.parser()
Parser4.add_argument('LogicalWord', type=str, required=True, help="논리명")
Parser4.add_argument('Hostname', type=str, required=True, help="호스트명")

@ns3.route('/insert')
@ns3.expect(Parser3)
class TemporaryWordInsert(Resource):
    def post(self):
        args = Parser3.parse_args()
        Lgwd, phwd, full_phwd, hostname, WordType, SynonymWord, desc, attrclsyn = \
        args['LogicalWord'], args['PhysicalShortWord'], args['PhysicalFullWord'], args['Hostname'], args['WordType'], args['SynonymTargetWord'], args['Description'], args['AttrClsYN']
        info = StdPaser.TempWordInsert(Lgwd, phwd, full_phwd, hostname, WordType, desc, SynonymWord, attrclsyn)
        ret_val = {"count":len([info]), "result":[info]}
        return ret_val
    
@ns3.route('/delete')
@ns3.expect(Parser4)
class TemporaryWordDelete(Resource):
    def put(self):
        args = Parser4.parse_args()
        Lgwd, hostname = args['LogicalWord'], args['Hostname']
        info = StdPaser.TempWordDelete(Lgwd,  hostname)
        ret_val = {"count":len([info]), "result":[info]}
        return ret_val
    
@ns3.route('/confirm')
@ns3.expect(Parser4)
class TemporaryWordConfirm(Resource):
    def put(self):
        args = Parser4.parse_args()
        Lgwd, hostname = args['LogicalWord'], args['Hostname']
        info = StdPaser.TempWordConfirm(Lgwd,  hostname)
        ret_val = {"count":len([info]), "result":[info]}
        return ret_val    
    
    
###########################################################################
ns5 = Namespace('TemporaryDomain')
Parser5 = ns5.parser()
Parser5.add_argument('DomainName', type=str, required=True, help="도메인명")
Parser5.add_argument('DataType', type=str, required=True, help="데이터타입(VARCHAR2만 이용)")
Parser5.add_argument('Length', type=int, required=True, help="데이터길이")
Parser5.add_argument('DomainUsageScaleType', type=str, required=True, help="도메인사용범위코드(로컬,전역)")
Parser5.add_argument('UsageSystemNo', type=str, required=False, help="사용시스템번호(서버번호)")
Parser5.add_argument('Hostname', type=str, required=True, help="호스트명")

Parser5_2 = ns5.parser()
Parser5_2.add_argument('DomainName', type=str, required=True, help="도메인명")
Parser5_2.add_argument('Hostname', type=str, required=True, help="호스트명")

@ns5.route('/insert')
@ns5.expect(Parser5)
class TemporaryDomainInsert(Resource):
    def post(self):
        args = Parser5.parse_args()      
        info = StdPaser.TempDomainInsert(args['DomainName'], args['DataType'], args['Length'], args['DomainUsageScaleType'], args['UsageSystemNo'], args['Hostname'])
        
        ret_val = {"count":len([info]), "result":[info]}
        return ret_val
    
@ns5.route('/delete')
@ns5.expect(Parser5_2)
class TemporaryDomainDelete(Resource):
    def post(self):
        args = Parser5_2.parse_args()      
        info = StdPaser.TempDomainDelete(args['DomainName'], args['Hostname'])
        ret_val = {"count":len([info]), "result":[info]}
        return ret_val    

    
api.add_namespace(ns1)
api.add_namespace(ns2)
api.add_namespace(ns3)
api.add_namespace(ns5)

APIServer = waitress.serve

