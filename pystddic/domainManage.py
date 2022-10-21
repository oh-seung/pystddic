import pandas as pd
from string import capwords
from copy import copy
import ray
from tqdm.notebook import tqdm



class domainGroupManage:
    """ 도메인 그룹 관리 """
    def __init__(self):
        self.domainGroupColumns = ['domainGroupName', 'domainGroupDescription', 'domainGroupUniqueness', 'domainAttributeClassWord']
        self.domainGroupKoreanMapping = {'domainGroupName':'도메인그룹명', 
                                         'domainGroupDescription':'도메인그룹설명',
                                         'domainGroupUniquenessRule':'도메인그룹유일성규칙',
                                         'domainAttributeClassWord':'도메인그룹사용속성분류어',
                                         }
        self.domainGroupUniquessList = ['제한', '번호']

    def _domainGroupStorageEmpty(self):
        """ 도메인그룹 저장 DataFrame 생성(비우기) """
        self.domainGroupStorage = pd.DataFrame(None, columns=self.domainGroupColumns)

    def domainGroupInsert(self, domainGroupName:str, domainGroupDescription:str, domainGroupUniqueness:str, domainAttributeClassWord:list, **kwargs):
        tempDomainGroupSet = {'domainGroupName':domainGroupName, 'domainGroupDescription':domainGroupDescription, 'domainGroupUniqueness':domainGroupUniqueness, 'domainAttributeClassWord':domainAttributeClassWord}
        ### 체크결과에 오류(True)가 있을때는 오류를 발생시키고, 오류가 없을 경우 데이터 프레임에 입력
        CheckResult = self._domainGroupValidationCheck(tempDomainGroupSet)
        if True in CheckResult.values():
            errorMessage = ""
            for key, values in CheckResult.items():
                if values == True:
                    errorMessage += key + ', '
            assert False, 'An error occurred in the domain group registration. \n domainGroupName:{0}, ErrorMessage:{1}'.format(tempDomainGroupSet['domainGroupName'], errorMessage[:-2])
        else:
            self.domainGroupStorage = self.domainGroupStorage.append(tempDomainGroupSet, ignore_index=True)
        
        
    def _domainGroupModification(self, domainGroupSet:dict):
        """ 등록하고자 하는 도메인그룹을 규칙에 맞게 조정"""
        pass
    
    def _domainGroupValidationCheck(self, domainGroupSet:dict):
        """ 도메인이 맞는지 검증 """
        checkResult = dict()
        
        checkResult['도메인그룹명 중복'] = domainGroupSet['domainGroupName'] in self.domainGroupStorage['domainGroupName'].values
        checkResult['도메인그룹 설명 미작성'] = len(domainGroupSet['domainGroupDescription'].strip()) == 0
        checkResult['도메인그룹 유일성 기준값 없음(제한 또는 번호 사용)'] = domainGroupSet['domainGroupUniqueness'] not in self.domainGroupUniquessList
        checkResult['도메인그룹 사용 속성분류어 미작성'] = len(domainGroupSet['domainAttributeClassWord']) == 0
       
        return checkResult

    def domainGroupUpdate(self, **kwargs):
        """ """
        pass

    def domainGroupDelete(self, **kwargs):
        """ """
        pass

