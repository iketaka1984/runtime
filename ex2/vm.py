import re
import sys
import time
import random
import tkinter as tk
from multiprocessing import Process, Value, Array, Lock, Manager, current_process, Semaphore

pre=0
codes=[]
com=[]
opr=[]
parcom1=[]
paropr1=[]
parcom2=[]
paropr2=[]
stack=[]
rstack=[]
temp=[]
ldata=[]
rdata=[]
top=-1
count_pc=0
parflag=0
args=sys.argv

def push(a,stack,top):
    stack.append(a)
    #print("push "+str(a)+" at "+str(top)+"")
    #print("push "+str(stack[top])+" in "+str(top)+"")
    #print("stack",end=':')
    #for i in range(0,len(stack),1):
    #    print(str(stack[i]),end=',')
    return top+1

def pop1(stack,top):
    t=stack[top-1]
    #print("pop "+str(t)+"at "+str(top-1)+"")
    stack.pop()
    return (t,top-1)

def executedcommand(mlock,stack,rstack,lstack,com,opr,pc,pre,top,rtop,ltop,address,value,parpath):
    if com==1:#push
        top=push(opr,stack,top)
        #print(stack)
        pre=pc
        return (pc+1,pre,stack,top,rtop)
    elif com==2:#load
        value.acquire()
        c=value[opr]
        value.release()
        top=push(c,stack,top)
        #print(stack)
        pre=pc
        return (pc+1,pre,stack,top,rtop)
    elif com==3:#store
        value.acquire()
        rstack[rtop.value]=(value[opr])
        rstack[rtop.value+1]=(parpath)
        #print("rtop "+str(rtop.value)+"")
        rtop.value=rtop.value+2
        (stack[opr],top)=pop1(stack,top)
        value[opr]=stack[opr]
        value.release()
        #print(stack)
        #if bytes[pc+2]==3:
        #    print("R = "+str(stack[3])+"")
        pre=pc
        return (pc+1,pre,stack,top,rtop)
    elif com==4:#jpc
        (c,top)=pop1(stack,top)
        if c==1:
            pre=pc
            pc=opr-2
        return (pc+1,pre,stack,top,rtop)
    elif com==5:#jmp
        pre=pc
        pc=opr-2
        return (pc+1,pre,stack,top,rtop)
    elif com==6:#op
        if (opr)==0:
            (c,top)=pop1(stack,top)
            (d,top)=pop1(stack,top)
            top=push(c+d,stack,top)
        elif (opr)==1:
            (c,top)=pop1(stack,top)
            (d,top)=pop1(stack,top)
            top=push(c*d,stack,top)
        elif opr==2:
            (c,top)=pop1(stack,top)
            (d,top)=pop1(stack,top)
            top=push(d-c,stack,top)
        elif opr==3:
            (c,top)=pop1(stack,top)
            (d,top)=pop1(stack,top)
            if d>c:
                top=push(1,stack,top)
            else:
                top=push(0,stack,top)
        elif opr==4:
            (c,top)=pop1(stack,top)
            #print(c)
            (d,top)=pop1(stack,top)
            #print(d)
            if d==c:
                top=push(1,stack,top)
            else:
                top=push(0,stack,top)
        pre=pc
        return (pc+1,pre,stack,top,rtop)
    elif com==7:#label
        if args[2]=='f':
            lstack[ltop.value]=(pre)
            lstack[ltop.value+1]=parpath
            ltop.value = ltop.value+2
        pre=pc
        return (pc+1,pre,stack,top,rtop)
    elif com==8:#rjmp
        pre=pc
        ltop.value=ltop.value-1
        pc=int(lstack[ltop.value])
        pc=pc-2
        ltop.value=ltop.value-1
        #mlock.release()
        return (pc+1,pre,stack,top,rtop)
    elif com==9:#restore
        rtop.value=rtop.value-1
        value[opr]=int(rstack[rtop.value])
        rtop.value=rtop.value-1
        #print(stack)
        pre=pc
        return (pc+1,pre,stack,top,rtop)
    elif com==0:#nop
        pre=pc
        return (pc+1,pre,stack,top,rtop)
    elif com==10:#par
        pre=pc
        return (pc+1,pre,stack,top,rtop)

