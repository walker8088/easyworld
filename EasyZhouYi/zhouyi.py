
#coding:utf8

                
class Gua :
        xian_tian_ba_gua_list = (
                (u'乾', '111', u"金", 1, 6),
                (u'兑', '011', u"金", 2, 7),
                (u'离', '101', u"火", 3, 9),
                (u'震', '001', u"木", 4, 3),
                (u'巽', '110', u"木", 5, 4), 
                (u'坎', '010', u"水", 6, 1), 
                (u'艮', '100', u"土", 7, 8),
                (u'坤', '000', u"土", 8, 2),
                )
                
        def __init__(self, name, code, wu_xing, xian_tian_no, hou_tian_no) :
                self.name = name
                self.code = code
                self.wu_xing = wu_xing
                self.xian_tian_no = xian_tian_no
                self.hou_tian_no = hou_tian_no
        
        def __str__(self) :
                return self.name
                
        @staticmethod
        def Code2Gua(code) :
                for item in Gua.xian_tian_ba_gua_list :
                        if item[1] == code :
                                return Gua(*item)
        
        @staticmethod
        def Code2Index(code) :
                for item in Gua.xian_tian_ba_gua_list :
                        if item[1] == code :
                                return item[3] - 1
        
        @staticmethod
        def Name2Index(name) :
                index = 0
                for item in Gua.xian_tian_ba_gua_list :
                        if item[0] == name :
                                return index
                        index += 1
        
        @staticmethod
        def Index2Gua(index) :
                param = Gua.xian_tian_ba_gua_list[index] 
                return Gua(*param)
                
        def relation(self, other) :
                pass
                
chong_gua_dict = {}
#排列方法：横排为上卦，竖排为下卦
xian_tian_chong_gua_list = (       
       #(u'乾',   u'兑',  u'离',   u'震',   u'巽',   u'坎',   u'艮',   u'坤'  )
        (u'乾',   u'夬',  u'大有', u'大壮', u'小畜', u'需',   u'大畜', u'泰'  ), #乾
        (u'履',   u'兑',  u'睽',   u'归妹', u'中孚', u'节',   u'损',   u'临'  ), #兑         
        (u'同人', u'革',  u'离',   u'丰',   u'家人', u'既济', u'贲',   u'明夷'), #离
        (u'无妄', u'随',  u'噬嗑', u'震',   u'益',   u'屯',   u'颐',   u'复'  ), #震
        (u'逅',   u'大过',u'鼎',   u'恒',   u'巽',   u'井',   u'蛊',   u'升'  ), #巽
        (u'讼',   u'困',  u'未济', u'解',   u'涣',   u'坎',   u'蒙',   u'师'  ), #坎
        (u'遁',   u'咸',  u'旅',   u'小过', u'渐',   u'蹇',   u'艮',   u'谦'  ), #艮
        (u'否',   u'萃',  u'晋',   u'豫',   u'观',   u'比',   u'剥',   u'坤'  ), #坤
        )
        
        
