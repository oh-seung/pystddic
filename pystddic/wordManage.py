import pandas as pd
from string import capwords
import sys
from tqdm.notebook import tqdm

class wordManage:
    """ 표준단어 관리 클래스 """
    def __init__(self):
        self.englishColumns = ['LogicalWord', 'PhysicalWord', 'LogicalDescription', 'PhysicalDescription', \
                               'EntityClassWord', 'AttributeClassWord', 'wordStandardType', 'synonymousWord']
        self.koreanColumnMapping = {'LogicalWord':'논리명', 'PhysicalWord':'물리명', 'LogicalDescription':'단어설명', 'PhysicalDescription':'물리전체명칭',\
                                    'EntityClassWord':'엔터티분류어여부', 'AttributeClassWord':'속성분류어여부', 'wordStandardType':'단어유형코드', 'synonymousWord':'동의어'}

        self._wordStorageEmpty()
        
        self.wordVefiryList = {'논리명중복제한':True,
                                '논리명미존재':True,
                                '물리명미존재':True,
                                '물리전체명칭미존재':True,
                                '물리명중복제한':True,
                                '물리명길이제한':True,
                                '특수문자사용제한':True,
                                '물리명대문자변환':True,
                                '물리전체명칭첫글자대문자변환':True,
                                '물리명최대길이수':10,
                                '사용제한특수문자':"(,),%,@,!,~,$,^,&,*,<,>,;,/,?,-,_,=,+,.',\",[,]",
                              }
                
        #self.physicalWordUpperCase = True ### 물리명는 대문자로만 사용
        #self.physicalDescriptionCapWord = True ### 물리전체명칭은 첫글자와 공백 기준 첫글자는 대문자로
        self.PhysicalWordLengthLimit = 10
        self.nonUseSpecialword = "(,),%,@,!,~,$,^,&,*,<,;,/,?,-,_,=,+" ### 
        self.dictionarySync = False
        
    def _wordStorageEmpty(self):
        """ 단어저장소를 생성 또는 비우는 메소드 """
        self.wordStorage = pd.DataFrame(None, columns=self.englishColumns)


    def multiWordInsert(self, records, **kwargs):        
        records = tqdm(records) if kwargs['progress'] else records if 'progress' in kwargs.keys() else records
        

        error_words = []

        #### 멀티 Insert시 replace 요청일 경우 기존 단어를 삭제하고 새로 입력한다.
        #### DB와 실시간 연동시 필요하다, MultiCurrenty 환경을 너무 고민하지 말자. 그건 DB 버전으로 할 경우에 사용
        #### multiInsert에 대해 type? 을 정의하여 replace(전체변경), merge(데이터병합) 의 유형으로 생성함
        #### replace : 데이터를 전체 삭제하고 새로 반영
        
        allReplace = True if kwargs['replace'] else False if 'replace' in kwargs.keys() else False        
        if allReplace:
            self._wordStorageEmpty()

        ### 행별 데이터 처리
        for row in records:
            synonymousWord = row['synonymousWord'] if 'synonymousWord' in row.keys() else ""
            try:
                self.wordInsert(LogicalWord=row['LogicalWord'], PhysicalWord=row['PhysicalWord'], \
                                LogicalDescription=row['LogicalDescription'], PhysicalDescription=row['PhysicalDescription'], \
                                EntityClassWord=row['EntityClassWord'], AttributeClassWord=row['AttributeClassWord'], \
                                wordStandardType=row['wordStandardType'], synonymousWord=synonymousWord, allReplace=allReplace)
            except:
                _, message, _ = sys.exc_info()
                error_words.append([message, row])

        return None if len(error_words) == 0 else error_words
                
            
    def wordInsert(self, LogicalWord:str, PhysicalWord:str, LogicalDescription:str, PhysicalDescription:str, \
                   EntityClassWord:bool, AttributeClassWord:bool, wordStandardType:str, **kwargs):
        """ 표준단어를 추가함 
             - LogicalWord : 논리단어
             - PhysicalWord : 물리명 용어사용시 해당 단어를 조합
             - LogicalDescription : 논리단어에 대한 설명
             - PhysicalDescription : 약어가 아닌 영문 전체 명칭을 정의
             - EntityClassWord : 엔터티 분류어 여부
             - AttributeClassWord : 속성 분류어 여부
             - wordStandardType : 표준단어, 동의어, 금칙어를 지정함
             - synonymousWord : 동의어 단어에 지정된 단어를 매핑
        """

        ### 동의어가 있다면 동의어 기록, 없으면 None
        synonymousWord = kwargs['synonymousWord'] if 'synonymousWord' in kwargs.keys() else ""
        ### 단어 셋을 지정
        tempWordSet = {'LogicalWord':LogicalWord, 'PhysicalWord':PhysicalWord, 'LogicalDescription':LogicalDescription, \
         'PhysicalDescription':PhysicalDescription, 'EntityClassWord':EntityClassWord, 'AttributeClassWord':AttributeClassWord, \
         'wordStandardType':wordStandardType, 'synonymousWord':synonymousWord}
        
        ### 표준단어 입력에 대한 기초적인 정제
        tempWordSet = self._wordModification(tempWordSet)
        
        ### 동의어일 경우, 해당 표준단어에 맞게 조정함
        if tempWordSet['wordStandardType'] == '동의어':
            tempWordSet, _ = self._synonymusWordModification(tempWordSet)
        
        ### 체크결과에 오류(True)가 있을때는 오류를 발생시키고, 오류가 없을 경우 데이터 프레임에 입력
        CheckResult = self._wordValidationCheck(tempWordSet)
        if True in CheckResult.values():
            errorMessage = ""
            for key, values in CheckResult.items():
                if values == True:
                    errorMessage += key + ', '
            assert False, 'An error occurred in the word registration. \n LogicalWord:{0}, ErrorMessage:{1}'.format(tempWordSet['LogicalWord'], errorMessage[:-2])
        else:
            self.wordStorage = self.wordStorage.append(tempWordSet, ignore_index=True)

        self.dictionarySync = False

    def wordUpdate(self, newWordSet:dict, **kwargs):
        """ 단어를 수정, 논리명 기준으로 찾아서 변경 """
        try:
            idx = self.wordStorage[self.wordStorage['LogicalWord'] == newWordSet['LogicalWord']].index[0]
            tempWordSet = self.wordStorage.loc[idx].to_dict()
            for k, v in newWordSet.items():
                tempWordSet[k] = v        

            ### 표준단어 입력에 대한 기초적인 정제
            tempWordSet = self._wordModification(tempWordSet)

            ### 동의어일 경우, 해당 표준단어에 맞게 조정함
            if tempWordSet['wordStandardType'] == '동의어':
                tempWordSet, _ = self._synonymusWordModification(tempWordSet)

            ### 체크결과에 오류(True)가 있을때는 오류를 발생시키고, 오류가 없을 경우 데이터 프레임에 입력
            CheckResult = self._wordValidationCheck(tempWordSet, dmlType='UPDATE', newWordSet=newWordSet)
            if True in CheckResult.values():
                errorMessage = ""
                for key, values in CheckResult.items():
                    if values == True:
                        errorMessage += key + ', '
                assert False, 'An error occurred in the word registration. \n LogicalWord:{0}, ErrorMessage:{1}'.format(tempWordSet['LogicalWord'], errorMessage[:-2])
            else:
                print('word change complete.')
                print(tempWordSet)
                self.wordStorage.loc[idx] = tempWordSet
        except IndexError as e:
            assert False, 'There is no word with matching logical name, {0}'.format(e)
            
        except:
            _, message, _ = sys.exc_info()
            assert False, 'undefined error, {0}'.format(message)
        
    def wordDelete(self, condition:dict, **kwargs):
        """ 조건에 맞는 단어를 삭제 """
        tempWordStorage = self.wordStorage
        for k, v in condition.items():
            tempWordStorage = tempWordStorage[tempWordStorage[k] == v]
        self.wordStorage = self.wordStorage.drop(tempWordStorage.index)
        self.wordStorage.reset_index(drop=True, inplace=True)
        
        print('deleted word:', ", ".join(tempWordStorage['LogicalWord'].tolist()))
        
    def wordVefiryRuleChange(self, **kwargs):
        """ 단어 검증룰을 변경함
        """
        for key in kwargs.keys():
            if key in self.wordVefiryList.keys():
                self.wordVefiryList[key] = kwargs[key]
                print(key, ':', self.wordVefiryList[key], '으로 변경')

            
    def wordQuery(self, **kwargs):
        """ 저장된 표준단어를 요청하는 언어(Language)에 따라 컬럼명을 변경하여 호출함"""
        try:
            if kwargs['language'] == 'Korean':
                return self.wordStorage.rename(columns=self.koreanColumnMapping)
        except:
            return  self.wordStorage
        
        return  self.wordStorage

    def _wordValidationCheck(self, tempWordSet:dict, dmlType:str='INSERT', **kwargs):
        """ 표준단어 추가에 대한 정합성 체크"""
        CheckResult = {}
        if [type(val).__name__ for val in tempWordSet.values()] == ['str', 'str', 'str', 'str', 'bool', 'bool', 'str', 'str']:
            ### 데이터형식 체크 결과
            CheckResult['데이터형식불일치'] = False
            ### 논리명 중복 체크
            LogicalWordCheck = self.wordStorage['LogicalWord'] == tempWordSet['LogicalWord']
            LogicalWordCheck = list(LogicalWordCheck)
            if self.wordVefiryList['논리명중복제한']:
                CheckResult['논리명중복발생'] = True if True in LogicalWordCheck else False

            ### 단어에 특수문자 존재
            specialwords = set(self.wordVefiryList['사용제한특수문자'].split(",")) & set(list(tempWordSet['LogicalWord']))
            CheckResult['특수문자존재'] = True if len(specialwords) > 0 else False

            ### 논리명, 물리명, 물리전체명칭 길이가 0 이상일 경우 
            CheckResult['논리명미존재'] = True if len(tempWordSet['LogicalWord']) == 0 else False
            CheckResult['물리명미존재'] = True if len(tempWordSet['PhysicalWord']) == 0 else False
            CheckResult['물리전체명칭미존재'] = True if len(tempWordSet['PhysicalDescription']) == 0 else False
            
            ### 표준단어에만 해당되는 검증
            if tempWordSet['wordStandardType'] == '표준단어':
                
                PhysicalWordCheck = self.wordStorage['PhysicalWord'] == tempWordSet['PhysicalWord']
                PhysicalWordCheck = list(PhysicalWordCheck)
                ### 물리명 중복 체크
                if self.wordVefiryList['물리명중복제한']:
                    CheckResult['물리명중복발생'] = True if True in PhysicalWordCheck else False        
                ### 물리명 길이 체크
                if self.wordVefiryList['물리명길이제한']:
                    CheckResult['물리명길이제한초과'] = True if len(tempWordSet['PhysicalWord']) > self.wordVefiryList['물리명최대길이수'] else False
                ### 엔터티분류어, 속성분류어에 Bool값으로 여부 확인
            
            ### 동의어에만 해당하는 체크
            elif tempWordSet['wordStandardType'] == '동의어':
                ### 표준단어 칸이 채워져 있는지 확인
                CheckResult['표준단어공란'] = True if tempWordSet['synonymousWord'] == "" else False
                ### 표준단어가 존재하는지를 확인
                _, stadardWordExist = self._synonymusWordModification(tempWordSet)
                CheckResult['표준단어미존재'] = True if stadardWordExist == False else False
        else:
            CheckResult['데이터형식불일치'] = True
            
        try:
            if dmlType == 'UPDATE':
                # (1) 논리명 중복을 제거함,
                del CheckResult['논리명중복발생']
                # (2) 물리명 중복의 경우, 단어 신청 내용이 없으면 검증하지 않아도 됨
                newWordSet = kwargs['newWordSet']
                if 'PhysicalWord' not in newWordSet.keys():
                    del CheckResult['물리명중복발생']

        except:
            pass

        return CheckResult
    
    def _wordModification(self, tempWordSet):
        """ 입력된 단어에 대한 정비"""
        if [type(val).__name__ for val in tempWordSet.values()] == ['str', 'str', 'str', 'str', 'bool', 'bool', 'str', 'str']:
            ### 1) 물리명에 대한 대문자 변환
            tempWordSet['PhysicalWord'] = tempWordSet['PhysicalWord'].upper() if self.wordVefiryList['물리명대문자변환'] == True else tempWordSet['PhysicalWord']
            ### 2) 물리설명에 대해 첫글자, 공백앞 문자 제거
            tempWordSet['PhysicalDescription'] = capwords(tempWordSet['PhysicalDescription']) if self.wordVefiryList['물리전체명칭첫글자대문자변환'] == True else tempWordSet['PhysicalDescription']
            ### 2) 논리명, 물리명, 논리물리설명에 공백 제거
            tempWordSet['LogicalWord'] = tempWordSet['LogicalWord'].strip()
            tempWordSet['PhysicalWord'] = tempWordSet['PhysicalWord'].strip()
            tempWordSet['LogicalDescription'] = tempWordSet['LogicalDescription'].strip()
            tempWordSet['PhysicalDescription'] = tempWordSet['PhysicalDescription'].strip()
        
        return tempWordSet
    
    def _synonymusWordModification(self, tempWordSet):
        """ 입력된 단어가 동의어일 경우 물리명 및 설명, 엔터티분류어, 속성분류어 등을 표준단어와 같도록 조정"""
        condition = (self.wordStorage['LogicalWord'] == tempWordSet['synonymousWord']) & (self.wordStorage['wordStandardType'] == '표준단어')
        condition = list(condition)
        stadardWordExist = False
        if True in condition:
            standardWordSet = self.wordStorage[condition].to_dict('records')[0]
            tempWordSet['PhysicalWord']        = standardWordSet['PhysicalWord']
            tempWordSet['LogicalDescription']  = standardWordSet['LogicalDescription']
            tempWordSet['PhysicalDescription'] = standardWordSet['PhysicalDescription']
            tempWordSet['EntityClassWord']     = standardWordSet['EntityClassWord']
            tempWordSet['AttributeClassWord']  = standardWordSet['AttributeClassWord']
            stadardWordExist = True
            
        return tempWordSet, stadardWordExist 
        
    def _dictionarySyncStatusChange(self, Status=False):
        """ 딕셔너리 Sync에 대한 상태를 바꿔줌 """
        self.dictionarySync = Status
