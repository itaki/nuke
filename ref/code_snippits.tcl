#GETTING A KNOB’S VALUE OF A SPECIFIC NODE:

#First frame of current read/write:
[value Read1.first]

#Getting a knob’s value of current node:
[value this.first_frame]

#Return label value of the input node:
[value this.size]

#Name of the input node:
[value this.input0.label]

#Name of the node before the group (Outside):
[value this.input.name]

#Return 1 if the node is on error otherwise 0:
[value this.parent.input.name]

#Get the bounding Box from the input of the node:
[value error]


#Here some expression for the Format
format.x
format.y
width
height
bbox.x
bbox.y
bbox.w
bbox.h

#Get the format from the input of the node:
#left boundary
[value input.bbox.x] 
#right boundary
[value input.bbox.r] 

#Get the format from the input of the node:
#width
[value input.format.r]
#height
[value input.format.t]

#Get the x position of the point #3 of the Bezier1 of the Roto1 node:
[value Roto1.curves.Bezier1.curve_points.3.main.x]

#Return sample pixel value of the node Add1 reading in the red at position of knob Center:
[sample Add1 Red Center.x Center.y]

#Get the value of the channel of a node, at a specific pixelcoordinates (e.g.: 10,10):
[sample [node input] red 10 10]

#---------------------------------------------------------------------
#SET VALUES

#Setting a knob’s value of a specific node:
[knob Read1.first 10]

#Setting a variable, without returning that (useful in a textnode):
[set seq [value Read1.file]; return]

#---------------------------------------------------------------------
#STRING

#Replace string in current node file knob with regex (string “proj” to “projects” in all occurences):
[regsub -all "proj" [value [node this].file] "projects"] 

#String map (replace multiple stringpairs) (this returns: xxffffxxyy):
[string map {"aa" "xx" "bb" "yy"} "aaffffaabb" ]

#Compare strings:
[string equal [value Text1.message] "bla"]

#Regexp matching:
[regexp -inline "_v\[0-9]{3}" [value Read2.file]] 

#Evaluating string
[python os.getenv('rotate') == 'xavierb']

#---------------------------------------------------------------------
#IF CONDITION

[if {condition} {expr1} else {expr2}]

#Example:
[if {[value blackpoint]==1} {return 2} {return 3}]
[if {[value blackpoint]==1} {return True} {return False}]
[if {[value blackpoint]==1} {return blackpoint} {return whitepoint}]
[if {[value filter]=="gaussian"} {return filter} {return False}]

#OTHER METHOD
condition ? then : else

#Example:
#if (r==1)? return 0: else (return r*2)
r ==1 ? 0 : r*2

#---------------------------------------------------------------------
#PATH MANIPULATIONS:

#Filepath without extension:
[file rootname [value [topnode].file]]

#Filename only:
[basename [value [topnode].file ]]

#Filename only without extension:
[basename[file rootname [value [topnode].file]]]

#---------------------------------------------------------------------
#RELATIVE PATH
#In the Read node you can use the relative path for your footage/Obj

#In your Read Node in the knob "file", use this:

#Read file "render.exe" in the same folder of your file nuke 
[python {nuke.script_directory()}]/render.exr

#Read file "render.exe" in the subfolder where your file nuke is  
[python {nuke.script_directory()}]/folder/render.exr