#コードの実行
def execution(mode,lock,mlock,command,opr,start,end,stack,address,value,tablecount,rstack,lstack,rtop,ltop,endflag,parpath):
    pc=start
    pre=pc
    top=len(stack)
    if args[2]=='f':
        while pc<end:
            if parpath!=0:
               lock.acquire()
            #if you want to measure time,comment out
            if args[3]!='q':
                if command[pc]==1:
                    command1='ipush'
                elif command[pc]==2:
                    command1=' load'
                elif command[pc]==3:
                    command1='store'
                elif command[pc]==4:
                    command1='  jpc'
                elif command[pc]==5:
                    command1='  jmp'
                elif command[pc]==6:
                    command1='   op'
                elif command[pc]==7:
                    command1='label'
                elif command[pc]==10:
                    command1='  par'
                print("~~~~~~~~Process"+str(parpath)+" execute~~~~~~~~")
                print("pc = "+str(pc+1)+"   command = "+command1+"   operand = "+str(opr[pc])+"")
            (pc,pre,stack,top,rtop)=executedcommand(mlock,stack,rstack,lstack,command[pc],opr[pc],pc,pre,top,rtop,ltop,address,value,parpath)
            if args[3]!='q':
                print("executing stack:       "+str(stack[:])+"")
                print("shared variable stack: "+str(value[0:tablecount])+"")
            if parpath!=0:
                if mode=='2':
                    lock.acquire(False)
                    mlock.release()
                elif mode=='1':
                    lock.release()
        endflag.value=1
    elif args[2]=='b':
        #print("parflag="+str(parpath)+"")
        while pc<end:
            if parpath!=0:
                lock.acquire()
            #if you want to measure time, comment out
            if args[3]!='q':
                if command[pc]==0:
                    command1='    nop'
                elif command[pc]==7:
                    command1='  label'
                elif command[pc]==8:
                    command1='   rjmp'
                elif command[pc]==9:
                    command1='restore'
                elif command[pc]==10:
                    command1='    par'
                print("~~~~~~~~Process"+str(parpath)+" execute~~~~~~~~")
                print("pc = "+str(pc+1)+"   command = "+command1+"   operand = "+str(opr[pc])+"")
            (pc,pre,stack,top,rtop)=executedcommand(mlock,stack,rstack,lstack,command[pc],opr[pc],pc,pre,top,rtop,ltop,address,value,parpath)
            if args[3]!='q':
                print("shared variable stack: "+str(value[0:tablecount])+"")
            if parpath!=0:
                lock.acquire(False)
                mlock.release()
        endflag.value=1
    return stack        

#実行コード読み取り
def coderead(start,end):
    global codes
    global com
    global opr
    global count_pc
    global parflag
    f=open(args[1],mode='r')
    codes=f.read()
    f.close()
    for i in range(0,len(codes),9):
        t1=codes[i:i+2]
        s1=re.search(r'\d+',t1)
        t2=codes[i+2:i+8]
        s2=re.search(r'\d+',t2)
        #if ((int)(s1.group())!=10 and parflag==0):
        com.append((int)(s1.group()))
        opr.append((int)(s2.group()))
        if ((int)(s1.group())==10 and (int)(s2.group())==0):
            start.append(count_pc)
        elif ((int)(s1.group())==10 and (int)(s2.group())==1):
            end.append(count_pc)
            parflag=parflag+1
        #elif ((int)(s1.group())==10 and parflag==2 and (int)(s2.group())==0):
        #   start2=count_pc
        #elif ((int)(s1.group())==10 and parflag==2 and (int)(s2.group())==1):
        #    end2=count_pc
        #elif ((int)(s1.group())==10 and (int)(s2.group())==0 and parflag==0):
        #    parflag=1
        #    parcom1.append(10)
        #    paropr1.append(0)
        #elif ((int)(s1.group())==10 and (int)(s2.group())==1 and parflag==1):
        #    parflag=2
        #    parcom1.append(10)
        #    paropr1.append(1)
        #elif ((int)(s1.group())==10 and (int)(s2.group())==0 and parflag==2):
        #    parcom2.append(10)
        #    paropr2.append(0)
        #elif ((int)(s1.group())==10 and (int)(s2.group())==1 and parflag==2):
        #    parflag=0
        #    parcom2.append(10)
        #    paropr2.append(1)
        #elif ((int)(s1.group())!=10 and parflag==1):
        #    parcom1.append((int)(s1.group()))
        #    paropr1.append((int)(s2.group()))
        #elif ((int)(s1.group())!=10 and parflag==2):
        #    parcom2.append((int)(s1.group()))
        #    paropr2.append((int)(s2.group()))
        #print(com[count_pc],end=',')
        #print(opr[count_pc],end='\n')
        count_pc=count_pc+1
    #print(com)
    #print(opr)
    return (start,end)
    

