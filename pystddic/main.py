import pandas as pd
import numpy as np
from string import capwords
from copy import copy
import psutil
import ray
import pickle
import sys
import os
from tqdm.notebook import tqdm

#################################################################################################################
#################################################################################################################
#################################################################################################################
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
        if 'progress' in kwargs.keys():
            records = tqdm(records) if kwargs['progress'] else records

        error_words = []

        #### 멀티 Insert시 replace 요청일 경우 기존 단어를 삭제하고 새로 입력한다.
        #### DB와 실시간 연동시 필요하다, MultiCurrenty 환경을 너무 고민하지 말자. 그건 DB 버전으로 할 경우에 사용
        #### multiInsert에 대해 type? 을 정의하여 replace(전체변경), merge(데이터병합) 의 유형으로 생성함
        #### replace : 데이터를 전체 삭제하고 새로 반영
        
        allReplace = False
        if 'replace' in kwargs.keys():
            allReplace = True if kwargs['replace'] else allReplace
                
        
        if allReplace:


        else:
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
        

#################################################################################################################
#################################################################################################################
#################################################################################################################

class stdDicMultiProcessing:
    """ 형태소분석 병렬 처리를 위한 별도 클래스 """
    def __init__(self):
        self.rayInit = False
        
    def _listSplit(self, arr):
        """ 병렬개수에 맞춰 분할하기"""
        ret_arr = [ [] for _ in range(self.MultiProcessCount)]
        for i, val in enumerate(arr):
            ret_arr[i % self.MultiProcessCount].append(val)
        return ret_arr

    def MultiProcessingInit(self):
        """ 병렬처리 모듈 Run """
        self.MultiProcessCount = psutil.cpu_count(logical=False)
        ray.init(num_cpus=self.MultiProcessCount, ignore_reinit_error=True)
        self.rayInit = True

    def MultiProcessingShutdown(self):
        """ 병렬처리 모듈 Shutdown """
        self.MultiProcessCount = psutil.cpu_count(logical=False)
        ray.shutdown()
        
    def _termParsingMultiProcessing(self, termList, wordStorage):
        """ 병렬처리를 위한 처리 함수 """
        if not self.rayInit:
            self.MultiProcessingInit()
        partTermList = self._listSplit(termList)
        
        @ray.remote
        def _tempTermParsing(partTermList):
            finalResults = list()
            termParser = termParse()
            termParser._wordStorageSet(wordStorage)
            for term in partTermList:
                finalResult = termParser._termParsing(term)
                finalResults.append(finalResult)
            return finalResults
        
        a = [_tempTermParsing.remote(partTermList[i]) for i in range(self.MultiProcessCount)]
        _result = ray.get(a)
        
        result = []
        for partResult in _result:
            result += partResult
        
        return result

#################################################################################################################
#################################################################################################################
#################################################################################################################

