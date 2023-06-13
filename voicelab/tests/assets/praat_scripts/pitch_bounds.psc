
#Asks user for the directory of files to be worked on

directory$ = "/home/david/Dropbox/voicelab-poetry/voicelab/tests/assets/audio/"

#Sets up Data File - erases existing file with same name
filedelete 'directory$''name$'pitch_bounds.csv
header_row$ = "Filename" + tab$ + "floor" + tab$ + "ceiling"+ newline$
header_row$ > 'directory$'pitch_bounds.csv


#Sets up array of files to run batch process on
Create Strings as file list...  list 'directory$'*.wav
  number_files = Get number of strings
  for j from 1 to number_files
     select Strings list
     current_token$ = Get string... 'j'
     name$ = current_token$ - ".wav"
     Read from file... 'directory$''current_token$'


#This part measures pitch with broad parameters
  select Sound 'name$'
     nowarn To Pitch (ac): 0, 50, 15, "yes", 0.03, 0.45, 0.01, 0.35, 0.14, 500
     broad = Get mean... 0 0 Hertz
     if broad > 170
          floor = 100
          ceiling = 500
     elif broad < 170
         floor = 50
         ceiling = 300
     #else
     #    floor = 50
     #    ceiling = 500
    endif

  fileappend "'directory$'pitch_bounds.csv" 'current_token$' 'tab$' 'floor' 'tab$' 'ceiling' 'newline$'
 
endfor
select all
minus Strings list
Remove