#backward前処理
def backward():
    global ldata
    global rdata
    global stack
    if args[2]=='b':
        path4='lstack.txt'
        path5='rstack.txt'
        path7='stack.txt'
        f4=open(path4,mode='r')
        f5=open(path5,mode='r')
        f7=open(path7,mode='r')
        temp=f4.read()
        ldata=re.findall(r'[-]?\d+',temp)
        #print(ldata)
        temp=f5.read()
        rdata=re.findall(r'[-]?\d+',temp)
        #print(rdata)
        temp=f7.read()
        stack=re.findall(r'[-]?\d+',temp)
        #print(stack)
        f4.close()
        f5.close()
        f7.close()

#スタックとinvertedcodeの出力
def forward(ltop,rtop):
    if args[2]=='f':
        path2='inv_code.txt'
        f2=open(path2,mode='w')
        for i in range(0,count_pc,1):
            if com[count_pc-i-1]==7:
                f2.write(" 8     0\n")
            elif com[count_pc-i-1]==3:
                f2.write(" 9 "+str(opr[count_pc-i-1]).rjust(5)+"\n")
            elif com[count_pc-i-1]==4:
                f2.write(" 7     0\n")
            elif com[count_pc-i-1]==5:
                f2.write(" 7     0\n")
            elif com[count_pc-i-1]==10:
                f2.write("10 "+str(opr[count_pc-i-1]).rjust(5)+"\n")
            else:
                f2.write(" 0     0\n")
        f2.close()
        path='lstack.txt'
        f=open(path,'w')
        for i in range(0,ltop,2):
            f.write(""+str(count_pc-lstack[i])+" "+str(lstack[i+1])+" ")
        f.close()

        path3='rstack.txt'
        f3=open(path3,'w')
        for i in range(0,rtop,1):
            f3.write(""+str(rstack[i])+" ")
        f3.close()

        path6='stack.txt'
        f6=open(path6,'w')
        for i in range(0,len(value),1):
            f6.write(""+str(value[i])+" ")
        f6.close()