#Read file "render.exe" in the subfolder of your .nuke folder  
[python {"/Users/gere/.nuke} ]/folder/render.exr


[value NormalWritePath.file]

[file dirname [value [topnode].file]]/proxy/[index [split [index [split [value [topnode]file].] 0] /]end]_proxy.mov

topnode: [topnode]
filename: [filename [topnode]]
knob: [knob [topnode].file]
value: [value [topnode].file]
[file tail [value root.name]]

[python {nuke.toNode('var_holder').knob('filename').getValue()} ]

[join [lrange [split [value root.name] / ] 7 7 ] / ]
[split [string map {"_v" \uffff} [join [lrange [split [value root.name] / ] end end ] / ]] \uffff]

[split [string map {"_v" \uffff} [join [lrange [split [value root.name] / ] 7 7 ] / ]] \uffff]

[basename [file dirname [filename]]]_[lrange [split [file tail [filename]] "_"] 0 end-1]


Getting a knob's value of a specific node:
[value Read1.first]

Getting a knob's value of current node:
[value this.size]

Setting a knob's value of a specific node:
[knob Read1.first 10]

First frame of current read/write:
[value this.first_frame]

Setting a general tcl variable :
[set variablename value]
for example (tsize is the variable name):
[set tsize 15]

Using that variable later (notice the "$") for setting a knob value:
[knob this.size $tsize]

Name of the input node:
[value this.input.name]

Expressions in a group going outside (to parentgroup or root). This example gives the name of the node before the group:
[value this.parent.input.name]


String substitute and compare:

Replace string in current node file knob with regex (string "proj" to "projects" in all occurences):
[regsub -all "proj" [value [node this].file] "projects"]

String map (replace multiple stringpairs):
[string map {"aa" "xx" "bb" "yy"} "aaffffaabb" ] this returns: xxffffxxyy

Compare values:
[string equal [value Text1.message] "bla"]

Regexp matching:
[regexp -inline "_v\[0-9]{3}" [value Read2.file]]


Path manipulations:

Filepath without extension:
[file rootname [value [topnode].file]]


Filename only:
[basename [value [topnode].file ]]


Filename only without extension:
[basename[file rootname [value [topnode].file]]]


This one splits the uppermost node's (probably a readnode) filepath by slashes and then joins together until a certain point, giving a directory few levels upper than the currrent path). "File split" does the splitting, making a list of directory names, "lrange ... 0 7 "selects a range from the list, from the beginning to the 7. item, and "join ... / " joins by forward slashes (which I use always in paths):

[join [lrange [file split [value [topnode].file]] 0 7] /]


This one can be used in a writenode fileknob to quickly convert the topmost readnode's path to another format(tga). Similar to the previous, but splits path by "." (different than previous file split), and gets the range from the beginning to 2 before the end, this way cutting off the extension and the counter (framecounter must have preceeded by a "." ) :

[join [lrange [split [value [topnode].file] .] 0 end-2] .].%04d.tga
(I use similar to make the comps writenode have the output path automatically getting from path of the nukescene )

Other useful:

Get the value the channel of a node, at a specific pixelcoordinates (e.g.: 10,10):
[sample [node input] red 10 10]

Setting a variable, without returning that (useful in a textnode):
[set seq [value Read1.file]; return]


Example of "IF" in an expression:
[if {condition} {expr1} else {expr2}]
for example:
[if {[value Switch1.which]==1} {return "aaa"} {return "bbb"}]

______________________________________________________________
#MATH FUNCTIONS
#TCL

#RETURNS THE ABSOLUTE VALUE OF THE FLOATING-POINT NUMBER X.
abs (x)

#ROUND X UP TO THE NEAREST INTEGER.
ceil (x)

#ROUND X DOWN TO THE NEAREST INTEGER.
floor (x)

#ROUND X TO THE NEAREST INTEGER NOT LARGER IN ABSOLUTE VALUE
int (x)

#ROUND X TO THE NEAREST INTEGER
rint (x)

#RETURN X CLAMPED TO [0.0 ... 1.0].
clamp (x)

#RETURNS THE COSINE OF X.
cos(x)

#RETURNS THE SINE OF X.
sin (x)

#RETURNS A POINT ON THE LINE F(X) WHERE F(0)==A AND F(1)==B. MATCHES THE LERP FUNCTION IN OTHER SHADING LANGUAGES.
lerp (a, b, x)

#RETURNS THE Y VALUE OF THE ANIMATION CURVE AT THE GIVEN FRAME
curve (frame)
rotate(frame)

#RETURNS THE CURRENT FRAME
frame

#CONVERT THE ANGLE X FROM RADIANS INTO DEGREES
degrees (x)

#CONVERT THE ANGLE X FROM DEGREES INTO RADIANS
radians (x)

#RETURN THE GREATEST OF ALL VALUES
max (x, y, ... )

#RETURN THE SMALLEST OF ALL VALUES
min (x, y, ... )

#RETURN THE VALUE FOR PI (3.141592654...)
pi

#RETURNS THE VALUE OF X RAISED TO THE POWER OF Y.
pow (x, y)

#RETURNS THE NON-NEGATIVE SQUARE ROOT OF X.
sqrt (x)

#EVALUATES THE Y VALUE FOR AN ANIMATION AT THE GIVEN FRAME
value (frame)