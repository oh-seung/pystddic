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