class domainManage(domainGroupManage):
    def __init__(self):
        super().__init__()
        self.domainColumns = ['domainName', 'domainDescription', 'domainDataType', 'domainLength', 'domainScale', 'domainGroupName', 'minValue', 'maxValue', 'validValue', 'default']
        self.domainKoreanMapping = {}

        self.domainDataTypes = ['varchar', 'char', 'int', 'float', 'clob', 'blob', 'nvarchar', 'nchar', 'date', 'datetime', 'timestamp', 'datestr']
        self.stringDataTypes = ['varchar', 'char', 'nvarchar', 'nchar', 'datestr']

        self._domainGroupStorageEmpty()
        self._domainStorageEmpty()

    def _domainStorageEmpty(self):
        """ 도메인 저장 DataFrame 생성(비우기) """
        self.domainStorage = pd.DataFrame(None, columns=self.domainColumns)        

    def domainInsert(self, domainName:str, domainDescription:str, domainDataType:str, domainGroupName:str, **kwargs):
        """ 도메인 등록 """

        tempDomainSet = {'domainName':domainName,
            'domainDescription':domainDescription,
            'domainDataType':domainDataType,
            'domainLength':None,
            'domainScale':None,
            'domainGroupName':domainGroupName,
            'minValue':None,
            'maxValue':None,
            'validValue':None,
            'default':None,
        }
        
        tempDomainSet['domainLength'] = kwargs['domainLength'] if 'domainLength' in kwargs.keys() else ''
        tempDomainSet['domainScale'] = kwargs['domainScale'] if 'domainScale' in kwargs.keys() else ''
        tempDomainSet['minValue'] = kwargs['minValue'] if 'minValue' in kwargs.keys() else ''
        tempDomainSet['maxValue'] = kwargs['maxValue'] if 'maxValue' in kwargs.keys() else ''
        tempDomainSet['validValue'] = kwargs['validValue'] if 'validValue' in kwargs.keys() else ''
        tempDomainSet['default'] = kwargs['default'] if 'default' in kwargs.keys() else ''

        checkResult = self._domainValidationCheck(tempDomainSet)
        if True in checkResult.values():
            errorMessage = ""
            for key, values in checkResult.items():
                if values == True:
                    errorMessage += key + ', '
            assert False, 'An error occurred in the domain registration. \n domainGroupName:{0}, ErrorMessage:{1}'.format(tempDomainSet['domainName'], errorMessage[:-2])
        else:
            self.domainStorage = self.domainStorage.append(tempDomainSet, ignore_index=True)

    
    def domainUpdate(self, domainSet:dict, **kwargs):
        """ 도메인 변경 """
        pass    
        
    def _domainModification(self, domainSet:dict):
        """ 등록하고자 하는 도메인을 규칙에 맞게 조정"""
        pass
    
    def _domainValidationCheck(self, domainSet:dict):
        """ 도메인이 맞는지 검증 """
        checkResult = {}
        domainGroupStorage = self.domainGroupStorage
        domainStorage = self.domainStorage

        ### 1) 실수형 검증
        ### 1-1) 데이터길이 보다 소수점이 작어야 한다.
        ### 1-3) 소수점을 반드시 지정해야 한다.
        if domainSet['domainDataType'] == 'float':
            if type(domainSet['domainScale']).__name__ == 'int':
                checkResult['소수점길이, 데이터길이 초과'] = domainSet['domainLength'] > 0 and domainSet['domainScale'] > 0 and domainSet['domainScale'] >= domainSet['domainLength']
            else:
                checkResult['소수점형식(float) 사용시 소수점 길이 지정 필요'] = True

        ### ?) 정수형과 문자형에 대한 소수점 검증
        if domainSet['domainDataType'] == 'int' or domainSet['domainDataType'] in self.stringDataTypes:
            checkResult['소수점 존재(Scale 삭제 필요)'] = type(domainSet['domainScale']).__name__ == 'int'

        ### 2) 데이터타입은 domainDataTypes 에 존재해야 함
        checkResult['미지정데이터타입'] = domainSet['domainDataType'] not in self.domainDataTypes

        ### 3) 문자형을 사용할 경우, 길이를 필수로 지정해야 함(max 사용가능)
        if domainSet['domainDataType'] in self.stringDataTypes:
            if type(domainSet['domainLength']).__name__ == 'str':
                checkResult['길이 지정 필요'] = domainSet['domainLength'] != 'MAX'
            elif type(domainSet['domainLength']).__name__ == 'int':
                checkResult['길이 지정 필요'] = domainSet['domainLength'] < 1

        ### 4) 도메인그룹 존재여부 확인
        checkResult['도메인 그룹 미존재'] = domainSet['domainGroupName'] not in domainGroupStorage['domainGroupName'].values

        ### 5) 속성 분류어 확인
        ### 5-1) 도메인그룹이 '제한'일 경우, 분류어 '='(Equal)로 검증
        ### 5-2) 도메인그룹이 '번호'일 경우, 분류어 endwith 로 검증
        ### 5-3) 도메인그룹이 '번호'일 경우, 분류어와 동일하게 도메인명 생성 불가 검증
        attributeClassWords = domainGroupStorage[domainGroupStorage['domainGroupName'] == domainSet['domainGroupName']].domainAttributeClassWord.values[0]
        domainGroupUniqueness = domainGroupStorage[domainGroupStorage['domainGroupName'] == domainSet['domainGroupName']].domainGroupUniqueness.values[0]
        if domainGroupUniqueness == '제한':
            checkResult['속성분류어 범위 미준수'] = domainSet['domainName'] not in attributeClassWords
        elif domainGroupUniqueness == '번호':
            checkResult['속성분류어 범위 미준수'] = True
            checkResult['번호도메인그룹은 분류어와 동일한 명칭으로 도메인 생성 불가'] = False
            for attributeClassWord in attributeClassWords:
                checkResult['속성분류어 범위 미준수'] = False if domainSet['domainName'].endswith(attributeClassWord) else checkResult['속성분류어 범위 미준수']
                checkResult['번호도메인그룹은 분류어와 동일한 명칭으로 도메인 생성 불가'] = True if domainSet['domainName'] == attributeClassWord else checkResult['번호도메인그룹은 분류어와 동일한 명칭으로 도메인 생성 불가']

        ### ?) 도메인 유일성 검증
        ### ?-1) 제한도메인의 경우, 도메인명 + 데이터타입 + 데이터길이 + 소수점으로 유일해야 한다.
        ### ?-2) 번호도메인의 경우, 도메인명으로 유일해야 한다.
        if domainGroupUniqueness == '제한':
            existdomainkeys = domainStorage['domainName'] + domainStorage['domainDataType'] + domainStorage['domainLength'].astype('str') + ',' + domainStorage['domainScale'].astype('str')
            newdomainkey = domainSet['domainName'] + domainSet['domainDataType'] + str(domainSet['domainLength']) + ',' + str(domainSet['domainScale'])
            checkResult['도메인 중복(제한)'] = newdomainkey in existdomainkeys.values
        elif domainGroupUniqueness == '번호':
            checkResult['도메인 중복(번호)'] = domainSet['domainName'] in domainStorage['domainName'].values

        ### 6) 길이지정 불가유형에 대해 검증
        if domainSet['domainDataType'] in ['clob', 'blob', 'date', 'datetime']:
            checkResult['데이터 길이 지정 불가'] = type(domainSet['domainLength']).__name__ == 'int'
            if type(domainSet['domainLength']).__name__ == 'str':
                checkResult['데이터 길이 사용 불가'] = domainSet['domainLength'] != ''

            checkResult['소수점 지정 불가'] = type(domainSet['domainScale']).__name__ == 'int'
            if type(domainSet['domainScale']).__name__ == 'str':
                checkResult['소수점 길이 사용 불가'] = domainSet['domainScale'] != ''                

        return checkResult
