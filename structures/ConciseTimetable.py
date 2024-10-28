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
        '24-02':Course.Crypto.value,
        '25-02':Course.QuantComp.value,
        '26-02':Course.Crypto.value,
        '27-02':Course.QuantComp.value,
        '28-02':Course.Crypto.value,
        '04-03':Course.QuantComp.value,
        '06-03':Course.QuantComp.value,
        '11-03':Course.QuantComp.value,
        '13-03':Course.QuantComp.value,
        '18-03':Course.QuantComp.value,
    }
    tenToEleven = {
        '14-10':Course.IntComArch.value,
        '16-10':Course.IntComArch.value,
        '18-10':Course.IntComArch.value,
        '21-10':Course.IntComArch.value,
        '23-10':Course.IntComArch.value,
        '25-10':Course.IntComArch.value,
        '28-10':Course.IntComArch.value,
        '30-10':Course.IntComArch.value,
        '01-11':Course.IntComArch.value,
        '04-11':Course.IntComArch.value,
        '06-11':Course.IntComArch.value,
        '07-11':Course.EconLaw.value,
        '08-11':Course.IntComArch.value,
        '11-11':Course.GroupProj.value,
        '12-11':Course.EconLaw.value,
        '13-11':Course.IntComArch.value,
        '14-11':Course.EconLaw.value,
        '15-11':Course.IntComArch.value,
        '18-11':Course.IntComArch.value,
        '19-11':Course.EconLaw.value,
        '20-11':Course.IntComArch.value,
        '21-11':Course.EconLaw.value,
        '26-11':Course.EconLaw.value,
        '28-11':Course.EconLaw.value,
        '03-12':Course.EconLaw.value,
        '23-01':Course.FurtherHCI.value,
        '24-01':Course.OptComp.value,
        '27-01':Course.OptComp.value,
        '28-01':Course.FurtherHCI.value,
        '29-01':Course.OptComp.value,
        '30-01':Course.FurtherHCI.value,
        '31-01':Course.OptComp.value,
        '03-02':Course.OptComp.value,
        '04-02':Course.FurtherHCI.value,
        '05-02':Course.OptComp.value,
        '06-02':Course.FurtherHCI.value,
        '07-02':Course.OptComp.value,
        '10-02':Course.OptComp.value,
        '11-02':Course.FurtherHCI.value,
        '12-02':Course.OptComp.value,
        '13-02':Course.FurtherHCI.value,
        '14-02':Course.OptComp.value,
        '17-02':Course.OptComp.value,
        '18-02':Course.FurtherHCI.value,
        '19-02':Course.OptComp.value,
        '21-02':Course.OptComp.value,
        '24-02':Course.OptComp.value,
        '26-02':Course.OptComp.value,
        '27-02':Course.CSM.value,
        '28-02':Course.OptComp.value,
        '02-05':Course.HLogModC.value,
        '05-05':Course.HLogModC.value,
        '07-05':Course.HLogModC.value,
        '09-05':Course.HLogModC.value,
        '12-05':Course.HLogModC.value,
        '14-05':Course.HLogModC.value,
        '16-05':Course.HLogModC.value,
        '19-05':Course.HLogModC.value,
        '21-05':Course.HLogModC.value,
        '23-05':Course.HLogModC.value,
        '26-05':Course.HLogModC.value,
        '28-05':Course.HLogModC.value,
    }
    elevenToTwelve = {
        '10-10': Course.PrincComm.value,
        '11-10': Course.Types.value,
        '14-10': Course.Types.value,
        '15-10': Course.PrincComm.value,
        '16-10': Course.Types.value,
        '17-10': Course.PrincComm.value,
        '18-10': Course.Types.value,
        '21-10': Course.Types.value,
        '22-10': Course.PrincComm.value,
        '23-10': Course.Types.value,
        '24-10': Course.PrincComm.value,
        '25-10': Course.Types.value,
        '28-10': Course.Types.value,
        '29-10': Course.PrincComm.value,
        '30-10': Course.Types.value,
        '31-10': Course.PrincComm.value,
        '01-11': Course.Types.value,
        '04-11': Course.Types.value,
        '05-11': Course.PrincComm.value,
        '06-11': Course.Types.value,
        '07-11': Course.PrincComm.value,
        '11-11': Course.Business.value,
        '12-11': Course.PrincComm.value,
        '13-11': Course.Business.value,
        '14-11': Course.PrincComm.value,
        '18-11': Course.Business.value,
        '19-11': Course.PrincComm.value,
        '20-11': Course.Business.value,
        '21-11': Course.PrincComm.value,
        '25-11': Course.Business.value,
        '26-11': Course.PrincComm.value,
        '27-11': Course.Business.value,
        '28-11': Course.PrincComm.value,
        '02-12': Course.Business.value,
        '03-12': Course.PrincComm.value,
        '04-12': Course.Business.value,
        '23-01': Course.MLBayInfer.value,
        '27-01': Course.RandAlgthm.value,
        '28-01': Course.MLBayInfer.value,
        '29-01': Course.RandAlgthm.value,
        '30-01': Course.MLBayInfer.value,
        '31-01': Course.RandAlgthm.value,
        '03-02': Course.RandAlgthm.value,
        '04-02': Course.MLBayInfer.value,
        '05-02': Course.RandAlgthm.value,
        '06-02': Course.MLBayInfer.value,
        '07-02': Course.RandAlgthm.value,
        '10-02': Course.RandAlgthm.value,
        '11-02': Course.MLBayInfer.value,
        '12-02': Course.RandAlgthm.value,
        '13-02': Course.MLBayInfer.value,
        '14-02': Course.RandAlgthm.value,
        '17-02': Course.RandAlgthm.value,
        '18-02': Course.MLBayInfer.value,
        '19-02': Course.RandAlgthm.value,
        '20-02': Course.MLBayInfer.value,
        '21-02': Course.RandAlgthm.value,
        '24-02': Course.ECommerce.value,
        '25-02': Course.MLBayInfer.value,
        '26-02': Course.ECommerce.value,
        '27-02': Course.MLBayInfer.value,
        '03-03': Course.ECommerce.value,
        '04-03': Course.MLBayInfer.value,
        '05-03': Course.ECommerce.value,
        '06-03': Course.MLBayInfer.value,
        '07-03': Course.How2writeD.value,
        '10-03': Course.ECommerce.value,
        '11-03': Course.MLBayInfer.value,
        '12-03': Course.ECommerce.value,
        '13-03': Course.MLBayInfer.value,
        '17-03': Course.ECommerce.value,
        '18-03': Course.MLBayInfer.value,
        '19-03': Course.ECommerce.value,
        '01-05': Course.IntDesign.value,
        '06-05': Course.IntDesign.value,
        '07-05': Course.BusSeminrs.value,
        '08-05': Course.IntDesign.value,
        '09-05': Course.BusSeminrs.value,
        '12-05': Course.BusSeminrs.value,
        '13-05': Course.IntDesign.value,
        '14-05': Course.BusSeminrs.value,
        '15-05': Course.IntDesign.value,
        '16-05': Course.BusSeminrs.value,
        '19-05': Course.BusSeminrs.value,
        '20-05': Course.IntDesign.value,
        '21-05': Course.BusSeminrs.value,
        '22-05': Course.IntDesign.value,
        '23-05': Course.BusSeminrs.value,
        '29-05': Course.IntDesign.value,
    }
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