class ChongGua :
	def __init__(self, name = None, code = None) :
		self.name = name
                self.code = code
                if self.name == None :
                        self.name = self.Code2Name(code)
                elif self.code == None :
                        self.code = self.Name2Code(name)
        
        def YaoCi(self, index) :
                return chong_gua_dict[self.name][index]
        
        @staticmethod                
        def Code2Name(code) :
                c1 = code[:3]
                c2 = code[3:]
                i1 = Gua.Code2Index(c1)
                i2 = Gua.Code2Index(c2)
                return xian_tian_chong_gua_list[i2][i1]
        
        @staticmethod
        def Name2Code(name) :     
                i = 0
                j = 0
                find = False
                for line in xian_tian_chong_gua_list :
                        j = 0
                        for item in line :
                                if item == name :
                                        find = True
                                        break
                                j += 1
                        if find :
                                break
                        i += 1
                                
                if not find :
                        return ''
                        
                c1 = Gua.xian_tian_ba_gua_list[j][1]       
                c2 = Gua.xian_tian_ba_gua_list[i][1]
                return c1 + c2
        
        @staticmethod        
        def No2Name(no1, no2) :
                name = xian_tian_chong_gua_list[no1 - 1][no2 - 1]
                return name

        def HuGua(self) :
                return ChongGua(code = self.code[1:4] + self.code[2:5])
        
        def split(self) :
                return (self.top(), self.bottom())
                
        def top(self) :
                return Gua.Code2Gua(self.code[:3])
                
        def bottom(self) :
                return Gua.Code2Gua(self.code[3:])
                
        @staticmethod        
        def BianGua(code, changed) :
                first = code
                second = ''
                index = 6
                for c in first :
                        if index in changed :
                                if c == '0':
                                        second += '1'
                                else :
                                        second += '0'
                        else :
                                second += c
                        index -= 1
                       
                        
                return (ChongGua(code = first), ChongGua(code = second))
        
        def CuoGua(self) :
                newCode = ''
                for c in self.code :                        
                        if c == '0':
                                newCode += '1'
                        else :
                                newCode += '0'
                #end for
                return ChongGua(code = newCode)
                
        def ZongGua(self) :
                codelist = list(self.code)
                codelist.reverse()
                newcode = ''.join(codelist)
                return ChongGua(code = newcode)
                
        def diff(self, bian) :
                changelist = []
                for i in xrange(len(self.code)) :
                        if self.code[5-i] != bian.code[5-i] :
                                changelist.append(i+1)
                return changelist
                
        def info(self) :
                s = self.split()        
                return u"%-2s(%s)(%s-%s) : %s" % (self.name, self.code, s[0].name, s[1].name, self.YaoCi(0))
                
        def PrintAllRelated(self, bian = None) :       
                hu = self.HuGua()
                cuo = self.CuoGua()
                zong = self.ZongGua()
                
                print u"本卦：%s" % self.info()
                if bian :
                        print u"变卦：%s" % bian.info()        
                print u"互卦：%s" % hu.info()
                print u"错卦：%s" % cuo.info()
                print u"综卦：%s" % zong.info()
                if bian :
                        changed = self.diff(bian)
                        print u'变爻辞:'
                        for index in changed :
                                print "    ", self.YaoCi(index)
                print
                
        def __str__(self) :
                return self.name
        
def loadYaoCi(file_name) :
        file = open(file_name, "rb")
        try:
                status = "WANT_NAME"
                for line in file:
                        line = line.decode('utf8').strip()
                        if status == "WANT_NAME" :
                                if len(line) == 0:
                                        continue
                                name = line
                                status = "WANT_VALUE"
                                valuelist = []
                        elif status == "WANT_VALUE" :
                                if len(line) > 0:
                                        valuelist.append(line)
                                else :
                                        chong_gua_dict[name] = valuelist				
                                        status = "WANT_NAME"
                                        valuelist = []
                        #endif
                if status == "WANT_VALUE" :
                        chong_gua_dict[name] = valuelist				        
        finally:
                file.close()

def verifyYaoCi() :
        for line in xian_tian_chong_gua_list :
                for gua in line :
                        if gua not in chong_gua_dict :
                                print "Gua Error : ", gua
                                continue
                        value = chong_gua_dict[gua] 
                        if len(value) < 7 :
                                print "Ci Error : ", gua, value
        
loadYaoCi("ZhouYi.txt")
verifyYaoCi()

g = ChongGua(name = u"既济")
g.PrintAllRelated()

g = ChongGua(name = u"鼎")
g.PrintAllRelated()

g = ChongGua(name = u"咸")
g.PrintAllRelated()

g = ChongGua(code = '010110')
g.PrintAllRelated()

ss = ChongGua.BianGua('100001', [2,3])
ss[0].PrintAllRelated(ss[1])

