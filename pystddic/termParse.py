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
