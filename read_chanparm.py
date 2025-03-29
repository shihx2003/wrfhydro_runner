import numpy as np; np.random.seed(42)
import matplotlib.pyplot as plt
import sys

print(len(sys.argv))
print("first param:", sys.argv[1])

kparam=float(sys.argv[1])

f=open("./CHANPARM.TBL.temp")
w=open("./CHANPARM.TBL", 'w', encoding='utf-8')

line = f.readline()
w.write(line)
line = f.readline()
w.write(line)
line = f.readline()
w.write(line)

for num in range(1,11):
  print(num)
  line = f.readline()
  linestr=line.split(',')

  strl=[0,0,0,0,0]

  strl[0]=int(linestr[0])
  strl[1]=float(linestr[1])
  strl[2]=float(linestr[2])
  strl[3]=float(linestr[3])
  strl[4]=float(linestr[4])*kparam

  data='' + str(strl[0]) + ',' + str('{:8.2f}'.format(strl[1])) + ',' + str('{:8.2f}'.format(strl[2])) + ',' + str('{:8.2f}'.format(strl[3])) + ',' + str('{:8.3f}'.format(strl[4])) 
  w.write(data)
  w.write("\n")

  print(linestr)
  print(strl)
f.close()
w.close()
