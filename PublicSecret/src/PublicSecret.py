"""
What is this app?
This is a text editor cum stegnography tool that can be used to hide your secret messages inside punctuation marks in a paragraph and store it in public discussion forums secretly.
"""
from tkinter import *
import re

table={"E":",.","T":",,","A":",?","I":",!","N":",;","O":",-","S":".,","H":"..","R":".?","D":".!","L":".;","U":".-","C":"?,","M":"?.","F":"??","W":"?!","Y":"?;","G":"?-","P":"!,","B":"!.","V":"!?","K":"!!","Q":"!;","J":"!-","X":";,","Z":";.","0":";?","1":";!","2":";;","3":";-","4":"-,","5":"-.","6":"-?","7":"-!","8":"-;","9":"--"}
supported_chars=["A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z","1","2","3","4","5","6","7","8","9","0"]
cprbkup=""
def encode(a,b,c): #trace function will call this with default arguments, hence a,b,c are placeho
    global cprbkup,table
    new=""
    old=msg.get().upper()
    for char in old:
        if char in supported_chars:
            new+=table[char]
    cpr.set(new[:10]+" ("+str(len(new))+")")
    cprbkup=new

def punct_highlight(fulltext):
    p=re.compile("[,.;!?:/-](?!  )(?:(?<!  [,.;!?:/-])|(?<=[,.;!?:/-]  [,.;!?:/-]))")
    count=1
    stegno.tag_remove("punct","1.0",END)
    stegno.tag_remove("spunct","1.0",END)
    for line in fulltext.split('\n'):
        iter=p.finditer(line)
        for m in iter:
            if m[0] in [':','/']:
                stegno.tag_add("spunct",str(count)+"."+str(m.span()[0]),str(count)+"."+str(m.span()[1]))
            else:
                stegno.tag_add("punct",str(count)+"."+str(m.span()[0]),str(count)+"."+str(m.span()[1]))
        count+=1

def scope_highlight(fulltext,reg,style):
    p=re.compile(reg,flags=re.DOTALL)
    stegno.tag_remove(style,"1.0",END)
    iter=p.finditer(fulltext)
    
    scoped=False
    for m in iter:
        #START
        #before precision
        first=fulltext.count("\n",0,m.span()[0])+1
        #after precision
        second=m.span()[0]-len('\n'.join(fulltext.split("\n")[0:first-1]))
        if first!=1: #If the character is not in first line, add 1 to count the newline at the end. because join will not add newline at the end.
            second-=1
        start=str(first)+"."+str(second)
        
        #STOP
        #before precision
        first=fulltext.count("\n",0,m.span()[1])+1
        #after precision
        second=m.span()[1]-len('\n'.join(fulltext.split("\n")[0:first-1]))
        if first!=1: #If the character is not in first line, add 1 to count the newline at the end. because join will not add newline at the end.
            second-=1
        stop=str(first)+"."+str(second)

        #if "punct" in stegno.tag_names(start) and "punct" in stegno.tag_names(stop.split(".")[0]+"."+str(int(stop.split(".")[1])-1)):
        stegno.tag_add(style,start,stop)
        scoped=True
        if style=="nonscope": #We have to remove punct highlights inside nonscoped text
            stegno.tag_remove("punct",start,stop)
            stegno.tag_remove("spunct",start.split(".")[0]+"."+str(int(start.split(".")[1])+1),stop.split(".")[0]+"."+str(int(stop.split(".")[1])-1))
        if style=="scope":
            #below calls should be in below order not to highlight puncts again.
            punct_highlight(re.sub(r"[^\n]",'~',fulltext[:m.span()[0]])+fulltext[m.span()[0]:m.span()[1]]+re.sub(r"[^\n]",'~',fulltext[m.span()[1]:]))
            stegno.tag_remove("spunct",start.split(".")[0]+"."+str(int(start.split(".")[1])+1),stop.split(".")[0]+"."+str(int(stop.split(".")[1])-1))
            scope_highlight(re.sub(r"[^\n]",'~',fulltext[:m.span()[0]])+fulltext[m.span()[0]:m.span()[1]]+re.sub(r"[^\n]",'~',fulltext[m.span()[1]:]),"/(?!  )(?:(?<!  /)|(?<=[,.;!?:/-]  /))[^/:]*?:(?!  )(?:(?<!  :)|(?<=[,.;!?:/-]  :))","nonscope")

    if not scoped and style=="scope": #Means, there is no scope mentioned, so we have to take all text as scope
        stegno.tag_add(style,"1.0",END)
        #below calls should be in below order not to highlight puncts again.
        punct_highlight(fulltext)
        scope_highlight(fulltext,"/(?!  )(?:(?<!  /)|(?<=[,.;!?:/-]  /))[^/:]*?:(?!  )(?:(?<!  :)|(?<=[,.;!?:/-]  :))","nonscope")

def changecpr(event):
    global cprbkup,cipher
    fulltext=stegno.get("1.0",END)
    
    #First get all valid puncts from the texts, including control puncts [:,/]
    cover="".join(re.findall("[,.;!?:/-](?!  )(?:(?<!  [,.;!?:/-])|(?<=[,.;!?:/-]  [,.;!?:/-]))",fulltext))
    #Then extract only puncts that are in scope
    start=re.sub("/.*?:",'',''.join([''.join(a) for a in re.findall("(?:.*?:(.*)/.*)|(.*)",cover)]))
    #Remove all excess control puncts
    start=start.replace('/','').replace(':','')
    
    if cprbkup.startswith(start):
        cpr.set(cprbkup[len(start):][:10]+" ("+str(len(cprbkup[len(start):]))+")")
        cipher.config(fg="black")
    else:
        cipher.config(fg="red")
    
    stegno.tag_config('punct', background='yellow')
    stegno.tag_config('spunct', background='pink') #scope punt, only for : and /
    stegno.tag_config('scope', foreground='blue')
    stegno.tag_config('nonscope', foreground='black')
    
    scope_highlight(fulltext,":(?!  )(?:(?<!  :)|(?<=[,.;!?:/-]  :)).*/(?!  )(?:(?<!  /)|(?<=[,.;!?:/-]  /))","scope")
    

def decode():
    global stegno,table,message
    inv_table={v: k for k, v in table.items()}
    
    #First read all the valid puncts from the text, including control puncts
    cover="".join(re.findall("[,.;!?:/-](?!  )(?:(?<!  [,.;!?:/-])|(?<=[,.;!?:/-]  [,.;!?:/-]))",stegno.get("1.0",END)))
    #Then extract only relevent puncts that are in scope
    new=re.sub("/.*?:",'',''.join([''.join(a) for a in re.findall("(?:.*?:(.*)/.*)|(.*)",cover)]))
    #Remove all excess control puncts
    new=new.replace('/','').replace(':','')
    
    cpr.set(new[:10]+" ("+str(len(new))+")")
    cipher.config(fg="black")
    old=""
    for i in range(0,len(new),2):
        old+=inv_table[new[i:i+2]]
    message.insert(0,old)

root = Tk()

cpr=StringVar()
cipher=Label(root, text=" ",textvariable=cpr,font=(None,15))
cipher.grid(row=1,column=0,sticky=W)

msg=StringVar()
msg.trace("w",encode)
message = Entry(root,textvariable=msg)
message.insert(0,"")
message.grid(row=0,column=0,columnspan=2,sticky=EW)

stegno=Text(root)
stegno.grid(row=2,column=0,columnspan=2)
stegno.bind("<KeyRelease>", changecpr)

dehide=Button(root,text="^",command=decode)
dehide.grid(row=1,column=1,sticky=E)


root.mainloop()