if __name__ == '__main__':
    start_time = time.time()
    #start1=0
    #end1=0
    #start2=0
    #end2=0
    start=[]
    end=[]
    tabledata=[]
    tablecount=0
    address = Array('i',10)
    value = Array('i',10)
    rstack = Array('i',100000)
    lstack = Array('i',100000)
    rtop = Value('i',0)
    ltop = Value('i',0)
    endflag={}
    endflag0=Value('i',0)
    lock={}
    
    mlock = Lock()
    lockfree  = Lock()
    a='1'
    path='table.txt'
    f=open(path,mode='r')
    tabledata=f.read()
    f.close()
    k=0
    for i in range(0,len(tabledata),20):
        t=tabledata[i+11:i+13]
        s=re.search(r'\d+',t)
        #print(s.group())
        address[k]=((int)(s.group()))
        t2=tabledata[i+13:i+19]
        s2=re.search(r'\d+',t2)
        #print(s2.group())
        value[k]=((int)(s2.group()))
        k=k+1
        tablecount=tablecount+1

    backward()

    if args[2]=='f':
        (start,end)=coderead(start,end)
        for i in range(0,parflag,1):
            endflag[i] = Value('i',0)
            #print(endflag[i].value)
            lock[i] = Lock()
        #print(start)
        #print(end)
        if parflag!=0:
            if args[3]=='q':
                mode='1'
            else:
                mode=input('mode   1:auto 2:select >> ')
            stack=execution(mode,lockfree,lockfree,com,opr,0,start[0],stack,address,value,tablecount,rstack,lstack,rtop,ltop,endflag0,0)
            #monitor=Process(target=monitor,args=(lock1,lock2,mlock))
            if mode=='2':
                for i in range(0,parflag,1):
                    lock[i].acquire()
                process={}
                for i in range(0,parflag,1):        
                    process[i]=Process(target=execution,args=(mode,lock[i],mlock,com,opr,start[i],end[i],stack,address,value,tablecount,rstack,lstack,rtop,ltop,endflag[i],i+1))
            #process2=Process(target=execution,args=(mode,lock2,mlock,com,opr,start,end,stack,address,value,rstack,lstack,rtop,ltop,endflag2,2))
            if mode=='1':
                process={}
                for i in range(0,parflag,1):        
                    process[i]=Process(target=execution,args=(mode,lock[0],mlock,com,opr,start[i],end[i],stack,address,value,tablecount,rstack,lstack,rtop,ltop,endflag[i],i+1))
            for i in range(0,parflag,1):
                    process[i].start()
            if mode=='2':
                while a!='esc':
                    a=input('>> ')
                    mlock.acquire(False)
                    ifflag=0
                    for i in range(0,parflag,1):
                        if a==str(i+1) and endflag[i].value!=1 and ifflag==0:
                            ifflag=1
                            lock[i].release()
                        #elif a=='2' and endflag2.value!=1:
                        #    lock2.release()
            for i in range(0,parflag,1):
                process[i].join()
        elif parflag==0:
            mode='1'
            execution(mode,lockfree,mlock,com,opr,0,len(com),stack,address,value,tablecount,rstack,lstack,rtop,ltop,endflag0,0)
        #print(value[0:tablecount])
        #print(lstack[0:ltop.value])
        #print(rstack[0:rtop.value])
        forward(ltop.value,rtop.value)

    elif args[2]=='b':
        (start,end)=coderead(start,end)
        for i in range(0,parflag,1):
            endflag[i] = Value('i',0)
            #print(endflag[i].value)
            lock[i] = Lock()
        #print(""+str(start1)+" "+str(end1)+" "+str(start2)+" "+str(end2)+"")
        #print(ldata)
        #print(rdata)
        for i in range(0,len(ldata),1):
            lstack[i]=int(ldata[i])
            ltop.value=ltop.value+1
        for i in range(0,len(rdata),1):
            rstack[i]=int(rdata[i])
            rtop.value=rtop.value+1
        for i in range(0,len(stack),1):
            value[i]=int(stack[i])
        ltop.value=ltop.value-1
        #print(value[:])
        rtop.value=rtop.value-1
        mode='0'
        #print(str(parflag))
        if parflag!=0:
            #______measure time mode_________ 
            if args[3]=='q':
                mode='1'
            else:
                mode=input('mode   1:auto  2:select >> ')
            for i in range(0,parflag,1):
                lock[i].acquire()
            #monitor=Process(target=monitor,args=(lock1,lock2,mlock))
            process={}
            for i in range(0,parflag,1):
                process[i]=Process(target=execution,args=(mode,lock[parflag-i-1],mlock,com,opr,end[i],start[i],stack,address,value,tablecount,rstack,lstack,rtop,ltop,endflag[i],parflag-i))
            #process2=Process(target=execution,args=(mode,lock2,mlock,com,opr,start2,end2,stack,address,value,rstack,lstack,rtop,ltop,endflag1,1))
            for i in range(0,parflag,1):
                process[i].start()
            a='2'
            if mode=='2':
                while a!='esc':
                    a=input('process '+str(lstack[ltop.value])+' ')
                    mlock.acquire(False)
                    for i in range(0,parflag,1):
                        if int(lstack[ltop.value])==i+1:
                            lock[i].release()
            elif mode=='1':
                while a!='esc':
                    mlock.acquire()
                    ifflag=0
                    endcount=0
                    for i in range(0,parflag,1):
                        if int(lstack[ltop.value])==i+1 and ifflag==0:
                            lock[i].release()
                            ifflag=1
                    for i in range(0,parflag,1):
                        if endflag[i].value==1:
                            endcount=endcount+1
                    if endcount==parflag:
                        a='esc'
            #monitor.start()
            #monitor.join()
            for i in range(0,parflag,1):
                process[i].join()
            execution(mode,lockfree,lockfree,com,opr,start[parflag-1]+1,count_pc,stack,address,value,tablecount,rstack,lstack,rtop,ltop,endflag0,0)
        elif parflag==0:
            execution(mode,lockfree,lockfree,com,opr,0,len(com),stack,address,value,tablecount,rstack,lstack,rtop,ltop,endflag0,0)

    elapsed_time = time.time()-start_time
    print("elapsed_time:{0}".format(elapsed_time) + "[sec]")