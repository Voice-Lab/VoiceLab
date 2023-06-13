
#Asks user for the directory of files to be worked on

directory$ = "/home/david/Dropbox/voicelab-poetry/voicelab/tests/assets/audio/"

#Sets up Data File - erases existing file with same name
filedelete 'directory$''name$'max_formant.csv
header_row$ = "Filename" + tab$ + "max_formant" + newline$
header_row$ > 'directory$'max_formant.csv


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
     nowarn To Pitch (ac): 0, 50, 15, "yes", 0.03, 0.45, 0.01, 0.35, 0.14, 600
     broad = Get mean... 0 0 Hertz
    if (170 <= broad) and (broad <= 300)
        max_formant = 5500
    elif broad < 170
        max_formant = 5000
    else
        max_formant = 5500
    endif

  fileappend "'directory$'max_formant.csv" 'current_token$' 'tab$' 'max_formant' 'newline$'
 
endfor
select all
minus Strings list
Remove