class termParse(stdDicMultiProcessing):
    """ 단어사전을 활용하여 용어에 대한 형태소 분석 """    
    def __init__(self):
        self.termParseVefiryList = {'물리명연결문자': '_',
                              }        
        
    def _wordStorageSet(self, wordStorage):
        """ 용어 형태소분석을 위한 단어사전을 지정 """
        self.wordStorage = wordStorage
        
    def _attributeClassCheck(self, termParsingResult):
        """ 속성분류어 체크 """
        attrclsword = self.wordStorage[self.wordStorage['AttributeClassWord']]['LogicalWord'].tolist()
        
        termParsingResult.reverse()
        attributeClassWord, attributeClassResult = "", False
        tempAttributeClassWord = ""
        for word, _, _, _, _, _ in termParsingResult:
            tempAttributeClassWord = word + tempAttributeClassWord

            if tempAttributeClassWord in attrclsword:
                attributeClassWord, attributeClassResult = copy(tempAttributeClassWord), True
                
        return attributeClassWord, attributeClassResult
    
    def _numericSplit(self, term:str):
        """ 논리명의 끝 숫자를 제거 """
        parsterm = term[::-1]

        numericWord = ''
        for i, s in enumerate(parsterm):
            if s.isdigit() == True:
                numericWord += s
            elif s.isdigit() == False:
                term = term[0:len(term)-i]
                break

        return term, numericWord

    def _wordListCreation(self, term):
        """ 용어를 구성할 수 있는 단어 목록을 생성 """
        wordList = list()
        termLength = len(term)
        
        ### 만들어 질 수 있는 단어의 형태로 모두 잘라냄
        for i in range(1, termLength + 1):
            for j in range(termLength - i + 1):
                wordList.append(term[j:i+j])
        
        KeyWordList = self.wordStorage['LogicalWord'].tolist()
        ### 단어의 위치를 등록.
        termWordList = []
        for word in wordList:
            wordSearchResult = False
            if word in KeyWordList:
                wordSearchResult = True
                _, PhysicalWord, _, _, _, _, wordStandardType, synonymousWord = \
                    self.wordStorage[self.wordStorage['LogicalWord'] == word].values[0]

            for i in range(termLength - len(word) + 1):
                result = term.startswith(word, i)
                if result == True:
                    if wordSearchResult == True:
                        termWordList.append([word, PhysicalWord, i, i+ len(word), wordStandardType, synonymousWord])
                    elif wordSearchResult == False and len(word) == 1:
                        termWordList.append([word, "", i, i+ len(word), '비표준', word])
                            
                        
        termWordList = pd.DataFrame(termWordList, columns=['논리명', '물리명', '시작위치', '종료위치', '단어유형', '표준단어'])
        termWordList = termWordList.drop_duplicates().sort_values(['시작위치', '종료위치']).to_numpy()
        return termWordList
    
    def _termCartessianProduct(self, term, termWordList):
        ### 단어 조합으로 만들 수 있는 경우의 수를 생성
        termParsingList = list()

        for i in range(len(term)):
            MatchList = termWordList[termWordList[:, 2] == i]
            if i == 0:
                #표준단어나 동의어가 존재할 경우, 비표준단어로 시작은 삭제함 (단어의 경우의 수를 줄이기 위함
                if '표준단어' in MatchList[:, 4] or '동의어' in MatchList[:, 4]:
                    MatchList = MatchList[MatchList[:, 4] != '비표준']
                for MatchRow in MatchList:
                    termParsingList.append(MatchRow)                    
            else:
                NewParsingList = list()
                for ParsingCol in termParsingList:
                    matching = False
                    for MatchRow in MatchList:
                        if ParsingCol[-3] == MatchRow[2]:
                            matching = True
                            NParsingCol = np.append(ParsingCol, MatchRow)
                            NewParsingList.append(NParsingCol)
                    if not matching:
                        NewParsingList.append(ParsingCol)
                termParsingList = NewParsingList
        return termParsingList
        
    def _nonStandardwordCleansing(self, termParsing):
        """비표준 단어에 대한 연결된 결과를 만듬 """
        ParsingPatterm = termParsing.reshape(-1, 6)
        NonParsWord = ""
        ParsingResult = []
        bef_e = 0
        for word, phwd, s, e, gb, stdwd in ParsingPatterm:
            if gb != '비표준':
                ParsingResult.append([word, phwd, s, e, gb, stdwd])
            else:
                if s > bef_e or s == 0:
                    NonParsWord = word
                    NonParsresult = [word, '', s, e, gb, stdwd]

                elif s == bef_e:
                    NonParsresult = copy(ParsingResult[-1])
                    s, e = NonParsresult[2], NonParsresult[3]+1
                    del ParsingResult[-1]
                    NonParsWord = NonParsWord + word
                    NonParsresult = [NonParsWord, '', s, e, gb, NonParsWord]

                ParsingResult.append(NonParsresult)
                bef_e = copy(e)
        return ParsingResult
    
        return termParsingList
    
    def _bestParsingPicking(self, termParsingList):
        """ 가장 좋은 단어의 구성을 찾음 """
        attrclsword = self.wordStorage[self.wordStorage['AttributeClassWord']]['LogicalWord'].tolist()
        
        summaryResult = []
        for i, ParsingData in enumerate(termParsingList):
            ParsingData = ParsingData.reshape(-1, 6)
            ParsingDataSummary = {'행번호':0, '속성분류어길이':99, '표준단어':0, '동의어':0, '비표준':0, '비표준길이합':0, '임시동의어':0, '임시단어':0}
            ParsingDataSummary['비표준길이합'] = sum([len(word) for word in ParsingData[ParsingData[:, 4] == '비표준'][:, 0]])

            ks, vs = np.unique(ParsingData[:, 4], return_counts=True)
            for k, v in zip(ks, vs):
                ParsingDataSummary[k] = v

            #ParsingDataSummary['속성분류어사용여부'] = 'Y' if ParsingData[-1][0] in attrclsword else 'N'
            ParsingDataSummary['속성분류어길이'] = len(ParsingData[-1][0]) if ParsingData[-1][0] in attrclsword else 99

            ParsingDataSummary['행번호'] = i
            summaryResult.append(ParsingDataSummary)

        df = pd.DataFrame(summaryResult).fillna(0)
        df['표준동의어합'] = df['동의어'] + df['표준단어']
        
        ## 형태소분석 조건중 우선 순위 지정
        #### 1) 비표준 단어의 길이가 적어야 한다.
        #### 2) 표준단어와 동의어 단어의 사용 개수가 적어야 한다.
        #### 3) 단어 사용개수가 동률일경우, 동의어 사용개수가 적어야 한다
        #### 4) 속성분류어의 길이가 적은 것을 권장한다 (명과 장명, 수와 점수)

        #df = df.sort_values(by=['속성분류어사용여부', '비표준길이합','표준동의어합', '동의어'], ascending=[False, True, True, True])
        df = df.sort_values(by=['비표준길이합', '표준동의어합', '동의어', '속성분류어길이'], ascending=[True, True, True, True])
        idx = df.head(1).reset_index()['index'][0]
        return termParsingList[idx]
    
    def _ParsingResultConcat(self, bestParsingResult):
        physicalWordConcatChar = self.termParseVefiryList['물리명연결문자']
        
        """ 가장 좋은단어의 구성을 결과로 연결하고, 요약함 """
        logicalTermParsingResult, physicalTermParsingResult = "", ""
        
        finalResult = {"logicalParsingResult":"",
                       "physicalName":"",
                       "termSplitResult":"",
                       "attributeClassWord":"",
                       "attributeClassUseResult":False,
                       "nonstandardWords":"",
                       "synonymousWords":"",
                       "termOriginalName":"",
                       "termRegisterValidationCheck":False,
                       "termRegistration":False,
                      }

        for i, (LogicalWord, PhysicalWord, _, _, wordStandardType, synonymousWord) in enumerate(bestParsingResult):
            finalResult['termSplitResult'] += LogicalWord + ';'
            
            if wordStandardType == '표준단어':
                finalResult['logicalParsingResult'] += "[" + LogicalWord + "]"
            
            elif wordStandardType == '동의어':
                finalResult['logicalParsingResult'] += "{" + synonymousWord + "}"
                finalResult['synonymousWords'] += LogicalWord + ";"
                
            elif wordStandardType == '비표준':
                finalResult['logicalParsingResult'] += "%" + LogicalWord + "%"
                
                finalResult['nonstandardWords'] += LogicalWord + ";"                
                
            if wordStandardType == '표준단어' or wordStandardType == '동의어':
                finalResult['physicalName'] += PhysicalWord if i == 0 else physicalWordConcatChar + PhysicalWord
            else:
                finalResult['physicalName'] += '%' + LogicalWord + '%' if i == 0 else physicalWordConcatChar + '%' + LogicalWord + '%'
                
        finalResult["attributeClassWord"], finalResult["attributeClassUseResult"] = self._attributeClassCheck(bestParsingResult)
        
        ### 용어 등록 가능 여부
        finalResult['termRegisterValidationCheck'] = True if len(finalResult['nonstandardWords']) == 0 and len(finalResult['synonymousWords']) == 0 else False    

        return finalResult
    
    def _termParsing(self, term):
        """ 단어 동기화가 필요함 """
        term, numericWord = self._numericSplit(term)
        termWordList = self._wordListCreation(term)
        termParsingList = self._termCartessianProduct(term, termWordList)
        bestParsingResult = self._bestParsingPicking(termParsingList)
        bestParsingResult = self._nonStandardwordCleansing(bestParsingResult)
        finalResult = self._ParsingResultConcat(bestParsingResult)
        finalResult["termOriginalName"] = term + numericWord
        
        return finalResult
    
