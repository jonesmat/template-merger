#!/usr/bin/env python

""" Dynamically generates entry fields for pre-existing merge templates. """

import os
import glob
import wx
import pyperclip

__author__ = "Matt"
__copyright__ = "Copyright 2011, CEO Software"
__credits__ = ["Matt Jones"]
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Matt Jones"
__email__ = "matt@ceoetc.com"
__status__ = "Production"


[wxID_FRAME1, wxID_FRAME1CBOTEMPLATE, wxID_FRAME1PANEL1,
 wxID_FRAME1SCROLLEDWINDOW1, wxID_FRAME1STATICLINE1, wxID_FRAME1STATICTEXT1,
 ] = [wx.NewId() for _init_ctrls in range(6)]

class Frame1(wx.Frame):
	active_field_controls = []
	fields = []
	raw_template = ""

	def _init_ctrls(self):
		# generated method, don't edit
		wx.Frame.__init__(self, id=wxID_FRAME1, name='', parent=None,
						  pos=wx.Point(872, 252), size=wx.Size(320, 402),
						  style=wx.DEFAULT_FRAME_STYLE, title='Template Merger')
		self.SetClientSize(wx.Size(304, 364))

		self.panel1 = wx.Panel(id=wxID_FRAME1PANEL1, name='panel1', parent=self,
							   pos=wx.Point(0, 0), size=wx.Size(304, 364),
							   style=wx.TAB_TRAVERSAL)

		self.staticText1 = wx.StaticText(id=wxID_FRAME1STATICTEXT1,
										 label='Template:', name='staticText1',
										 parent=self.panel1,
										 pos=wx.Point(24, 24),
										 size=wx.Size(49, 13), style=0)

		self.cboTemplate = wx.ComboBox(choices=[], id=wxID_FRAME1CBOTEMPLATE,
									   name='cboTemplate', parent=self.panel1,
									   pos=wx.Point(78, 24),
									   size=wx.Size(180, 21),
									   style=wx.CB_READONLY, value='comboBox1')
		self.cboTemplate.SetLabel('comboBox1')
		self.cboTemplate.Bind(wx.EVT_COMBOBOX, self.OnCboTemplateCombobox,
							  id=wxID_FRAME1CBOTEMPLATE)

		self.editButton = wx.Button(id=wx.NewId(), name='editButton',
									parent=self.panel1,
									pos=wx.Point(268, 24),
									size=wx.Size(25, 21), style=0,
									label='>>')
		self.editButton.Bind(wx.EVT_BUTTON, self.OnEditButton)

		self.staticLine1 = wx.StaticLine(id=wxID_FRAME1STATICLINE1,
										 name='staticLine1', parent=self.panel1,
										 pos=wx.Point(16, 56),
										 size=wx.Size(272, 2), style=0)

		self.scrolledWindow1 = wx.ScrolledWindow(id=wxID_FRAME1SCROLLEDWINDOW1,
												 name='scrolledWindow1',
												 parent=self.panel1,
												 pos=wx.Point(0, 72),
												 size=wx.Size(304, 288),
												 style=wx.VSCROLL | wx.TAB_TRAVERSAL)

	def __init__(self):
		self._init_ctrls()

	def OnCboTemplateCombobox(self, event):
		""" cboTemplate onItemChanged event """
		# Remove any existing children first.
		self.clear_template()

		self.raw_template = self.get_raw_template(self.cboTemplate.GetValue())
		self.fields = self.get_template_fields()
		self.create_template_fields(self.fields)

	def get_raw_template(self, template):
		""" Pulls in the text from the selected template file. """
		filepath = r'.\templates\%s.template' % template
		f = open(filepath, 'r')

		# Pull the entire template into a single string.
		text = ""
		for line in f.readlines():
			text += line
		return text

	def clear_template(self):
		""" Cleans up all field controls used on previous templates. """
		for field in self.active_field_controls:
			getattr(self, field).Destroy()

	def get_template_fields(self):
		""" Gets list of merge fields from the template text. """
		# Check the string for <<>> template fields.  When one is found,
		# add it to the collection and then remove all instances of it
		# from the raw template string (to prevent duplicates).
		template = self.raw_template
		template_fields = []
		while template.find('<<') >= 0:
			start = template.find('<<') + 2
			end = template.find('>>')

			if start == -1 or end == -1:
				raise Exception('Invalid template field found, aborting.')

			field = template[start:end]

			template_fields.append(field)
			template = template.replace('<<' + field + '>>', '')

		return template_fields

	def create_template_fields(self, fields):
		""" Dynamically generates static text and text ctrls using exec(). """
		self.active_field_controls = []
		s_point = [15, 10]
		t_point = [115, 10]
		scroll_units = 1

		for index, field in enumerate(fields):
			# Create static text
			code = "self.staticText%d = wx.StaticText(id=wx.NewId(), " % index
			code += "name='staticText%d', parent=frame.scrolledWindow1, " % index
			code += "pos=wx.Point(%d, %d), " % (s_point[0], s_point[1])
			code += "size=wx.Size(95, 30), style=0, label='%s')" % field
			exec code
			code = "self.active_field_controls.append('staticText%d')" % index
			exec code

			# Create text control
			code = ""
			code += "self.textCtrl%d = wx.TextCtrl(id=wx.NewId(), " % index
			code += "name='textCtrl%d', parent=frame.scrolledWindow1, " % index
			code += "pos=wx.Point(%d, %d), " % (t_point[0], t_point[1])
			code += "size=wx.Size(165, 21), style=0, value='')"
			exec code
			code = "self.active_field_controls.append('textCtrl%d')" % index
			exec code

			# Advance the position for the next control set.
			s_point[1] += 30
			t_point[1] += 30
			scroll_units += 3

		code = ""
		code += "self.submitButton = wx.Button(id=wx.NewId(), "
		code += "name='submitButton', parent=frame.scrolledWindow1, "
		code += "pos=wx.Point(%d, %d), " % (50, t_point[1] + 10)
		code += "size=wx.Size(200, 21), style=0, label='Merge To Clipboard')"
		exec code
		self.submitButton.Bind(wx.EVT_BUTTON, self.OnSubmitButton)
		self.active_field_controls.append('submitButton')

		scroll_units += 3

		# Set the scroll bars. (x_unit_size, y_unit_size, x_count, y_count)
		# The scroll bar area is the unit_size * count.
		self.scrolledWindow1.SetScrollbars(0, 10, 0, scroll_units)

	def OnEditButton(self, event):
		""" OnEditButton click event """
		template_name = self.cboTemplate.GetValue()
		if len(template_name) > 0:
			filepath = r'.\templates\%s.template' % template_name
			os.system("notepad.exe %s" % filepath)

	def OnSubmitButton(self, event):
		""" OnSubmitButton click event """
		text = self.get_merged_text()
		pyperclip.copy(text)
		self.submitButton.Label = "Copied %d Characters to Clipboard!" % len(text)

	def get_merged_text(self):
		""" Merges the template text with the user input. """
		text = self.raw_template
		for i, field in enumerate(self.fields):
			# 2 * the index + 1is the TextCtrl for the field set.
			text_value = getattr(self, self.active_field_controls[i * 2 + 1]).Value
			field_key = '<<' + field + '>>'

			text = text.replace(field_key, text_value)
		return text
		


class TemplateMerger():
	def __init__(self):
		pass

	def load_templates(self):
		""" Loads template file names from a templates sub directory. """
		templates = []
		for template_file in glob.glob(r'.\templates\*.template'):
			templates.append(template_file.split('.\\templates\\')[1]\
							 .split('.template')[0])
		return templates

if __name__ == '__main__':
	app = wx.PySimpleApp()
	frame = Frame1()
	frame.Show()

	merger = TemplateMerger()
	frame.cboTemplate.AppendItems(merger.load_templates())

	app.MainLoop()