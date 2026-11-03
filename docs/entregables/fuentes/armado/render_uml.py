import sys, subprocess, os, json
sys.path.insert(0,'.')
import uml_data as U
fails=[]
for cu in U.EST:
    for kind,fn in (('est',U.est_text),('din',U.din_text)):
        base=f'uml/{cu}_{kind}'
        open(base+'.mmd','w').write(fn(cu))
        r=subprocess.run(['mmdc','-i',base+'.mmd','-o',base+'.png','-b','white','-s','2'],capture_output=True,text=True)
        if r.returncode or not os.path.exists(base+'.png'):
            fails.append((cu,kind,(r.stderr or r.stdout)[-300:]))
print('fails',len(fails))
for f in fails: print(f)