#################################################################################################################
#################################################################################################################
#################################################################################################################
class termManage:
    def __init__(self):
        pass
    
    def termInsert(self, LogicalWord:str, LogicalDescription:str, wordStandardType:str, **kwargs):
        """ 용어를 등록 """
        pass
    
    def termUpdate(self, termSet:dict, **kwargs):
        """ 용어를 변경 """
        pass    
        
    def _termModification(self, termSet:dict):
        """ 등록하고자 하는 용어를 표준에 맞게 조정"""
        pass
    
    def _termValidationCheck(self, termSet:dict):
        """ 용어가 맞는지 검증 """
        pass
    
    

#################################################################################################################
#################################################################################################################
#################################################################################################################

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

    
    
#################################################################################################################
#################################################################################################################
#################################################################################################################

class stddic:
    def __init__(self):
        self.wordManager = wordManage()
        self.termParser = termParse()
        self.domainManager = domainManage()
            
    def multiTermParsing(self, termList, **kwargs):
        """ 병렬처리 """
        parallel = kwargs['parallel'] if 'parallel' in kwargs.keys() else False
        
        if parallel:
            results = self.termParser._termParsingMultiProcessing(termList, self.wordManager.wordStorage)            
        else:
            if self.wordManager.dictionarySync == False:
                self.termParser._wordStorageSet(self.wordManager.wordStorage)
                self.wordManager.dictionarySync = True
            results = list()
            for term in termList:
                result = self.termParser._termParsing(term)
                results.append(result)
        
        return results
    
    def termParsing(self, term):
        """ 용어를 단어 기준으로 파싱함 """
        if self.wordManager.dictionarySync == False:
            self.termParser._wordStorageSet(self.wordManager.wordStorage)
            self.wordManager.dictionarySync = True

        result = self.termParser._termParsing(term)
        
        return result
    
    def dictionaryPath(self, filePath):
        """ 딕셔너리를 저장하고 불러들일 경로 지정 """
        self.filePath = filePath
    
    def dictionarySave(self, filename):
        fullFilePath = self.filePath + filename
        with open(fullFilePath, 'wb') as fw:
            pickle.dump(self.wordManager.wordStorage, fw)
        print('Dictionary Dump file 저장 완료')
        
    def dictionaryLoad(self, filename):
        """ 단어 사전 로드 """
        fullFilePath = self.filePath + filename
        with open(fullFilePath, 'rb') as fr:
            self.wordManager.wordStorage = pickle.load(fr)
        print('Dictionary Dump file 호출 완료')

    def nonStandardWordExtraction(self, termList):
        """ 사전에 정의되지 않은 단어를 추출함 """
        ParsingResult = self.multiTermParsing(termList, parallel=True)
        ParsingResultDf = pd.DataFrame(ParsingResult)
        
        ### 비표준단어 목록 추출(Unique)
        nonstandardWordList = []
        for nonstandardWords in ParsingResultDf['nonstandardWords']:
            nonstandardWords = nonstandardWords[:-1].split(";")
            if len(nonstandardWords) > 0 and nonstandardWords[0] != '':
                nonstandardWordList += [word.strip() for word in nonstandardWords]
        nonstandardWordList = list(set(nonstandardWordList))
        nonstandardWordList.sort()
        
        results = []
        replaceWords = [':', '(', ')', '[', ']'] ###해당 단어가 포함되어 있으면 치환함, 오류 처리용
        skipWords = ['.', '?', ''] ### 해당단어는 검색하지 않음
        
        ## 해당단어를 포함하고 있는 용어를 찾음
        for word in nonstandardWordList:
            cnt = 0
            if word not in skipWords:
                orgword = word
                for replaceWord in replaceWords:
                    word = word.replace(replaceWord , '\\'+replaceWord)
                word = "%" + word + "%"
                useTerms = list(set(ParsingResultDf[ParsingResultDf['logicalParsingResult'].str.contains(word)]['termOriginalName'].tolist()))
                useTerms = ", ".join(useTerms)
                if useTerms != '':
                    results.append([orgword, useTerms, len(useTerms)])
                    
        results = pd.DataFrame(results, columns=['비표준단어명', '비표준단어사용용어목록', '사용건수']).sort_values(by=['사용건수'], ascending=False)
        
        return results
