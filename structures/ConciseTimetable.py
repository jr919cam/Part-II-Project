from datetime import datetime 
from enum import Enum

class Course(Enum):
    Tex = 'LaTeX and Julia'
    Denot = 'Denotational Semantics'
    IntComArch = 'Introduction to Computer Architecture'
    EconLaw = 'Economics, Law and Ethics'
    GroupProj = 'Group Project Briefing'
    Types = 'Types'
    Business = 'Business Studies'
    PrincComm = 'Principles of Communication'
    ProgC = 'Programming in C and C++'
    Semantics = 'Semantics of Programming Languages'
    BioInfo = 'Bioinformatics'
    Databases = 'Databases'
    InfoTheo = 'Information Theory'
    Library = 'Library'
    SciComp = 'Scientific Computer'
    Crypto = 'Cryptography'
    QuantComp = 'Quantum Computing'
    FurtherHCI = 'Further Human–Computer Interaction'
    OptComp = 'Optimising Compilers'
    CSM = 'Computer Systems Modelling'
    RandAlgthm = 'Randomised Algorithms'
    ECommerce = 'E-Commerce'
    MLBayInfer = 'Machine Learning and Bayesian Inference'
    How2writeD = 'How to write a dissertation'
    AdComArch = 'Advanced Computer Architecture'
    MLRD = 'Machine Learning and Real-world Data'
    HLogModC = 'Hoare Logic and Model Checking'
    IntDesign = 'Interaction Design'
    BusSeminrs = 'Business Seminars'
    ArtInt = 'Artificial Intelligence'
    ForModLang = 'Formal Models of Language'
    IIProject = 'Part II Project Briefing'

class ConciseTimetable():
    nineToTen = {
        '10-10':Course.Tex.value,
        '15-10':Course.Tex.value,
        '30-10':Course.Denot.value,
        '1-11':Course.Denot.value,
        '6-11':Course.Denot.value,
        '8-11':Course.Denot.value,
        '13-11':Course.Denot.value,
        '15-11':Course.Denot.value,
        '20-11':Course.Denot.value,
        '22-11':Course.Denot.value,
        '27-11':Course.Denot.value,
        '29-11':Course.Denot.value,
        '23-01':Course.QuantComp.value,
        '24-01':Course.Crypto.value,
        '27-01':Course.Crypto.value,
        '28-01':Course.QuantComp.value,
        '29-01':Course.Crypto.value,
        '30-01':Course.QuantComp.value,
        '31-01':Course.Crypto.value,
        '03-02':Course.Crypto.value,
        '04-02':Course.QuantComp.value,
        '05-02':Course.Crypto.value,
        '06-02':Course.QuantComp.value,
        '07-02':Course.Crypto.value,
        '10-02':Course.Crypto.value,
        '11-02':Course.QuantComp.value,
        '12-02':Course.Crypto.value,
        '13-02':Course.QuantComp.value,
        '14-02':Course.Crypto.value,
        '17-02':Course.Crypto.value,
        '18-02':Course.QuantComp.value,
        '19-02':Course.Crypto.value,
        '20-02':Course.QuantComp.value,
        '21-02':Course.Crypto.value,
    }
    tenToEleven = {}
    elevenToTwelve = {}
    twelveToThirteen = {}
    
    timetable = {9:nineToTen, 10:tenToEleven, 11:elevenToTwelve, 12:twelveToThirteen}

    @staticmethod
    def getStatus(acp_timestamp: float) -> tuple[str, str]:
        '''
        returns the current lecture course and repspective lecturer which are currently 
        occupying LT1 for the 2024/25 academic year

        all lectures in LT1 occur on the hour and last for either 1 or 2 hours exactly
        '''

        # get hour and date from timestamp
        datetimeObj = datetime.fromtimestamp(acp_timestamp)

        date = datetimeObj.strftime('%d-%m') # DD-MM
        hour = datetimeObj.hour # 0-23

        # index by hour then date?
