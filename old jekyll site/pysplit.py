fo = open("list.txt", "r")
lines = fo.readlines()
outf = open("out.txt", "w")
for line in lines:
    l = line.replace("\n","")
    ls = l.split(",")
    pl = "first: " + ls[0] + " second: " + ls[1] + " third: " + ls[2]
    outf.write(pl)
outf.close()
