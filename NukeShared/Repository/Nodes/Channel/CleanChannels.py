# CleanChannels v1.0 - Created by Henrique Moser, September, 2012

import nuke , os , nukescripts , copy

class CleanChannels( nukescripts.PythonPanel):
	def __init__(self):
		nukescripts.PythonPanel.__init__(self , 'Clean Channels', 'com.ohufx.CleanChannels')
		print 'Clean Channels'
		
		#VARIABLES
		
		self.__DEBUG = False 		# Sets debug mode: a lot of things will be printed if this is set to True
		self.__ignore_knobs = set()	# Future
		self.__lines = list()
		self.__index = list()
		self.__channels = list()
		self.__all_channels = False
		
		# CREATING KNOBS
		self.in_file_knob = nuke.Text_Knob( 'in_script' ,'Input script: ')
		self.out_file_knob = nuke.File_Knob( 'out_script' , 'Output script: ' )

		self.clean_knob = nuke.PyScript_Knob( 'clean_channels' , ' Clean Channels ')
		self.get_in_file_knob = nuke.PyScript_Knob( 'get_file' , ' New Input Script ')
		self.all_channels_knob = nuke.PyScript_Knob( 'all_channels' , ' All channels ' )
		
		# ADDING KNOBS
		
		self.addKnob(self.in_file_knob)
		self.addKnob( self.__add_line() )
		self.addKnob(self.out_file_knob)
		self.addKnob( self.__add_line() )
		self.addKnob(self.get_in_file_knob)
		self.addKnob(self.clean_knob)
		self.addKnob( self.__add_line() )
		self.addKnob(self.all_channels_knob)

		# GET FIRST VALUES
		
		self.in_file_knob.setValue( nuke.Root().name() )
		self.__getChannels()
		self.showPane()


	# METHODS

	def __add_line(self):
		# Returns a line object to be added in the Pane UI.
		return nuke.Text_Knob('')

	def __getChannels( self ):
		in_file = self.in_file_knob.value()
		if (in_file != 'Root'):
			self.__debug( 'In file: %s' %(in_file) )
		else:
			in_file = self.__getNewScript()
			
		try:
			rfile = open( in_file , 'r')
			self.__setOutput(in_file)
			lines = []
			index = []
			channels = []
			more_lines = True
			while more_lines == True:
				try:
					line = rfile.next()
					if ( line.find('add_layer')!= -1 ):
						chans = line.split('{')[1][:-2]
						chans = chans.split(' ')
						channels.extend(chans)					
						index.append( len(lines))
					lines.append(line)
				except:
					more_lines = False
					break
			rfile.close()
			self.__lines = copy.copy(lines)
			self.__index = index
			self.__channels = channels
			self.__setKnobs(channels)
		except:
			nuke.message('Something went wrong, please select the script<br>you want to clean the custom channels.')

	def __setOutput( self , in_file):
		name = os.path.split(in_file)
		dot_index = name[1].rfind('.')
		sufix = name[1][dot_index:]
		prefix = name[1][:dot_index]
		new_name = os.path.join( name[0] , (prefix + '_clean' + sufix) )
		self.out_file_knob.setValue( new_name )

	def __getNewScript( self ):
			in_file =''
			try:
				in_file = nuke.getFilename('Select input script:' , '*.nk , *.gizmo , *.tcl' , (os.path.dirname( nuke.Root().name() )) )
				self.in_file_knob.setValue( in_file )
				return in_file
			except TypeError:
				nuke.message( 'Error: you must select a file' )
				return False

	def __setKnobs(self , channels):
		ks = self.knobs()
		for k in ks:
			k_class = ks[k].Class()
			if ( k_class == 'Boolean_Knob'):
				self.removeKnob(ks[k])
		count = 4
		for ch in channels:
			ch_name = ch.replace('.' , '_')
			self.addKnob( nuke.Boolean_Knob( ch_name , ch ) )
			if count == 4:
				self.knobs()[ch_name].setFlag(nuke.STARTLINE)
				count = 0
			else:
				count += 1


	def __toggleChannels(self):
		val = self.__all_channels
		if (val == True):
			val = False
		else:
			val = True
		ks = self.knobs()
		for k in ks:
			if (ks[k].Class() == 'Boolean_Knob'):
				ks[k].setValue(val)
		self.__all_channels = val


	def __cleanChannels(self):
		index = copy.copy(self.__index)
		lines = copy.copy(self.__lines)
		del_chans = list()
		
		ks = self.knobs()
		for k in ks:
			if (ks[k].value() == True):
				k = k.replace('_' , '.')
				del_chans.append (k)
		del_chans = set(del_chans)
		
		remove_list = list()
		for i in index:
			self.__debug( 'Dirty line is: %s' %(lines[i]) )
			pfx_i = lines[i].find('{') + 1
			sfx_i = lines[i].find('}')
			line = [ lines[i][:pfx_i] , lines[i][pfx_i:sfx_i] , lines[i][sfx_i:] ]	
			spt_line = set( line[1].split(' ') )
			clean_line = spt_line - del_chans
			clean_line = str(' ').join(clean_line)
			if clean_line == '':
				remove_list.append(lines[i])
			else:
				line[1] = clean_line
				line = str(line[0]) + str(line[1]) + str(line[2])
				lines[i] = line
				self.__debug( 'Clean line is: %s' %(lines[i]) )
			
		for obj in remove_list:
			self.__debug('Removed line: %s' %(obj))
			lines.remove(obj)
			
		self.__saveCleanFile( lines )
		'''
		if ( cmp(lines , self.__lines) != 0 ):
			self.__saveCleanFile( lines )
		else:
			nuke.message('You must select the channels to delete.')
			for o in self.__lines:
				print o
		'''


	def __saveCleanFile( self , lines ):
		out_file = self.out_file_knob.value()
		if ( os.path.exists(out_file) == True ) and ( nuke.ask( (out_file +'<br>The output file already exist. Are you sure you want to overwrite it?') ) == False ):
			self.__debug('do not overwrite it')
			nuke.message( 'Please, enter a new output file name.' )
		else:
			self.__debug('go ahead')
			w_file = open( out_file , 'w' )
			w_file.writelines(lines)
			w_file.close()
			nuke.message('Now it is recommended to close Nuke and<br>restarting it before loading the new cleaned up file')

	def knobChanged(self,knob):
		kname = knob.name()
		if (kname == 'get_file'):
			check = self.__getNewScript()
			if ( check != False ):
				self.__getChannels()
		elif (kname == 'all_channels'):
			self.__toggleChannels()
		elif (kname == 'clean_channels'):
			self.__cleanChannels()
	
	def __debug(self , msg):
		if (self.__DEBUG == True):
			print str(msg)

	def showPane(self):
		ret = nukescripts.PythonPanel.show(self)
		return ret
	

