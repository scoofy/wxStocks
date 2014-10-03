import wx
import sys
 
class Fader(wx.Frame):
	def __init__(self):
		wx.Frame.__init__(self, None, title='Test')
		self.amount = 255
		self.delta = 5
		panel = wx.Panel(self, wx.ID_ANY)

		self.SetTransparent(self.amount)
		self.timer = None

		refresh_screen_button = wx.Button(self, label="refresh", pos=(150,90), size=(-1,-1))
		refresh_screen_button.Bind(wx.EVT_BUTTON, self.fadeOutThenIn, refresh_screen_button)

		self.quit_button = None

		self.first_cycle = True


	def fadeOutThenIn(self, event):
		## ------- Fade out Timer -------- ##
		self.timer = wx.Timer(self, wx.ID_ANY)
		self.timer.Start(30)
		self.Bind(wx.EVT_TIMER, self.AlphaCycle)
		## ---------------------------- ##

	def AlphaCycle(self, evt):
		self.amount -= self.delta
		if not self.first_cycle:
			return
		if self.amount >= 255:
			self.delta = -self.delta
			self.amount = 255
		if self.amount <= 0:
			self.delta = -self.delta
			self.amount = 0
		self.SetTransparent(self.amount)
		if self.amount == 255:
			self.first_cycle = False
			self.timer.Stop()
			self.quit_button = wx.Button(self, label="quit", pos=(150,120), size=(-1,-1))
			self.quit_button.Bind(wx.EVT_BUTTON, self.quit, self.quit_button)
	def quit(self, event):
		sys.exit()

# if __name__ == '__main__':
# 	app = wx.App(False)
# 	frm = Fader()
# 	frm.Show()
# 	app.MainLoop()

import hashlib
def make_sha256_hash(pw):
	return hashlib.sha256(pw).hexdigest()

print make_sha256_hash("blah")