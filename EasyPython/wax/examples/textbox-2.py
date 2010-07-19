# textbox-2.py
#

from wax import *

demo_text = """\
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.
"""

class MainFrame(VerticalFrame):
    def Body(self):
        toolbar = self.make_toolbar(self)
        self.AddComponent(toolbar, expand='h')

        self.textbox = TextBox(self, multiline=1, readonly=1,
                       Font=Font("Courier New", 10), Size=(650,500),
                       Value=demo_text)
        self.AddComponent(self.textbox, expand='both')

        self.Pack()

    def make_toolbar(self, parent):
        p = HorizontalPanel(parent)
        b = Button(p, "test test...", event=self.one)
        p.AddComponent(b)
        p.Pack()
        return p

    def one(self, event):
        assert self.textbox.Modified == False
        a = "OH! "
        self.textbox.InsertionPoint = 42
        self.textbox.InsertText(0, a)
        assert self.textbox.InsertionPoint == 42 + len(a)
        self.textbox.InsertText(101, a)
        assert self.textbox.InsertionPoint == 42 + len(a)

        assert self.textbox.Modified == True
        self.textbox.Modified = False
        assert self.textbox.Modified == False
        self.textbox.Modified = True
        assert self.textbox.Modified == True

        assert len(self.textbox.Lines) == 13


app = Application(MainFrame, title='textbox-2')
app.Run()

