
def init(plugins) :
        plugins.append(ChineseChessPlugin())

def ChineseChessPlugin() :
        def RegiterPlugin(self, mainFrame) :
                print "hehreerererereer"
                self.mainFrame = mainFrame        
                mainFrame.SubjectMsgHandler["chinese_chess"] = self.HandleMessage
                
        def HandleMessage(self, msg) :
                pass
                
