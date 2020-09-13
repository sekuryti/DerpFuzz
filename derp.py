#!/usr/bin/env python3
import glob, subprocess, random, time, threading, os, hashlib

def fuzz(thr_id, inp):
   assert isinstance(thr_id, int)
   assert isinstance(inp, bytearray)
   tmpfn = f"tmpinput(thr_id)"
   crashes = 0
   with open(tmpfn, "wb") as fd:
      fd.write(inp)
   sp = subprocess.Popen(["objdump", "-f", tmpfn], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
   ret = sp.wait()
   if ret < 0:
         print(f"Exited with {ret}")
         if ret == -11:
               dahash = hashlib.sha256(inp).hexdigest()
               open(os.path.join("crashes", f"crash_{dahash:64}"), "wb").write(inp)
               crashes += 1
               print("SEGFAULT")

corpus_filenames = glob.glob("corpus/*")
corpus = set()
for filename in corpus_filenames:
   corpus.add(open(filename, "rb").read())
corpus = list(map(bytearray, corpus))
start = time.time()
cases = 0

def worker(thr_id):
   global start, corpus, cases

   while True:
      try:
         inp = bytearray(random.choice(corpus))
         for _ in range(random.randint(1, 8)):
            inp[random.randint(0, len(inp))] = random.randint(0, 255)
         fuzz(thr_id, inp)
         cases += 1
         elapsed = time.time() - start
         fcps = float(cases) / elapsed

         print(f"{elapsed:10.4f} cases {cases:10} | fcps {fcps:10.4f}")
      except: 
         pass      

for thr_id in range(60):
   threading.Thread(target=worker, args=[thr_id]).start()

while threading.active_count() > 0:
   time.sleep(0.3)
